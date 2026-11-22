"""LangChain & Deterministic Rule Engine Tools for JanKalyan AI."""

import json
import hashlib
import logging
import math
import os
import threading
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Load schemes data safely
SCHEMES_FILE = Path(__file__).parent.parent / "data" / "schemes.json"
VECTOR_EMBEDDING_MODEL = "models/gemini-embedding-001"
_EMBEDDING_BATCH_SIZE = 64
_VECTOR_TOP_K = 12
_VECTOR_MIN_SCORE = 0.30
_SCHEME_EMBEDDINGS: Dict[str, List[float]] = {}
_SCHEME_EMBEDDINGS_LOCK = threading.RLock()
_ALL_INDIA_OFFICIAL_DOMAINS = [
    "india.gov.in",
    "gov.in",
    "pib.gov.in",
    "pmindia.gov.in",
    "mygov.in",
    "digitalindia.gov.in",
    "scholarships.gov.in",
    "pmkisan.gov.in",
    "mofpi.gov.in",
    "msme.gov.in",
    "skillindia.gov.in",
]

_STATE_OFFICIAL_DOMAINS = {
    "Andhra Pradesh": [
        "ap.gov.in",
        "sspensions.ap.gov.in",
        "navasakam.ap.gov.in",
        "gsws-nbm.ap.gov.in",
        "jnanabhumi.ap.gov.in",
        "apagrisnet.gov.in",
        "cse.ap.gov.in",
        "apcfss.in",
        "apmsidc.in",
        "apeprocurement.gov.in",
    ],
    "Karnataka": [
        "karnataka.gov.in",
        "sevasindhuservices.karnataka.gov.in",
        "ssp.postmatric.karnataka.gov.in",
        "bcwd.karnataka.gov.in",
        "sw.karnataka.gov.in",
        "fruits.karnataka.gov.in",
        "kmdc.karnataka.gov.in",
        "fisheries.karnataka.gov.in",
        "ashraya.karnataka.gov.in",
        "raitamitra.karnataka.gov.in",
        "kcdf.karnataka.gov.in",
    ],
    "Kerala": [
        "kerala.gov.in",
        "egrantz.kerala.gov.in",
        "sjd.kerala.gov.in",
        "sha.kerala.gov.in",
        "ksywb.kerala.gov.in",
        "highereducation.kerala.gov.in",
        "fisheries.kerala.gov.in",
        "lsgkerala.gov.in",
        "keralaagriculture.gov.in",
        "kudumbashree.org",
    ],
    "Tamil Nadu": [
        "tn.gov.in",
        "tnsocialwelfare.tn.gov.in",
        "tnhealth.tn.gov.in",
        "tneaonline.org",
        "tndipr.gov.in",
        "tnscholarships.gov.in",
        "tnstc.in",
        "fisheries.tn.gov.in",
        "agri.tn.gov.in",
        "cmchistn.com",
        "ruraldevelopment.tn.gov.in",
    ],
    "Telangana": [
        "telangana.gov.in",
        "telanganalabour.telangana.gov.in",
        "tg.meeseva.telangana.gov.in",
        "telanganaepass.cgg.gov.in",
        "rythubandhu.telangana.gov.in",
        "rythubima.telangana.gov.in",
        "aarogyasri.telangana.gov.in",
        "agri.telangana.gov.in",
        "tsmeeseva.cgg.gov.in",
        "wehyb.telangana.gov.in",
        "swd.telangana.gov.in",
    ],
}


def get_official_search_domains(
    state: Optional[str] = None,
    scheme_id: Optional[str] = None,
) -> List[str]:
    """Returns the public official-domain allowlist for a selected state."""
    state_domains = _STATE_OFFICIAL_DOMAINS.get(state or "", [])
    domains: List[str]
    if state:
        domains = list(dict.fromkeys([*state_domains, *_ALL_INDIA_OFFICIAL_DOMAINS]))
    else:
        domains = list(_ALL_INDIA_OFFICIAL_DOMAINS)
    if scheme_id:
        scheme = next(
            (item for item in load_schemes_catalog() if item.get("id") == scheme_id),
            None,
        )
        if scheme:
            source_urls = [
                *(scheme.get("sourceUrls") or []),
                scheme.get("officialPortalUrl"),
            ]
            for source_url in source_urls:
                if not isinstance(source_url, str):
                    continue
                parsed = urlparse(source_url)
                if parsed.scheme == "https" and parsed.hostname:
                    domains.append(parsed.hostname.lower())
    return list(dict.fromkeys(domains))


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


def _scheme_text(s: Dict[str, Any]) -> str:
    """Multilingual scheme text used to build its semantic-search embedding."""
    parts = [
        s.get("nameEn", ""),
        s.get("nameKn", ""),
        s.get("nameHi", ""),
        s.get("department", ""),
        s.get("state", ""),
        s.get("category", ""),
        s.get("benefitSummaryEn", ""),
        s.get("benefitSummaryKn", ""),
        s.get("benefitSummaryHi", ""),
        s.get("eligibilityNoteEn", ""),
    ]
    for criterion in s.get("eligibilityCriteria", []) or []:
        if isinstance(criterion, dict):
            parts.append(criterion.get("criterionEn", ""))
    for r in s.get("rules", []) or []:
        if isinstance(r, dict):
            parts.append(r.get("descriptionEn", ""))
    for document in s.get("requiredDocuments", []) or []:
        if isinstance(document, dict):
            parts.append(document.get("nameEn", ""))
    return " ".join(str(p) for p in parts if p)


class VectorSearchError(RuntimeError):
    """Raised when semantic retrieval cannot be completed."""


def _get_embedding_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise VectorSearchError("Gemini embeddings are not configured.")
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
    except ImportError as exc:
        logger.error("Gemini embedding dependency is unavailable (%s).", type(exc).__name__)
        raise VectorSearchError("Gemini embeddings are unavailable.") from None
    return GoogleGenerativeAIEmbeddings(
        model=VECTOR_EMBEDDING_MODEL,
        google_api_key=api_key,
    )


def _embedding_key(scheme: Dict[str, Any], text: str) -> str:
    value = f"{scheme.get('id', '')}\0{text}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _verbose_agent_trace_enabled() -> bool:
    return os.getenv("AGENT_TRACE_VERBOSE", "").strip().lower() in {"1", "true", "yes"}


def _valid_embedding(vector: Any) -> bool:
    return (
        isinstance(vector, list)
        and bool(vector)
        and all(isinstance(value, (int, float)) and math.isfinite(value) for value in vector)
    )


def _cosine_similarity(left: List[float], right: List[float]) -> float:
    if len(left) != len(right):
        raise VectorSearchError("Gemini returned embeddings with inconsistent dimensions.")
    dot = sum(a * b for a, b in zip(left, right))
    norm_left = math.sqrt(sum(value * value for value in left))
    norm_right = math.sqrt(sum(value * value for value in right))
    if not norm_left or not norm_right:
        return 0.0
    return dot / (norm_left * norm_right)


def _populate_scheme_embedding_cache(
    client: Any,
    schemes: List[Dict[str, Any]],
    texts: List[str],
) -> List[Tuple[Dict[str, Any], str]]:
    entries = [
        (scheme, text, _embedding_key(scheme, text))
        for scheme, text in zip(schemes, texts)
    ]
    missing = [entry for entry in entries if entry[2] not in _SCHEME_EMBEDDINGS]
    logger.info(
        "Gemini embedding index: model=%s scoped_scheme_count=%d cache_miss_count=%d",
        VECTOR_EMBEDDING_MODEL,
        len(entries),
        len(missing),
    )
    for start in range(0, len(missing), _EMBEDDING_BATCH_SIZE):
        batch = missing[start : start + _EMBEDDING_BATCH_SIZE]
        if _verbose_agent_trace_enabled():
            logger.info(
                "GeminiEmbeddingDocuments input=%s",
                json.dumps(
                    [{"schemeId": entry[0].get("id"), "text": entry[1]} for entry in batch],
                    ensure_ascii=False,
                ),
            )
        try:
            vectors = client.embed_documents([entry[1] for entry in batch])
        except Exception as exc:
            logger.error(
                "Gemini scheme embedding request failed (%s); provider details omitted.",
                type(exc).__name__,
            )
            raise VectorSearchError("Gemini scheme embeddings could not be generated.") from None
        if len(vectors) != len(batch) or not all(_valid_embedding(vector) for vector in vectors):
            logger.error("Gemini returned an invalid scheme-embedding batch.")
            raise VectorSearchError("Gemini returned invalid scheme embeddings.")
        for (_, _, key), vector in zip(batch, vectors):
            _SCHEME_EMBEDDINGS[key] = [float(value) for value in vector]
        logger.info(
            "GeminiEmbeddingDocuments response: item_count=%d dimensions=%d",
            len(vectors),
            len(vectors[0]) if vectors else 0,
        )
    return [(scheme, key) for scheme, _, key in entries]


def search_in_memory_schemes(
    query: str,
    state: Optional[str] = None,
    top_k: int = _VECTOR_TOP_K,
    min_score: float = _VECTOR_MIN_SCORE,
) -> List[Dict[str, Any]]:
    """Rank state-scoped schemes with Gemini embeddings and cosine similarity."""
    if not query.strip():
        logger.info("Semantic vector search skipped: no profile search intent was available.")
        return []
    catalog = load_schemes_catalog()
    scoped_schemes = [
        scheme for scheme in catalog
        if state is None or scheme.get("state") in (state, "All India")
    ]
    if not scoped_schemes:
        logger.info("Semantic vector search found no schemes for state=%s.", state)
        return []

    texts = [_scheme_text(scheme) for scheme in scoped_schemes]
    logger.info(
        "Semantic vector search request: model=%s state=%s query=%r scoped_scheme_count=%d",
        VECTOR_EMBEDDING_MODEL,
        state,
        query,
        len(scoped_schemes),
    )
    with _SCHEME_EMBEDDINGS_LOCK:
        try:
            client = _get_embedding_client()
        except VectorSearchError:
            raise
        except Exception as exc:
            logger.error(
                "Gemini embedding client initialization failed (%s); provider details omitted.",
                type(exc).__name__,
            )
            raise VectorSearchError("Gemini embedding client could not be initialized.") from None
        entries = _populate_scheme_embedding_cache(client, scoped_schemes, texts)
        try:
            query_vector = client.embed_query(query)
        except Exception as exc:
            logger.error(
                "Gemini query embedding failed (%s); provider details omitted.",
                type(exc).__name__,
            )
            raise VectorSearchError("Gemini query embedding could not be generated.") from None
        if not _valid_embedding(query_vector):
            logger.error("Gemini returned an invalid query embedding.")
            raise VectorSearchError("Gemini returned an invalid query embedding.")
        logger.info(
            "GeminiEmbeddingQuery response: dimensions=%d",
            len(query_vector),
        )

        scored = [
            (
                _cosine_similarity(query_vector, _SCHEME_EMBEDDINGS[key]),
                scheme,
            )
            for scheme, key in entries
        ]

    scored.sort(key=lambda item: item[0], reverse=True)
    results = [
        {**scheme, "score": round(score, 4)}
        for score, scheme in scored
        if score >= min_score
    ][: max(1, min(top_k, 30))]
    logger.info(
        "Semantic vector search result: state=%s minimum_score=%.2f top_k=%d result_count=%d candidates=%s",
        state,
        min_score,
        top_k,
        len(results),
        [{"id": scheme.get("id"), "score": scheme["score"]} for scheme in results],
    )
    return results



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
    domains = get_official_search_domains(state, scheme_id)
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
