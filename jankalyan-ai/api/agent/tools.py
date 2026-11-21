"""LangChain & Deterministic Rule Engine Tools for JanKalyan AI."""

import json
import logging
import math
import os
import re
from datetime import datetime
from collections import Counter
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Load schemes data safely
SCHEMES_FILE = Path(__file__).parent.parent / "data" / "schemes.json"
_STATE_OFFICIAL_DOMAINS = {
    "Andhra Pradesh": ["ap.gov.in"],
    "Karnataka": ["karnataka.gov.in"],
    "Kerala": ["kerala.gov.in"],
    "Tamil Nadu": ["tn.gov.in", "tnsocialwelfare.tn.gov.in"],
    "Telangana": ["telangana.gov.in"],
}


def load_schemes_catalog() -> List[Dict[str, Any]]:
    if not SCHEMES_FILE.exists():
        return []
    try:
        with open(SCHEMES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, OSError) as e:
        logger.warning("Could not load schemes catalog from %s: %s", SCHEMES_FILE, e)
        return []
    if not isinstance(data, list):
        logger.warning("Schemes catalog %s is not a JSON list", SCHEMES_FILE)
        return []
    return data


def _tokenize(text: Any) -> List[str]:
    """Lowercase and split on anything that is not a letter or digit."""
    return re.findall(r"[^\W_]+", str(text).lower())


def _cosine(a: Counter, b: Counter) -> float:
    """Cosine similarity between two term-frequency vectors."""
    if not a or not b:
        return 0.0
    dot = sum(count * b.get(term, 0) for term, count in a.items())
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _scheme_text(s: Dict[str, Any]) -> str:
    """English text of a scheme used for vector search."""
    parts = [
        s.get("nameEn", ""),
        s.get("department", ""),
        s.get("category", ""),
        s.get("benefitSummaryEn", ""),
    ]
    for r in s.get("rules", []) or []:
        if isinstance(r, dict):
            parts.append(r.get("descriptionEn", ""))
    return " ".join(str(p) for p in parts if p)


_SEARCH_STOPWORDS = frozenset({
    "for", "the", "a", "an", "of", "to", "my", "i", "am", "do",
    "need", "what", "is", "in", "and", "with", "on",
})
_NAME_FIELD_WEIGHT = 3  # extra weight multiplier for tokens in nameEn and category


def _content_tokens(text: Any) -> List[str]:
    """Tokens with common stopwords removed (falls back to all tokens if none remain)."""
    tokens = _tokenize(text)
    kept = [t for t in tokens if t not in _SEARCH_STOPWORDS]
    return kept or tokens


def search_in_memory_schemes(query: str) -> List[Dict[str, Any]]:
    """In-memory bag-of-words term-frequency cosine similarity over the schemes catalog.

    Tokens from nameEn and category count _NAME_FIELD_WEIGHT times; other fields count once.
    """
    catalog = load_schemes_catalog()
    if not query:
        return catalog

    query_vec = Counter(_content_tokens(query))

    scored = []
    for s in catalog:
        doc_vec = Counter(_content_tokens(_scheme_text(s)))
        name_tokens = Counter(_content_tokens(f"{s.get('nameEn', '')} {s.get('category', '')}"))
        for term, count in name_tokens.items():
            doc_vec[term] += (_NAME_FIELD_WEIGHT - 1) * count
        scored.append((_cosine(query_vec, doc_vec), s))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [{**item[1], "score": round(item[0], 3)} for item in scored]



def evaluate_single_rule(predicate: Dict[str, Any], profile_dict: Dict[str, Any]) -> Tuple[bool, Any, Any]:
    field = predicate.get("field")
    operator = predicate.get("operator")
    req_val = predicate.get("value")
    
    user_val = profile_dict.get(field)
    if user_val is None:
        # Field not provided
        return (False, None, req_val)
        
    passed = False
    if operator == "EQUALS":
        passed = str(user_val).strip().upper() == str(req_val).strip().upper()
    elif operator == "LTE":
        try:
            passed = float(user_val) <= float(req_val)
        except (ValueError, TypeError):
            passed = False
    elif operator == "GTE":
        try:
            passed = float(user_val) >= float(req_val)
        except (ValueError, TypeError):
            passed = False
    elif operator == "IN":
        if isinstance(req_val, list):
            passed = str(user_val).strip().upper() in [str(v).strip().upper() for v in req_val]
        else:
            passed = str(user_val).strip().upper() == str(req_val).strip().upper()
            
    return (passed, user_val, req_val)


def evaluate_all_schemes(profile_dict: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Strictly evaluates mathematical predicates against citizen profile.
    Returns (matches, near_misses).

    Classification per scheme:
      - LIKELY_ELIGIBLE: every rule passes (goes to matches).
      - NEAR_MISS: exactly one rule fails and that rule is not fatal (goes to near_misses).
      - INELIGIBLE: two or more rules fail (goes to near_misses with status INELIGIBLE).
        A single fatal failure is not returned in either list; it is only logged.
    """
    catalog = load_schemes_catalog()
    matches = []
    near_misses = []
    selected_state = profile_dict.get("state")
    
    for s in catalog:
        if s.get("state") not in (selected_state, "All India"):
            continue
        if s.get("eligibilityMode") == "MANUAL_REVIEW":
            logger.info(
                "Scheme %s requires manual eligibility review; not included in automated results.",
                s.get("id"),
            )
            continue

        scheme_id = s.get("id")
        if not scheme_id:
            logger.warning("Skipping scheme without an id: %r", s.get("nameEn", s))
            continue

        rules = s.get("rules", []) or []
        passed_rules = []
        failed_rules = []
        
        for r in rules:
            passed, user_val, req_val = evaluate_single_rule(r, profile_dict)
            rule_detail = {
                "predicate": r,
                "userValue": user_val,
                "requiredValue": req_val,
                "passed": passed
            }
            if passed:
                passed_rules.append(rule_detail)
            else:
                failed_rules.append(rule_detail)
                
        total_rules = len(rules) if rules else 1
        match_percentage = (len(passed_rules) / total_rules) * 100.0
        
        if len(failed_rules) == 0:
            matches.append({
                "schemeId": scheme_id,
                "scheme": s,
                "status": "LIKELY_ELIGIBLE",
                "matchPercentage": 100.0,
                "passedRules": passed_rules,
                "failedRules": [],
                "nearMissRemediation": None
            })
        elif len(failed_rules) == 1 and not failed_rules[0]["predicate"].get("fatal", False):
            failed_field = failed_rules[0]["predicate"].get("field")
            remediation = {
                "actionTitleEn": f"Action needed for {failed_rules[0]['predicate'].get('descriptionEn')}",
                "actionTitleKn": f"ಕ್ರಮ ಅಗತ್ಯವಿದೆ: {failed_rules[0]['predicate'].get('descriptionKn')}",
                "actionTitleHi": f"कार्रवाई की आवश्यकता है: {failed_rules[0]['predicate'].get('descriptionHi')}",
                "instructionsEn": f"Update or register your {failed_field} on the official state portal to qualify.",
                "instructionsKn": f"ಅರ್ಹತೆ ಪಡೆಯಲು ಅಧಿಕೃತ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ನಿಮ್ಮ {failed_field} ಅನ್ನು ನವೀಕರಿಸಿ.",
                "instructionsHi": f"पात्रता प्राप्त करने के लिए आधिकारिक पोर्टल पर अपना {failed_field} अपडेट करें।",
                "portalUrl": s.get("officialPortalUrl")
            }
            near_misses.append({
                "schemeId": scheme_id,
                "scheme": s,
                "status": "NEAR_MISS",
                "matchPercentage": round(match_percentage, 1),
                "passedRules": passed_rules,
                "failedRules": failed_rules,
                "nearMissRemediation": remediation
            })
        else:
            # INELIGIBLE with two or more failed rules is returned in near_misses with its own status.
            # A single fatal failure is only logged.
            if len(failed_rules) >= 2:
                failed_descriptions = "; ".join(
                    str(f["predicate"].get("descriptionEn", f["predicate"].get("field")))
                    for f in failed_rules
                )
                near_misses.append({
                    "schemeId": scheme_id,
                    "scheme": s,
                    "status": "INELIGIBLE",
                    "matchPercentage": round(match_percentage, 1),
                    "passedRules": passed_rules,
                    "failedRules": failed_rules,
                    "nearMissRemediation": f"Not eligible. Criteria not met: {failed_descriptions}"
                })
            logger.info("Scheme %s classified as INELIGIBLE (%d rules failed)", scheme_id, len(failed_rules))
            
    return (matches, near_misses)



def live_tavily_search(
    query: str,
    scheme_id: Optional[str] = None,
    state: Optional[str] = None,
) -> Dict[str, Any]:
    """Search official portals for the selected state; never fabricate fallback results."""
    domains = _STATE_OFFICIAL_DOMAINS.get(state or "", ["india.gov.in", "pib.gov.in"])
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.warning("Live scheme search skipped: TAVILY_API_KEY is not configured (state=%s)", state)
        return {
            "query": query,
            "results": [],
            "isMock": True,
            "note": "Live search is unavailable because TAVILY_API_KEY is not configured.",
            "verifiedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        }

    try:
        from tavily import TavilyClient

        response = TavilyClient(api_key=api_key).search(
            query=query,
            include_domains=domains,
            max_results=3,
        )
        results = response.get("results", [])
        logger.info(
            "WebSearch complete: state=%s scheme_id=%s domains=%s result_count=%d result_titles=%s",
            state,
            scheme_id,
            domains,
            len(results),
            [result.get("title") for result in results if isinstance(result, dict)],
        )
        return {
            "query": query,
            "results": results,
            "isMock": False,
            "note": "Search results are limited to official government domains; verify rules at the source.",
            "verifiedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
    except Exception:
        logger.exception("Live scheme search failed: state=%s scheme_id=%s domains=%s", state, scheme_id, domains)
        return {
            "query": query,
            "results": [],
            "isMock": True,
            "note": "Live search failed. No fallback results were substituted.",
            "verifiedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        }
