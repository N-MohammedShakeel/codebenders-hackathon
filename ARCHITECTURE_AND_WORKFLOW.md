# JanKalyan AI: Architecture and Workflow

## 1. What the application does
JanKalyan AI helps Indian citizens find welfare schemes they may qualify for. A citizen describes themselves in plain language (or fills a form), optionally uploads supporting documents, and the app lists schemes that appear to match, near-misses that need one more action, and schemes that need manual review. It also answers scheme questions in a chat. The current scheme catalogue covers Karnataka plus several other states.

**Important limit:** the app does not verify documents or decide eligibility. Only the government department can sanction a benefit. Every result should be confirmed on the official portal.

## 2. High-level architecture
- Frontend: React 18, TypeScript, Vite 5, react-router-dom 6, Tailwind CSS v4. Located in jankalyan-ai/frontend.
- Backend: Python FastAPI with Pydantic v2 models. Located in jankalyan-ai/api.
- External AI and search services: Google Gemini (intake extraction, policy chat, document OCR) and Tavily (live search of official portals).
- Storage: no database. Scheme catalogue and translations are JSON files in api/data and frontend/src/data. The browser keeps the citizen profile, applications and document records in localStorage.
- Deployment: the root vercel.json defines two services. Service "api" builds jankalyan-ai/api with the fastapi framework. Service "frontend" builds jankalyan-ai/frontend with the vite framework. Rewrites send /api/* to the api service and everything else to the frontend.

## 3. Backend API routes (api/index.py)
- GET /api/health: service status and scheme count.
- GET /api/schemes: returns the scheme catalogue.
- POST /api/intake: turns free text into a citizen profile. Uses Gemini; falls back to a local heuristic parser if Gemini fails. Response reports extractionMode and defaultedFields.
- POST /api/orchestrator: takes a profile and optional document evidence and returns matches, near-misses, manual-review schemes and an execution trace.
- GET /api/tavily-search: live search for official-portal results, optionally tied to a scheme.
- POST /api/document-ocr: multipart upload (file and category). Extracts fields from a document image or PDF with Gemini.
- POST /api/chat: answers a scheme question. With a schemeId it uses Gemini; without one it returns a deterministic answer (mode DETERMINISTIC_FALLBACK).

Data models are in api/models.py: the citizen profile (state, district, education level, family income, caste category, land holding, occupation, Aadhaar-bank link flag, and others), the match result, and the trace step.

## 4. The agentic workflow
The "agents" are a fixed pipeline of steps, not autonomous agents that decide their own actions. The orchestrator (api/agent/orchestrator.py) runs them in this order and records each one in an execution trace:

1. ProfilerAgent: normalises the profile and records which fields were defaulted rather than supplied.
2. VectorSearch: selects candidate schemes for the citizen's state and attributes. Uses a term-frequency cosine similarity over scheme text (api/agent/tools.py).
3. RuleEngine: evaluates each candidate's rules against the profile. Deterministic, no LLM. Operators: EQUALS, LTE, GTE, IN. Schemes with no rules or with eligibilityMode MANUAL_REVIEW are routed to manual review.
4. TavilyDetective: a live search of official portals for each candidate (api/agent/tools.py). It adds reference links; it does not change the match result.
5. DocConcierge: builds the document checklist from the matched schemes and marks which documents are already saved as valid evidence.

Result categories: LIKELY_ELIGIBLE (all rules pass), NEAR_MISS (exactly one rule fails, with a remediation action), and MANUAL_REVIEW.

Document evidence: the OCR module (api/agent/ocr.py) classifies a document into a category, extracts its fields and assigns a validity status. Identity and bank documents are rejected at upload, and the prompts forbid reading Aadhaar or bank numbers. Client-supplied evidence is used to set income; see the limitations below.

LLM use: Gemini (model gemini-2.5-flash) is used for intake, policy chat and OCR. Eligibility decisions are not made by the LLM.

Failure handling: when Gemini or Tavily fails, the backend returns a fallback result and marks it in the response (for example extractionMode HEURISTIC_FALLBACK, mode DETERMINISTIC_FALLBACK). The browser also has its own fallback path when the backend is unreachable.

## 5. Frontend
- Routes (frontend/src/App.tsx): / (home and intake), /schemes, /schemes/:id, /documents, /tracker, /passbook, /field-worker, /admin/schemes.
- State: three React contexts provide the language, the citizen profile and app state (applications and document records). Persistence is in localStorage.
- Backend calls (frontend/src/lib/api.ts): /api/intake, /api/orchestrator, /api/document-ocr, /api/tavily-search, /api/chat.
- Offline behaviour: the browser contains a rule evaluator that mirrors the backend's rules for when the backend is unreachable. It is not identical to the backend.
- Service worker (frontend/public/sw.js): caches the root page, index.html and manifest.json, using a network-first strategy with cache fallback. Scheme data and user records are not cached.
- Languages: English, Kannada, Hindi, and Tamil, Malayalam and Telugu for scheme text.

## 6. Data
- api/data/schemes.json: 13 schemes. Each has an id, name, state, department, official portal URL, lastVerifiedDate and eligibility rules. Five Karnataka schemes have rules; eight other-state schemes have none and go to manual review.
- api/data/scheme_translations_{ml,ta,te}.json: scheme text in Malayalam, Tamil and Telugu.
- frontend/src/data: a copy of the scheme and translation data used by the catalogue pages.

## 7. Configuration
Environment variables (names only; values go in .env locally or in Vercel project settings):
- GEMINI_API_KEY
- TAVILY_API_KEY

Backend dependencies are listed in api/requirements.txt: fastapi, uvicorn, pydantic, langchain, langchain-google-genai, tavily-python, python-multipart, google-generativeai, python-dotenv (all with minimum versions, none pinned exactly).

## 8. Testing
Backend unit tests are in api/tests (15 tests) and cover the identity/bank upload block, multilingual intake samples, OCR validity handling and evidence handling. Run them from the project root with PYTHONPATH set to that folder. Frontend: npm run build runs the TypeScript check and the Vite build.

## 9. Known limitations
- Scheme data has no official government source references for each rule. Only 5 of 13 schemes have rules.
- The profile does not capture several inputs real schemes need (age, gender, disability, bank account, residence proof).
- Client-supplied document evidence can set family income without server-side verification.
- No authentication or rate limiting on the paid endpoints; CORS allows all origins.
- No consent screen before personal data is sent to Gemini or Tavily.
- Offline support covers only the app shell, not scheme data or saved records.
- Some admin and tracker features are placeholders (editing and reminders are disabled).
- Field Worker queue is sample data kept in the page.

## 10. Running locally
1. Copy jankalyan-ai/.env.example to jankalyan-ai/.env and add your keys.
2. Backend: from jankalyan-ai, install api/requirements.txt, then run uvicorn api.index:app --port 8000 with PYTHONPATH set to jankalyan-ai.
3. Frontend: from jankalyan-ai/frontend, run npm install then npm run dev (port 3000, proxies /api to port 8000).
