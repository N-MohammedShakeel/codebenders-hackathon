"""Gemini OCR and conservative document-expiry checks."""

from __future__ import annotations

import datetime
import json
import logging
import math
import os
import re
from typing import Any, Dict, Optional

if __package__.startswith("api."):
    from api.agent.gemini_config import GEMINI_GENERATIVE_MODEL
    from api.agent.gemini_errors import gemini_failure_message
else:
    from agent.gemini_config import GEMINI_GENERATIVE_MODEL
    from agent.gemini_errors import gemini_failure_message

logger = logging.getLogger(__name__)

_MODEL_NAME = GEMINI_GENERATIVE_MODEL
_CATEGORIES = {
    "identity",
    "income",
    "residence",
    "education",
    "caste",
    "land",
    "bank",
    "other",
}
_PROMPT = """Inspect this citizen-submitted document for OCR only.
Return ONLY strict JSON with exactly these keys:
- "documentCategory": one of identity, income, residence, education, caste, land, bank, other
- "documentType": short document type, or null
- "issueDate": printed issue date as YYYY-MM-DD, or null
- "expiryDate": printed expiry / valid-until date as YYYY-MM-DD, or null
- "annualIncomeINR": annual income explicitly printed as a number in INR, or null

Do not infer missing dates, validity periods, income, or authenticity.
Do not read, return, or transcribe Aadhaar numbers, phone numbers, bank account numbers,
or personal names. "documentType" must be a generic type label and must not contain a
person's name or document number. Use null when a value is unclear. The expected category is {category}."""

_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")
_DOCUMENT_TYPE_LABELS = {
    "income certificate": "Income Certificate",
    "caste certificate": "Caste Certificate",
    "community certificate": "Community Certificate",
    "residence certificate": "Residence Certificate",
    "domicile certificate": "Domicile Certificate",
    "bonafide certificate": "Bonafide Certificate",
    "degree certificate": "Degree Certificate",
    "marks card": "Marks Card",
    "land record": "Land Record",
    "farmer certificate": "Farmer Certificate",
    "bank passbook": "Bank Passbook",
    "bank statement": "Bank Statement",
    "identity document": "Identity Document",
}


class OCRServiceError(RuntimeError):
    """Raised when Gemini cannot return a usable OCR result."""


def _provider_error_message(exc: Exception) -> str:
    return gemini_failure_message(exc, "document OCR")


def _strip_fences(text: str) -> str:
    return re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", text.strip(), flags=re.IGNORECASE)


def _to_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        try:
            number = float(value.replace(",", "").strip())
        except ValueError:
            return None
    else:
        return None
    return number if math.isfinite(number) and number >= 0 else None


def _to_date(value: Any) -> Optional[datetime.date]:
    if not isinstance(value, str) or not _DATE_PATTERN.fullmatch(value.strip()):
        return None
    try:
        return datetime.date.fromisoformat(value.strip())
    except ValueError:
        return None


def _to_text(value: Any) -> Optional[str]:
    if isinstance(value, str):
        return _DOCUMENT_TYPE_LABELS.get(value.strip().lower())
    return None


def _call_vision_ai(file_bytes: bytes, mime_type: str, api_key: str, category: str) -> Dict[str, Any]:
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(_MODEL_NAME)
        response = model.generate_content([
            _PROMPT.format(category=category),
            {"mime_type": mime_type, "data": file_bytes},
        ])
        text = getattr(response, "text", None)
    except Exception as exc:
        logger.exception("Gemini document OCR request failed")
        logger.error(
            "Gemini document OCR provider error: type=%s status=%s",
            type(exc).__name__,
            getattr(getattr(exc, "code", None), "value", getattr(exc, "code", None)),
        )
        raise OCRServiceError(_provider_error_message(exc)) from exc

    if not isinstance(text, str):
        raise OCRServiceError("Gemini returned no readable document details.")
    try:
        data = json.loads(_strip_fences(text))
    except ValueError as exc:
        raise OCRServiceError("Gemini returned an unreadable OCR response.") from exc
    if not isinstance(data, dict):
        raise OCRServiceError("Gemini returned an invalid OCR response.")
    return data


def analyze_document_image(
    file_bytes: bytes,
    filename: str,
    mime_type: str,
    expected_category: str,
) -> Dict[str, Any]:
    """Extracts limited fields and checks only an explicitly printed expiry date."""
    if expected_category not in _CATEGORIES:
        raise ValueError(f"Unsupported document category: {expected_category}")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise OCRServiceError("Gemini OCR is not configured; set GEMINI_API_KEY.")

    raw = _call_vision_ai(file_bytes, mime_type, api_key, expected_category)
    extracted_category = raw.get("documentCategory")
    if extracted_category not in _CATEGORIES:
        extracted_category = "other"

    issue_date = _to_date(raw.get("issueDate"))
    expiry_date = _to_date(raw.get("expiryDate"))
    annual_income = _to_number(raw.get("annualIncomeINR"))
    document_type = _to_text(raw.get("documentType"))
    today = datetime.date.today()

    if extracted_category != expected_category:
        validity_status = "TYPE_MISMATCH"
        validity_detail = (
            f"Document appears to be '{document_type or extracted_category}', "
            f"not the expected {expected_category} document."
        )
    elif expiry_date is not None and expiry_date < today:
        validity_status = "EXPIRED"
        validity_detail = f"The printed expiry date {expiry_date.isoformat()} has passed."
    elif issue_date is not None and issue_date > today:
        validity_status = "REVIEW_REQUIRED"
        validity_detail = f"The printed issue date {issue_date.isoformat()} is in the future; validity needs review."
    elif expiry_date is not None:
        validity_status = "CURRENT"
        validity_detail = f"The printed expiry date is {expiry_date.isoformat()}."
    else:
        validity_status = "REVIEW_REQUIRED"
        validity_detail = "No printed expiry date was found; validity cannot be determined automatically."

    extracted = {
        "documentCategory": extracted_category,
        "documentType": document_type,
        "issueDate": issue_date.isoformat() if issue_date else None,
        "expiryDate": expiry_date.isoformat() if expiry_date else None,
        "annualIncomeINR": annual_income,
    }
    return {
        "fileName": "document",
        "extracted": extracted,
        "validity": {
            "status": validity_status,
            "detail": validity_detail,
        },
        "checks": {
            "documentCategory": {
                "status": "PASS" if extracted_category == expected_category else "FAIL",
                "detail": "Detected category matches the selected document type."
                if extracted_category == expected_category
                else validity_detail,
            },
            "expiryDate": {
                "status": "NOT_SHOWN" if expiry_date is None else (
                    "EXPIRED" if expiry_date < today else "CURRENT"
                ),
                "detail": validity_detail,
            },
            "annualIncomeINR": {
                "status": "EXTRACTED" if annual_income is not None else "NOT_SHOWN",
                "detail": "Annual income read from the document."
                if annual_income is not None
                else "No annual income was found on the document.",
            },
        },
        "issues": [validity_detail] if validity_status != "CURRENT" else [],
        "mode": "GEMINI_VISION",
        "note": (
            "OCR checks only the printed information. It does not authenticate the document or "
            "replace the issuing authority's validity rules."
        ),
    }
