"""FastAPI Entrypoint for JanKalyan AI (Claim What's Yours).
Supports Vercel serverless deployment and local uvicorn development.
"""

import os
import sys
import logging

from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any, Literal

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"), override=False)
except ImportError:
    pass


if __package__ == "api":
    from api.models import (
        CitizenProfile,
        IntakeRequest,
        IntakeResponse,
        OrchestratorRequest,
        OrchestratorResponse,
        ChatRequest,
        ChatResponse,
        DocumentOCRResponse,
        TavilySearchResponse
    )
    from api.agent.tools import load_schemes_catalog, live_tavily_search, VectorSearchError
    from api.agent.orchestrator import (
        extract_profile_from_text,
        run_orchestration_swarm,
        answer_policy_query,
        _find_scheme,
        _normalize_language,
        _deterministic_scheme_answer,
    )
    from api.agent.ocr import analyze_document_image, OCRServiceError
else:
    from models import (
        CitizenProfile,
        IntakeRequest,
        IntakeResponse,
        OrchestratorRequest,
        OrchestratorResponse,
        ChatRequest,
        ChatResponse,
        DocumentOCRResponse,
        TavilySearchResponse
    )
    from agent.tools import load_schemes_catalog, live_tavily_search, VectorSearchError
    from agent.orchestrator import (
        extract_profile_from_text,
        run_orchestration_swarm,
        answer_policy_query,
        _find_scheme,
        _normalize_language,
        _deterministic_scheme_answer,
    )
    from agent.ocr import analyze_document_image, OCRServiceError

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logging.getLogger().setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

app = FastAPI(
    title="JanKalyan AI Backend",
    description="Welfare scheme discovery, document OCR, and eligibility support.",
    version="1.0.0"
)

# Enable CORS for React frontend (Vite local dev and production domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "JanKalyan AI Agentic Backend",
        "schemesCount": len(load_schemes_catalog()),
        "guardrail": "Likely Eligible (Never Guaranteed), Zero Aadhaar Stored"
    }

@app.get("/api/schemes")
def get_all_schemes():
    """Returns all verified schemes in the knowledge base."""
    return load_schemes_catalog()

@app.post("/api/intake", response_model=IntakeResponse)
def intake_endpoint(req: IntakeRequest):
    """Processes plain language speech or text and extracts a structured demographic profile."""
    profile, mode = extract_profile_from_text(req.text, req.language)
    if not isinstance(profile, CitizenProfile):
        profile = CitizenProfile(**profile)
    stated = profile.model_dump(exclude_unset=True)
    defaulted_fields = [name for name in CitizenProfile.model_fields if name not in profile.model_fields_set]
    logger.info(
        "Intake complete: extraction_mode=%s provided_fields=%s",
        mode,
        sorted(stated.keys()),
    )
    return IntakeResponse(profile=stated, extractionMode=mode, defaultedFields=defaulted_fields)

@app.post("/api/orchestrator", response_model=OrchestratorResponse)
def orchestrator_endpoint(req: OrchestratorRequest):
    """Coordinates semantic retrieval, Gemini relevance ranking and deterministic rules."""
    profile_dict = req.profile.model_dump(exclude_unset=True)
    evidence = [item.model_dump() for item in req.documentEvidence]
    income_documents = [
        item for item in evidence
        if item.get("category") == "income"
        and item.get("validityStatus") == "CURRENT"
        and (item.get("extracted") or {}).get("annualIncomeINR") is not None
    ]
    if income_documents:
        newest_income_document = max(income_documents, key=lambda item: item.get("savedAt") or "")
        profile_dict["familyAnnualIncome"] = newest_income_document["extracted"]["annualIncomeINR"]
        logger.info("Orchestrator using current income-certificate OCR evidence for rule matching.")
    logger.info(
        "Orchestrator request: state=%s saved_document_categories=%s income_evidence_applied=%s",
        profile_dict.get("state"),
        [item.get("category") for item in evidence],
        bool(income_documents),
    )
    try:
        matches, near_misses, trace = run_orchestration_swarm(profile_dict, evidence)
    except VectorSearchError as exc:
        logger.error("Scheme discovery AI unavailable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    manual_review_ids = (
        trace[1].output.get("manualReviewCandidateIds", [])
        if len(trace) > 1 and isinstance(trace[1].output, dict)
        else []
    )
    schemes_by_id = {scheme.get("id"): scheme for scheme in load_schemes_catalog()}
    return OrchestratorResponse(
        profile=req.profile,
        matches=matches,
        nearMisses=near_misses,
        manualReviewSchemes=[
            schemes_by_id[scheme_id]
            for scheme_id in manual_review_ids
            if scheme_id in schemes_by_id
        ],
        trace=trace,
        defaultedFields=[name for name in CitizenProfile.model_fields if name not in req.profile.model_fields_set]
    )

@app.get("/api/tavily-search", response_model=TavilySearchResponse)
def tavily_search_endpoint(
    query: str = Query("official government welfare schemes"),
    schemeId: Optional[str] = None,
    state: Optional[str] = None,
):
    """Checks live gazette notifications and deadline extensions on official portals."""
    if schemeId:
        scheme = next((item for item in load_schemes_catalog() if item.get("id") == schemeId), None)
        if scheme:
            state = scheme.get("state")
    result = live_tavily_search(query, scheme_id=schemeId, state=state)
    return TavilySearchResponse(**result)

@app.post("/api/document-ocr", response_model=DocumentOCRResponse)
async def document_ocr_endpoint(
    file: UploadFile = File(...),
    category: Literal["identity", "income", "residence", "education", "caste", "land", "bank", "other"] = Form(...),
):
    """Extracts limited document fields with Gemini and checks printed expiry dates."""
    allowed_mime_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/heic",
        "application/pdf",
    }
    if file.content_type not in allowed_mime_types:
        raise HTTPException(status_code=415, detail="Upload a JPG, PNG, WEBP, HEIC, or PDF document.")
    if category in {"identity", "bank"}:
        raise HTTPException(
            status_code=400,
            detail="Identity and bank documents are not accepted for OCR. Do not upload Aadhaar cards or bank records.",
        )
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(status_code=503, detail="Gemini OCR is not configured.")

    file_bytes = await file.read(10 * 1024 * 1024 + 1)
    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded document is empty.")
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="The uploaded document exceeds the 10 MB limit.")

    logger.info(
        "DocumentOCR start: category=%s mime_type=%s bytes=%d",
        category,
        file.content_type,
        len(file_bytes),
    )
    try:
        result = analyze_document_image(file_bytes, file.filename, file.content_type, category)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OCRServiceError as exc:
        logger.error("DocumentOCR failed: category=%s reason=%s", category, exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    logger.info(
        "DocumentOCR complete: category=%s validity=%s extracted_fields=%s",
        category,
        result["validity"]["status"],
        [key for key, value in result["extracted"].items() if value is not None],
    )
    return DocumentOCRResponse(**result)

def _chat_mode(scheme_id: Optional[str], language: str, answer: str) -> str:
    """Reports GEMINI only when the answer is not the deterministic scheme text.

    answer_policy_query returns the deterministic text on its fallback path and
    for non-scheme questions, and LLM text only on the Gemini path.
    """
    scheme = _find_scheme(scheme_id)
    if scheme is None or not os.getenv("GEMINI_API_KEY"):
        return "DETERMINISTIC_FALLBACK"
    if answer == _deterministic_scheme_answer(scheme, _normalize_language(language)):
        return "DETERMINISTIC_FALLBACK"
    return "GEMINI"

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """Answers citizen policy questions with verified gazette citations."""
    answer, sources = answer_policy_query(req.question, req.schemeId, req.language)
    return ChatResponse(
        answer=answer,
        sources=sources,
        mode=_chat_mode(req.schemeId, req.language, answer)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True)
