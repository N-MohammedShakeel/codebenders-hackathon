"""Safe, actionable messages for Gemini provider failures."""

from typing import Optional


def _error_details(exc: Exception) -> str:
    parts = [str(exc)]
    current: Optional[BaseException] = exc
    while current is not None:
        for attribute in ("status_code", "code", "status"):
            value = getattr(current, attribute, None)
            if value is not None:
                parts.append(str(value))
                enum_value = getattr(value, "value", None)
                if enum_value is not None:
                    parts.append(str(enum_value))
        current = current.__cause__ or current.__context__
    return " ".join(parts).lower()


def gemini_failure_message(exc: Exception, purpose: str) -> str:
    """Translate common provider errors without exposing prompts or request data."""
    details = _error_details(exc)
    if "429" in details or "resource_exhausted" in details or "resource exhausted" in details or "quota" in details:
        return (
            f"Gemini {purpose} quota is exhausted or rate-limited. "
            "Check Gemini API quota/billing or retry after the quota resets."
        )
    if any(term in details for term in ("401", "403", "permission_denied", "permission denied", "api_key_invalid", "invalid api key")):
        return (
            f"Gemini {purpose} is not authorized. Check the GEMINI_API_KEY, "
            "its API restrictions, and Gemini model access in Vercel."
        )
    if "404" in details or "not_found" in details or "not found" in details:
        return f"The Gemini model for {purpose} was not found or is unavailable to this API key."
    if any(term in details for term in ("timeout", "timed out", "deadline_exceeded", "deadline exceeded")):
        return f"Gemini {purpose} timed out. Please try again."
    if any(term in details for term in ("500", "502", "503", "504", "internal", "unavailable")):
        return f"Gemini is temporarily unavailable for {purpose}. Please try again later."
    if purpose == "document OCR" and any(term in details for term in ("400", "invalid_argument", "unsupported")):
        return (
            "Gemini rejected this document format or image. Upload a clear JPG, PNG, WEBP, "
            "or PDF file and try again."
        )
    return f"Gemini {purpose} failed. Please try again; if it persists, check the Vercel function logs."
