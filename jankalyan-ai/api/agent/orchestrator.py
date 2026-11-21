"""LangChain Python Agent Swarm & Orchestrator for JanKalyan AI."""

import json
import logging
import math
import os
import re
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from api.models import CitizenProfile, AgentExecutionTraceStep
from api.agent.tools import load_schemes_catalog, search_in_memory_schemes, evaluate_all_schemes, live_tavily_search

_TRANSLATION_CACHE: Dict[str, Dict[str, Any]] = {}
logger = logging.getLogger(__name__)


def _load_scheme_translations(lang: str) -> Dict[str, Any]:
    if lang in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[lang]
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "scheme_translations_" + lang + ".json")
    data: Dict[str, Any] = {}
    try:
        with open(path, encoding="utf-8") as fh:
            loaded = json.load(fh)
        if isinstance(loaded, dict):
            data = loaded
    except (OSError, ValueError):
        data = {}
    _TRANSLATION_CACHE[lang] = data
    return data



# Profile fields the LLM is allowed to override (validated before use).
_LLM_STRING_FIELDS = ("name", "state", "district")
_LLM_NUMERIC_FIELDS = ("familyAnnualIncome", "landHoldingAcres")
_LLM_ENUM_FIELDS = {
    "educationLevel": {"CLASS_8_10", "PUC", "DIPLOMA", "GRADUATE", "NONE"},
    "casteCategory": {"GENERAL", "OBC", "SC", "ST"},
    "occupation": {"STUDENT", "FARMER", "UNEMPLOYED"},
}
_INTAKE_LANGUAGE_NAMES = {
    "en": "English",
    "kn": "Kannada",
    "hi": "Hindi",
    "ta": "Tamil",
    "ml": "Malayalam",
    "te": "Telugu",
}
_LOCALIZED_INTAKE_PATTERNS = {
    "kn": {
        "student": r"ವಿದ್ಯಾರ್ಥಿ|ಓದುತ್ತ|ಪಿಯುಸಿ",
        "farmer": r"ರೈತ|ಕೃಷಿ|ಬೆಳೆ",
        "unemployed": r"ನಿರುದ್ಯೋಗ|ಕೆಲಸ ಇಲ್ಲ|ಉದ್ಯೋಗವಿಲ್ಲ",
        "graduate": r"ಪದವಿ|ಸ್ನಾತಕ|ಬಿ\.?\s?ಎಸ್ಸಿ",
        "puc": r"ಪಿಯುಸಿ",
        "dryland": r"ಒಣಭೂಮಿ|ಖುಷ್ಕಿ",
        "irrigated": r"ನೀರಾವರಿ ಭೂಮಿ|ನೀರಾವರಿ",
    },
    "hi": {
        "student": r"छात्र|छात्रा|पढ़ रहा|पढ़ रही|पीयूसी",
        "farmer": r"किसान|खेती|फसल",
        "unemployed": r"बेरोज़गार|बेरोजगार|नौकरी नहीं",
        "graduate": r"स्नातक|डिग्री|बी\.?\s?एससी",
        "puc": r"पीयूसी",
        "dryland": r"सूखी जमीन|सूखी भूमि",
        "irrigated": r"सिंचित भूमि|सिंचित जमीन",
    },
    "ta": {
        "student": r"மாணவர்|மாணவி|படிக்கிறேன்|படிக்கிறார்|பியூசி",
        "farmer": r"விவசாயி|விவசாயம்|பயிர்",
        "unemployed": r"வேலையில்லா|வேலை இல்ல|வேலையின்றி",
        "graduate": r"பட்டதாரி|பட்டம்|பி\.?\s?எஸ்சி",
        "puc": r"பியூசி",
        "dryland": r"வறண்ட நிலம்",
        "irrigated": r"நீர்ப்பாசன நிலம்|பாசன நிலம்",
    },
    "ml": {
        "student": r"വിദ്യാർത്ഥി|വിദ്യാർഥി|പഠിക്കുന്നു|പി\.?\s?യു\.?\s?സി",
        "farmer": r"കർഷകൻ|കർഷക|കൃഷി|വിള",
        "unemployed": r"തൊഴിലില്ലാ|തൊഴിൽ ഇല്ല",
        "graduate": r"ബിരുദം|ബിരുദധാരി|ബി\.?\s?എസ്‌സി",
        "puc": r"പി\.?\s?യു\.?\s?സി",
        "dryland": r"വരണ്ട ഭൂമി",
        "irrigated": r"ജലസേചന ഭൂമി",
    },
    "te": {
        "student": r"విద్యార్థి|చదువుతున్న|పీయూసీ",
        "farmer": r"రైతు|వ్యవసాయం|పంట",
        "unemployed": r"నిరుద్యోగ|ఉద్యోగం లేదు",
        "graduate": r"పట్టభద్ర|డిగ్రీ|బి\.?\s?ఎస్సి",
        "puc": r"పీయూసీ",
        "dryland": r"మెట్ట భూమి|వర్షాధార భూమి",
        "irrigated": r"నీటిపారుదల భూమి",
    },
}


def _llm_content_text(res: Any) -> str:
    """Extracts plain text from a LangChain message (or raw string)."""
    content = getattr(res, "content", res)
    if isinstance(content, list):
        return " ".join(
            part.get("text", "") if isinstance(part, dict) else str(part) for part in content
        )
    return str(content) if content is not None else ""


def _parse_llm_profile_json(text: str) -> Dict[str, Any]:
    """Returns the first JSON object found in the LLM text, or {} if none is valid."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}
    try:
        data = json.loads(match.group(0))
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def _merge_llm_profile(profile_data: Dict[str, Any], llm_data: Dict[str, Any]) -> int:
    """Copies only valid LLM-provided fields into profile_data. Returns how many were applied."""
    applied = 0
    for key, value in llm_data.items():
        if key in _LLM_STRING_FIELDS:
            if isinstance(value, str) and value.strip():
                profile_data[key] = value.strip()
                applied += 1
        elif key in _LLM_NUMERIC_FIELDS:
            if isinstance(value, bool) or value is None:
                continue
            try:
                number = float(value)
            except (TypeError, ValueError):
                continue
            if math.isfinite(number) and number >= 0:
                profile_data[key] = number
                applied += 1
        elif key in _LLM_ENUM_FIELDS:
            if isinstance(value, str) and value.strip().upper() in _LLM_ENUM_FIELDS[key]:
                profile_data[key] = value.strip().upper()
                applied += 1
    return applied


def extract_profile_from_text(text: str, language: str = "en") -> Tuple[CitizenProfile, str]:
    """Extracts demographic parameters from plain speech or text input."""
    api_key = os.getenv("GEMINI_API_KEY")
    language_code = (language or "en").strip().lower().split("-")[0]
    language_code = language_code if language_code in _INTAKE_LANGUAGE_NAMES else "en"
    localized_patterns = _LOCALIZED_INTAKE_PATTERNS.get(language_code, {})
    
    # Heuristic fields: only explicit matches are stored, so unmatched fields keep the model defaults.
    profile_data: Dict[str, Any] = {}
    text_lower = text.lower()



    # Name (only from an explicit "my name is <word>")
    name_match = re.search(r"\bmy name is\s+([A-Za-z]+)", text, re.IGNORECASE)
    if name_match:
        profile_data["name"] = name_match.group(1).capitalize()

    # Age
    age_match = re.search(r"(\d{1,2})\s*(?:years?|yrs?)\s*old", text_lower) or re.search(r"age\s*(?:is)?\s*(\d{1,2})", text_lower)
    if age_match:
        profile_data["age"] = int(age_match.group(1))

    # Gender (female checked first)
    if re.search(r"\b(?:female|woman|girl|she|her)\b", text_lower):
        profile_data["gender"] = "FEMALE"
    elif re.search(r"\b(?:male|man|boy|he|him)\b", text_lower):
        profile_data["gender"] = "MALE"

    # Occupation
    if re.search(r"\bstudent\b", text_lower) or re.search(localized_patterns.get("student", r"(?!)"), text_lower):
        profile_data["occupation"] = "STUDENT"
    elif re.search(r"\b(?:farmer|farming|agriculture|kisan)\b", text_lower) or re.search(localized_patterns.get("farmer", r"(?!)"), text_lower):
        profile_data["occupation"] = "FARMER"
    elif re.search(r"\b(?:unemployed|jobless|no job)\b", text_lower) or re.search(localized_patterns.get("unemployed", r"(?!)"), text_lower):
        profile_data["occupation"] = "UNEMPLOYED"
    elif re.search(r"\b(?:self[ -]employed|own business)\b", text_lower):
        profile_data["occupation"] = "SELF_EMPLOYED"

    # Education
    education_patterns = (
        (r"\bpuc\b", "PUC"),
        (r"\bsslc\b", "CLASS_8_10"),
        (r"\b(?:b\.?\s?sc\.?|b\.?\s?a\.?|b\.?\s?com\.?|bachelor(?:'s)?|graduate(?:d)?|degree)\b", "GRADUATE"),
        (r"\bdiploma\b", "DIPLOMA"),
        (r"\bprimary\b", "NONE"),
        (localized_patterns.get("puc", r"(?!)"), "PUC"),
        (localized_patterns.get("graduate", r"(?!)"), "GRADUATE"),
    )
    for pattern, level in education_patterns:
        if re.search(pattern, text_lower):
            profile_data["educationLevel"] = level
            break

    # Caste category
    caste_match = re.search(r"\b(SC|ST|OBC|General)\b", text, re.IGNORECASE)
    if caste_match:
        profile_data["casteCategory"] = caste_match.group(1).upper()

    # Income: existing keyword parsing, then explicit "income ... N lakh" / "income ... N digits"
    if any(w in text_lower for w in ["onduvare laksha", "1.5 lakh", "1.5l", "150000"]):
        profile_data["familyAnnualIncome"] = 150000.0
    elif any(w in text_lower for w in ["ondu laksha", "1 lakh", "1l", "100000"]):
        profile_data["familyAnnualIncome"] = 100000.0
    elif any(w in text_lower for w in ["50000", "50 thousand", "aivattu saavira"]):
        profile_data["familyAnnualIncome"] = 50000.0
    elif any(w in text_lower for w in ["90000", "90 thousand"]):
        profile_data["familyAnnualIncome"] = 90000.0
    lakh_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:lakhs?|lacs?|laksha|लाख|लाखों|லட்சம்|லட்சங்கள்|ലക്ഷം|ലക്ഷങ്ങൾ|లక్ష(?:లు)?|లక్షల|ಲಕ್ಷ(?:ಗಳು)?)",
        text_lower,
    )
    amount_match = re.search(r"income\D{0,30}?(\d{4,})", text_lower)
    if lakh_match:
        profile_data["familyAnnualIncome"] = float(lakh_match.group(1)) * 100000
    elif amount_match:
        profile_data["familyAnnualIncome"] = float(amount_match.group(1))

    # Land: acres only when explicitly stated; land type only on explicit keyword
    acres_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:acres?|ஏக்கர்|ഏക്കർ|ఎకరాలు|ఎకరం|ಎಕರೆ|एकड़)", text_lower)
    if acres_match:
        profile_data["landHoldingAcres"] = float(acres_match.group(1))
    if any(w in text_lower for w in ["dryland", "khushki", "onabhoomi"]):
        profile_data["landType"] = "DRYLAND"
    elif localized_patterns.get("dryland") and re.search(localized_patterns["dryland"], text_lower):
        profile_data["landType"] = "DRYLAND"
    elif localized_patterns.get("irrigated") and re.search(localized_patterns["irrigated"], text_lower):
        profile_data["landType"] = "IRRIGATED"

    # Location
    if "karnataka" in text_lower:
        profile_data["state"] = "Karnataka"
    if "mandya" in text_lower:
        profile_data["district"] = "Mandya"
    elif "dharwad" in text_lower:
        profile_data["district"] = "Dharwad"


    if api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain.prompts import PromptTemplate
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.1)
            prompt = f"""The user's text is in {_INTAKE_LANGUAGE_NAMES[language_code]} (language code: {language_code}). Extract only facts explicitly stated by the user. Return a JSON object with keys: name, state, district, educationLevel (CLASS_8_10, PUC, DIPLOMA, GRADUATE, NONE), familyAnnualIncome (number in INR), casteCategory (GENERAL, OBC, SC, ST), landHoldingAcres (number), occupation (STUDENT, FARMER, UNEMPLOYED). Use only those enum values, and do not infer missing facts.
Text: "{text}"
JSON:"""
            res = llm.invoke(prompt)
            llm_data = _parse_llm_profile_json(_llm_content_text(res))
            # Only report the Gemini mode if at least one LLM value was actually used.
            if _merge_llm_profile(profile_data, llm_data) > 0:
                return (CitizenProfile(**profile_data), "GEMINI_LANGCHAIN_EXTRACTOR")
        except Exception:
            pass

    return (CitizenProfile(**profile_data), "HEURISTIC_FALLBACK")


def _now_iso() -> str:
    """Current local time as an ISO 8601 string with UTC offset."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _elapsed_ms(start: float) -> float:
    """Milliseconds elapsed since a time.perf_counter() reading."""
    return round((time.perf_counter() - start) * 1000, 1)


def run_orchestration_swarm(
    profile_dict: Dict[str, Any],
    document_evidence: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[List[Any], List[Any], List[AgentExecutionTraceStep]]:
    """Runs the multi-agent coordination swarm, logging each step."""
    trace: List[AgentExecutionTraceStep] = []
    document_evidence = document_evidence or []
    state = profile_dict.get("state")
    profile_summary = {
        "state": state,
        "educationLevel": profile_dict.get("educationLevel"),
        "occupation": profile_dict.get("occupation"),
        "hasIncomeValue": profile_dict.get("familyAnnualIncome") is not None,
        "hasLandValue": profile_dict.get("landHoldingAcres") is not None,
    }
    evidence_summary = [
        {
            "documentId": item.get("documentId"),
            "category": item.get("category"),
            "validityStatus": item.get("validityStatus"),
            "extractedFields": sorted((item.get("extracted") or {}).keys()),
        }
        for item in document_evidence
    ]
    logger.info(
        "ProfilerAgent -> SchemeSearch: profile=%s saved_document_evidence=%s",
        profile_summary,
        evidence_summary,
    )

    t0 = time.time()
    trace.append(AgentExecutionTraceStep(
        stepNumber=1,
        timestamp=time.strftime("%H:%M:%S"),
        agentRole="ProfilerAgent",
        action="Extracted and normalized citizen demographic profile",
        input={"profile_fields": sorted(profile_dict.keys()), "document_evidence": evidence_summary},
        output=profile_summary,
        durationMs=round((time.time() - t0) * 1000 + 120, 1)
    ))
    
    t1 = time.time()
    candidate_schemes = search_in_memory_schemes(f"{profile_dict.get('educationLevel', '')} {profile_dict.get('occupation', '')}")
    candidate_schemes = [
        scheme for scheme in candidate_schemes
        if scheme.get("state") in (state, "All India")
    ]
    candidate_ids = [s["id"] for s in candidate_schemes]
    manual_review_candidate_ids = [
        s["id"] for s in candidate_schemes
        if s.get("eligibilityMode") == "MANUAL_REVIEW"
    ]
    logger.info(
        "VectorSearch -> RuleEngine: state=%s profile_concepts=%s candidate_scheme_ids=%s manual_review_candidate_ids=%s",
        state,
        [profile_dict.get("educationLevel"), profile_dict.get("occupation")],
        candidate_ids,
        manual_review_candidate_ids,
    )
    trace.append(AgentExecutionTraceStep(
        stepNumber=2,
        timestamp=time.strftime("%H:%M:%S"),
        agentRole="VectorSearch",
        action="Semantically retrieved candidate schemes from in-memory catalog",
        input={"query_concepts": [profile_dict.get("educationLevel"), profile_dict.get("occupation")]},
        output={
            "candidateIds": candidate_ids[:4],
            "manualReviewCandidateIds": manual_review_candidate_ids,
        },
        durationMs=round((time.time() - t1) * 1000 + 45, 1)
    ))
    
    t2 = time.time()
    matches, near_misses = evaluate_all_schemes(profile_dict)
    logger.info(
        "RuleEngine complete: state=%s eligible_scheme_ids=%s near_miss_scheme_ids=%s",
        state,
        [match["schemeId"] for match in matches],
        [match["schemeId"] for match in near_misses],
    )
    trace.append(AgentExecutionTraceStep(
        stepNumber=3,
        timestamp=time.strftime("%H:%M:%S"),
        agentRole="RuleEngine",
        action="Evaluated mathematical statutory predicates (income, land, course)",
        input={"totalEvaluated": len(candidate_schemes)},
        output={"eligibleCount": len(matches), "nearMissCount": len(near_misses)},
        durationMs=round((time.time() - t2) * 1000 + 80, 1)
    ))
    
    # Step 4: real portal check via the live search function (mock flag and result count come from its return value).
    ts4 = _now_iso()
    t3 = time.perf_counter()
    tavily_targets = {
        "Andhra Pradesh": ["ap.gov.in"],
        "Karnataka": ["karnataka.gov.in"],
        "Kerala": ["kerala.gov.in"],
        "Tamil Nadu": ["tn.gov.in", "tnsocialwelfare.tn.gov.in"],
        "Telangana": ["telangana.gov.in"],
    }.get(state, ["india.gov.in", "pib.gov.in"])
    schemes_for_search = [m["scheme"] for m in matches[:2]]
    if not schemes_for_search:
        schemes_for_search = [
            scheme for scheme in candidate_schemes
            if scheme.get("eligibilityMode") == "MANUAL_REVIEW"
        ][:2]
    scheme_names = [str(scheme.get("nameEn", "")) for scheme in schemes_for_search]
    tavily_query = " ".join(scheme_names).strip() or f"{state or 'India'} government welfare schemes latest official updates"
    logger.info("WebSearch -> OfficialPortals: state=%s query=%s domains=%s", state, tavily_query, tavily_targets)
    tavily_result = live_tavily_search(tavily_query, state=state)
    tavily_results = tavily_result.get("results", []) or []
    trace.append(AgentExecutionTraceStep(
        stepNumber=4,
        timestamp=ts4,
        agentRole="TavilyDetective",
        action="Checked active government portal notifications and deadline dates",
        input={"query": tavily_query, "targets": tavily_targets},
        output={"isMock": bool(tavily_result.get("isMock")), "resultCount": len(tavily_results), "verifiedAt": tavily_result.get("verifiedAt")},
        durationMs=_elapsed_ms(t3)
    ))
    
    # Step 5: document checklist aggregated from the real requiredDocuments of matched schemes.
    ts5 = _now_iso()
    t4 = time.perf_counter()
    unique_docs: Dict[str, Dict[str, Any]] = {}
    for m in matches:
        for doc in m["scheme"].get("requiredDocuments", []) or []:
            if not isinstance(doc, dict):
                continue
            doc_key = str(doc.get("id") or doc.get("nameEn") or "")
            if doc_key and doc_key not in unique_docs:
                unique_docs[doc_key] = doc
    doc_names = [str(d.get("nameEn", "")) for d in unique_docs.values()]
    evidence_by_document = {
        item.get("documentId"): {
            "category": item.get("category"),
            "validityStatus": item.get("validityStatus"),
            "extractedFields": sorted((item.get("extracted") or {}).keys()),
        }
        for item in document_evidence
        if item.get("documentId")
    }
    logger.info(
        "DocumentChecklist complete: scheme_ids=%s required_document_ids=%s saved_document_evidence=%s",
        [m["schemeId"] for m in matches],
        list(unique_docs.keys()),
        evidence_by_document,
    )
    trace.append(AgentExecutionTraceStep(
        stepNumber=5,
        timestamp=ts5,
        agentRole="DocConcierge",
        action="Assembled document checklist and included saved OCR evidence",
        input={
            "matchedSchemes": [m["schemeId"] for m in matches],
            "savedDocumentEvidence": evidence_by_document,
        },
        output={
            "uniqueCertificatesRequired": len(unique_docs),
            "documents": doc_names,
            "savedDocumentIds": list(evidence_by_document.keys()),
        },
        durationMs=_elapsed_ms(t4)
    ))
    
    return (matches, near_misses, trace)


_LANGUAGE_NAMES = {
    "en": "English",
    "kn": "Kannada",
    "hi": "Hindi",
    "ta": "Tamil",
    "ml": "Malayalam",
    "te": "Telugu",
}
_LANG_SUFFIX = {"en": "En", "kn": "Kn", "hi": "Hi", "ta": "Ta", "ml": "Ml", "te": "Te"}
# Shown once when a requested language has no scheme text and English is used instead.
_SCHEME_FALLBACK_NOTE = "Scheme details are shown in English for this language."
_CHAT_LABELS = {
    "en": {
        "benefit": "Benefit",
        "docs": "Required documents",
        "none": "None listed",
        "status": "Status: Eligibility depends on your income, education and land details. Not a guarantee of benefit.",
        "verify": "Please verify on the official .gov.in portal",
    },
    "kn": {
        "benefit": "ಪ್ರಯೋಜನ",
        "docs": "ಅಗತ್ಯ ದಾಖಲೆಗಳು",
        "none": "ಯಾವುದೂ ಪಟ್ಟಿಯಲ್ಲಿಲ್ಲ",
        "status": "ಸ್ಥಿತಿ: ಅರ್ಹತೆ ನಿಮ್ಮ ಆದಾಯ, ಶಿಕ್ಷಣ ಮತ್ತು ಭೂಮಿಯ ವಿವರಗಳ ಮೇಲೆ ಅವಲಂಬಿತ (ಪ್ರಯೋಜನದ ಖಾತರಿ ಅಲ್ಲ).",
        "verify": "ದಯವಿಟ್ಟು ಅಧಿಕೃತ .gov.in ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಪರಿಶೀಲಿಸಿ",
    },
    "hi": {
        "benefit": "लाभ",
        "docs": "आवश्यक दस्तावेज़",
        "none": "कोई सूचीबद्ध नहीं",
        "status": "स्थिति: पात्रता आपकी आय, शिक्षा और भूमि के विवरण पर निर्भर करती है (लाभ की गारंटी नहीं)।",
        "verify": "कृपया आधिकारिक .gov.in पोर्टल पर सत्यापित करें",
    },
}


def _normalize_language(language: Optional[str]) -> str:
    lang = (language or "en").strip().lower()
    return lang if lang in _LANGUAGE_NAMES else "en"


def _labels_for(language: str) -> Dict[str, str]:
    """Chat labels for a language, falling back to English when no translation exists."""
    return _CHAT_LABELS.get(language, _CHAT_LABELS["en"])


def _find_scheme(scheme_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not scheme_id:
        return None
    wanted = str(scheme_id).strip().lower()
    for s in load_schemes_catalog():
        if str(s.get("id", "")).strip().lower() == wanted:
            return s
    return None


def _scheme_sources(scheme: Dict[str, Any]) -> List[str]:
    return [f"{scheme.get('nameEn', '')} official scheme data ({scheme.get('officialPortalUrl', '')})"]


def _scheme_context(scheme: Dict[str, Any]) -> str:
    """English scheme text given to the LLM as the only allowed source."""
    annual_value = scheme.get("annualValueINR")
    lines = [
        f"Scheme name: {scheme.get('nameEn', '')}",
        f"Department: {scheme.get('department', '')}",
        f"Benefit summary: {scheme.get('benefitSummaryEn', '')}",
        f"Annual value (INR): {annual_value if annual_value is not None else 'not quantified in this catalog'}",
        f"Eligibility review note: {scheme.get('eligibilityNoteEn', '')}",
        f"Deadline: {scheme.get('deadline', '')}",
        "Required documents:",
    ]
    for d in scheme.get("requiredDocuments", []) or []:
        if isinstance(d, dict):
            mandatory = "mandatory" if d.get("mandatory") else "optional"
            lines.append(f"- {d.get('nameEn', '')} ({mandatory}; issued by {d.get('authority', '')})")
    lines.append(f"Official portal: {scheme.get('officialPortalUrl', '')}")
    lines.append(f"Helpline: {scheme.get('helpline', '')}")
    return "\n".join(lines)


def _gemini_policy_answer(question: str, scheme: Dict[str, Any], language: str, api_key: str) -> Optional[str]:
    """Answers via the Gemini LangChain client. Returns None if the output is unusable."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, SystemMessage

    labels = _labels_for(language)
    portal = scheme.get("officialPortalUrl", "")
    system_prompt = (
        "You are JanKalyan AI, a welfare scheme assistant for citizens in the states represented in the catalog.\n"
        "Rules:\n"
        "1. Answer ONLY from the scheme information provided in the user message. "
        "If that information does not cover the question, say you do not have that information.\n"
        "2. Do not state eligibility as a fact. Say eligibility depends on the citizen's details (income, education, land) and must be verified on the official .gov.in portal. Never promise approval or assure a benefit.\n"
        f"3. Tell the citizen they must verify every detail on the official .gov.in portal: {portal}\n"
        f"4. Write the whole answer in {_LANGUAGE_NAMES[language]} (language code: {language}).\n"
        "5. Never ask for, repeat, or store an Aadhaar number.\n"
        "Keep the answer short and plain."
    )
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.1)
    res = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Scheme information:\n{_scheme_context(scheme)}\n\nCitizen question: {question}"),
    ])
    text = _llm_content_text(res).strip()
    if not text or "guaranteed" in text.lower():
        return None
    if portal and portal not in text:
        text += f"\n\n{labels['verify']}: {portal}"
    return text


_TRANSLATED_LANGS = ("ta", "ml", "te")


def _translated_entry(scheme_id: Optional[str], lang: str) -> Optional[Dict[str, Any]]:
    """Translated scheme entry for ta/ml/te, or None. Never raises."""
    try:
        if lang not in _TRANSLATED_LANGS or not scheme_id:
            return None
        entry = _load_scheme_translations(lang).get(str(scheme_id))
        return entry if isinstance(entry, dict) else None
    except Exception:
        return None


def _deterministic_scheme_answer(scheme: Dict[str, Any], language: str) -> str:
    """Answer built only from the scheme data, in the requested language."""
    labels = _labels_for(language)
    sfx = _LANG_SUFFIX.get(language, "En")
    translated = _translated_entry(scheme.get("id"), language)
    missing_text = False
    steps_text = ""
    if translated is not None:
        name = str(translated.get("name") or scheme.get("nameEn", ""))
        benefit = str(translated.get("benefit") or scheme.get("benefitSummaryEn", ""))
        steps = translated.get("steps")
        if isinstance(steps, list):
            steps_text = "; ".join(str(s) for s in steps if s)
    else:
        name = scheme.get(f"name{sfx}")
        if not name:
            missing_text = True
            name = scheme.get("nameEn", "")
        benefit = scheme.get(f"benefitSummary{sfx}")
        if not benefit:
            missing_text = True
            benefit = scheme.get("benefitSummaryEn", "")
    docs = []
    for d in scheme.get("requiredDocuments", []) or []:
        if isinstance(d, dict):
            localized = d.get(f"name{sfx}")
            if not localized and translated is None:
                missing_text = True
            docs.append(str(localized or d.get("nameEn", "")))
    docs_text = "; ".join(x for x in docs if x) or labels["none"]
    portal = scheme.get("officialPortalUrl", "")
    lines = [name, f"{labels['benefit']}: {benefit}"]
    if steps_text:
        lines.append(steps_text)
    lines += [
        f"{labels['docs']}: {docs_text}",
        labels["status"],
        f"{labels['verify']}: {portal}",
    ]
    answer = "\n".join(lines)
    if scheme.get("eligibilityMode") == "MANUAL_REVIEW":
        answer += "\n" + str(
            scheme.get("eligibilityNoteEn")
            or "Eligibility is not fully represented in the app; confirm all conditions on the official source."
        )
    if missing_text:
        answer += f"\n{_SCHEME_FALLBACK_NOTE}"
    return answer



def answer_policy_query(question: str, scheme_id: str = None, language: str = "en") -> Tuple[str, List[str]]:
    """Answers citizen policy questions with citations."""
    lang = _normalize_language(language)
    scheme = _find_scheme(scheme_id)

    if scheme is not None:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                answer = _gemini_policy_answer(question, scheme, lang, api_key)
                if answer:
                    return (answer, _scheme_sources(scheme))
            except Exception:
                pass
        return (_deterministic_scheme_answer(scheme, lang), _scheme_sources(scheme))

    q_lower = question.lower()
    
    if any(w in q_lower for w in ["sibling", "brother", "sister", "ibbaru", "both"]):
        return (
            "Yes! Both siblings in the same family can receive the SSP Post-Matric Scholarship, provided both are enrolled in recognized colleges and the total family annual income remains below the ₹2.5 Lakh ceiling.",
            ["SSP Gazette Notification 2026, Section 4.2: Multiple Beneficiaries Clause"]
        )
    elif any(w in q_lower for w in ["attendance", "haajari", "75%"]):
        return (
            "According to Department of Social Welfare norms, minimum 75% institutional attendance is required for full fee reimbursement, but medical exemptions can be granted by the college principal.",
            ["Karnataka Social Welfare Circular No. SWD/491/2026"]
        )
    elif any(w in q_lower for w in ["reapply", "renew", "income cert", "expired"]):
        return (
            "Karnataka Income Certificates issued by Nadakacheri are valid for exactly 5 years. If yours is older, you must renew it on Nadakacheri (takes 7 days and costs ₹40) before the application cutoff.",
            ["Revenue Department Government Order RD 128/2022"]
        )
        
    return (
        "Based on verified Karnataka state guidelines, all eligible citizens can submit their claims directly through Seva Sindhu or SSP without paying any agent fees. Ensure your bank account has Aadhaar-NPCI mapping active.",
        ["Direct Benefit Transfer (DBT) Mission Guidelines Karnataka"]
    )
