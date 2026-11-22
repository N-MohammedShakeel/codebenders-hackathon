# JanKalyan AI: Architecture and Workflow

## 1. What the application does

JanKalyan AI helps citizens discover Indian welfare schemes in plain language. A user can:

- Start at the marketing landing page at `/`, then enter the application at `/discover`.
- Speak or type a situation in English, Kannada, Hindi, Tamil, Malayalam or Telugu.
- Select a state and run the scheme-discovery pipeline.
- View likely matches, near-misses, and schemes needing official eligibility review.
- Browse the scheme catalogue and open an official scheme portal.
- Upload an allowed document for Gemini OCR and inspect extracted fields and expiry evidence.
- Ask a scheme-specific policy question.
- Mark the bank-passbook requirement ready manually without OCR or bank data storage.

The app provides guidance only. It does not authenticate documents or guarantee government sanction.
Gemini is used to find and rank schemes relevant to someone’s situation. Eligibility decisions are separate: only deterministic rules evaluate the small set of schemes with modeled rules, and most catalog entries need official eligibility review.

## 2. System architecture

```text
Browser / React UI
  |  POST /api/intake
  |  POST /api/orchestrator
  |  POST /api/document-ocr
  |  POST /api/chat
  |  GET  /api/tavily-search
  v
FastAPI service
  |
  +-- Intake extractor: heuristics + Gemini
  +-- Orchestrator: profiling -> vector search -> rule engine -> web search -> checklist
  +-- Document OCR: Gemini Vision + printed-date validation
  +-- Policy chat: Gemini with deterministic fallback
  +-- Live search: Tavily official-domain search
```

- Frontend: React 18, TypeScript, Vite 5, React Router 6, Tailwind CSS.
- Backend: Python FastAPI and Pydantic v2.
- Catalog: JSON data in `jankalyan-ai/api/data/` and frontend copies in `jankalyan-ai/frontend/src/data/`.
- Browser storage: `localStorage` for profile, document evidence, application tracker data and recent search metadata.
- Deployment: repository-root `vercel.json` defines internal Vercel services `api` and `frontend`.

## 3. Frontend routes

| Route | Page | Responsibility |
|---|---|---|
| `/` | `LandingPage.tsx` | Marketing introduction with its own navbar and application entry link |
| `/welcome` | `LandingPage.tsx` | Marketing landing-page alias |
| `/discover` | `HomePage.tsx` | Application entry: intake, discovery, results and recent searches |
| `/schemes` | `SchemesCatalogPage.tsx` | State and category filtering |
| `/schemes/:id` | `SchemeDetailPage.tsx` | Scheme details and official portal |
| `/documents` | `DocumentsPage.tsx` | Document checklist, manual readiness and OCR |
| `/tracker` | `TrackerPage.tsx` | Discovered schemes and document-readiness tracking |
| `/passbook` | `PassbookPage.tsx` | Welfare passbook/export view |
| `/field-worker` | `FieldWorkerPage.tsx` | Field-worker-oriented sample workflow |
| `/admin/schemes` | `AdminSchemesPage.tsx` | Disabled catalogue-administration placeholder |

The landing page uses a separate navigation bar with a clear application-entry link. Application routes use the application navbar, whose Discover label follows the selected language. The frontend calls the API from `frontend/src/lib/api.ts` using relative `/api/...` URLs. Vercel routes those URLs to the API service and rewrites frontend paths to `index.html` for direct navigation and refresh; local Vite development proxies `/api` to `http://localhost:8000`.

## 4. Agentic discovery flow

The agentic flow is implemented by `api/agent/orchestrator.py` and `api/agent/tools.py`. It is a deterministic, coordinated pipeline, not a general autonomous agent with unconstrained actions.

```text
Voice/text or sample
  -> Intake/profile extraction
  -> State and profile validation
  -> State-scoped multilingual embedding retrieval
  -> Gemini relevance reranking of the shortlist
  -> Deterministic eligibility evaluation
  -> Official-portal web search
  -> Matched-scheme document checklist
  -> Likely, near-miss, and manual-review output
```

### Step 1: ProfilerAgent

`POST /api/intake` calls `extract_profile_from_text()` in `api/agent/orchestrator.py`.

- Multilingual and English heuristic patterns extract explicit fields.
- Gemini 2.5 Flash may supplement extraction when `GEMINI_API_KEY` is configured.
- The model is constrained to a JSON profile shape and only validated enum values are merged.
- Only explicitly extracted fields are passed to discovery; omitted fields are not treated as known facts by the matching pipeline.
- The selected state overrides text parsing at the discovery layer.
- Logs include extraction mode, language and field names, but not the raw transcript or extracted values.

### Step 2: VectorSearch

`run_orchestration_swarm()` calls `search_in_memory_schemes()`:

- `models/gemini-embedding-001` embeds multilingual scheme names, benefits, criteria and rule descriptions.
- The normalized query uses education, occupation and selected non-sensitive study details; income, caste, disability, name, district and document evidence are excluded.
- The selected state and All-India schemes are filtered before embedding and ranking.
- Cosine similarity returns at most 12 candidates with a minimum score of `0.30`; scheme vectors are cached for the lifetime of the API process.
- The first search in a process creates embeddings for the state-scoped catalog. Later searches reuse cached vectors; a new state's uncached catalog entries are embedded on demand.

### Step 3: GeminiSchemeReranker

- Gemini 2.5 Flash receives the normalized search intent and only the vector shortlist's public scheme fields.
- It returns an ordered subset of directly relevant candidate IDs. Unknown/malformed IDs or model errors are logged and fail discovery rather than exposing an unfiltered vector list; an empty valid list means Gemini found no relevant candidates.
- The model ranks topical relevance only. It must not infer legal eligibility or promise benefits.
- Entrepreneurship, business-loan and women-focused candidates are omitted unless the supplied intent supports them. At most eight manual-review schemes are returned for display.
- Terminal logs show the exact reranker prompts and raw response. Logs do not include API keys, raw intake text, income/caste/disability values or document contents.

### Step 4: RuleEngine

`evaluate_all_schemes()` in `api/agent/tools.py` applies JSON predicates:

- `EQUALS`
- `LTE`
- `GTE`
- `IN`

Classification:

- `LIKELY_ELIGIBLE`: every configured rule passes.
- `NEAR_MISS`: one non-fatal rule fails and a remediation action is generated.
- `INELIGIBLE`: two or more rules fail; these records are included in the near-miss response list with their `INELIGIBLE` status.
- `MANUAL_REVIEW`: the catalog explicitly marks the scheme for manual review; it is excluded from deterministic match evaluation and returned separately.

The current 110-entry catalog has 105 entries marked `MANUAL_REVIEW`; five entries have configured rule predicates. Gemini finds and ranks relevant candidates, but semantic similarity and Gemini ranking are not proof of eligibility.

### Step 5: OfficialWebSearch

`live_tavily_search()` in `api/agent/tools.py` constructs state-specific official-domain queries:

- Andhra Pradesh: `ap.gov.in`, `sspensions.ap.gov.in`, `navasakam.ap.gov.in`, `gsws-nbm.ap.gov.in`, `jnanabhumi.ap.gov.in`, `apagrisnet.gov.in`, `cse.ap.gov.in`, `apcfss.in`, `apmsidc.in` and `apeprocurement.gov.in`
- Karnataka: `karnataka.gov.in`, `sevasindhuservices.karnataka.gov.in`, `ssp.postmatric.karnataka.gov.in`, `bcwd.karnataka.gov.in`, `sw.karnataka.gov.in`, `fruits.karnataka.gov.in`, `kmdc.karnataka.gov.in`, `fisheries.karnataka.gov.in`, `ashraya.karnataka.gov.in`, `raitamitra.karnataka.gov.in` and `kcdf.karnataka.gov.in`
- Kerala: `kerala.gov.in`, `egrantz.kerala.gov.in`, `sjd.kerala.gov.in`, `sha.kerala.gov.in`, `ksywb.kerala.gov.in`, `highereducation.kerala.gov.in`, `fisheries.kerala.gov.in`, `lsgkerala.gov.in`, `keralaagriculture.gov.in` and `kudumbashree.org`
- Tamil Nadu: `tn.gov.in`, `tnsocialwelfare.tn.gov.in`, `tnhealth.tn.gov.in`, `tneaonline.org`, `tndipr.gov.in`, `tnscholarships.gov.in`, `tnstc.in`, `fisheries.tn.gov.in`, `agri.tn.gov.in`, `cmchistn.com` and `ruraldevelopment.tn.gov.in`
- Telangana: `telangana.gov.in`, `telanganalabour.telangana.gov.in`, `tg.meeseva.telangana.gov.in`, `telanganaepass.cgg.gov.in`, `rythubandhu.telangana.gov.in`, `rythubima.telangana.gov.in`, `aarogyasri.telangana.gov.in`, `agri.telangana.gov.in`, `tsmeeseva.cgg.gov.in`, `wehyb.telangana.gov.in` and `swd.telangana.gov.in`
- All India: official central domains such as `india.gov.in`, `gov.in`, `pib.gov.in`, `pmindia.gov.in`, `mygov.in`, `digitalindia.gov.in`, `scholarships.gov.in`, `pmkisan.gov.in`, `mofpi.gov.in`, `msme.gov.in` and `skillindia.gov.in`

Tavily is restricted to those domains for a state where a domain map exists. Other states fall back to central government domains. Missing keys or search failures return an explicit unavailable response with an empty result list; the app never fabricates government results. The standalone search endpoint returns live results; discovery records search metadata in its trace and does not change match classification.

### Step 6: DocConcierge

The orchestrator aggregates required documents from matched schemes, deduplicates document IDs and records saved OCR evidence. It also applies current income evidence to the profile before final rule evaluation.

Document evidence supplied by the browser is limited to category, validity status, extracted fields and save time. Identity and bank records are excluded from OCR and the bank passbook has only a manual-ready flag.

## 5. Separate AI-assisted flows

### Document OCR flow

`POST /api/document-ocr` in `api/index.py` sends an image or PDF to `api/agent/ocr.py`.

1. MIME type and 10 MB size limits are checked.
2. Identity and bank categories are rejected.
3. Gemini 2.5 Flash extracts only generic document type, printed issue date, printed expiry date and annual income.
4. The prompt forbids Aadhaar numbers, bank account numbers, personal names and unsupported inference.
5. The backend compares category and printed dates and returns `CURRENT`, `EXPIRED`, `REVIEW_REQUIRED` or `TYPE_MISMATCH`.
6. The browser saves only extracted fields and validity status in `localStorage`; the uploaded image itself is not added to browser storage.

OCR indicates printed evidence only; it does not authenticate a document or replace the issuing authority.

### Policy chat flow

`POST /api/chat` calls `answer_policy_query()`:

- If a scheme ID is found and Gemini is configured, Gemini answers with the scheme-specific catalog text.
- The response is required to remain grounded in the catalog and official portal.
- If Gemini fails or is not configured, a deterministic, localized scheme answer is used.
- Sources come from the catalog's official portal metadata.

## 6. Terminal and backend logging

The backend logs:

- Intake extraction mode and normalized provided fields.
- State-scoped embedding query, candidate IDs and similarity scores.
- Exact Gemini reranker system/user prompts, raw model response, accepted candidate order and fallback status.
- Profile field names and saved document evidence summaries, not the underlying values or document text.
- Eligible and near-miss IDs.
- State, official domains, search result count and titles.
- Document checklist and saved evidence IDs.
- OCR start, final validity and extracted field names, never raw document text or sensitive identifiers.

Set `AGENT_TRACE_VERBOSE=true` in a local backend terminal to additionally print the full profile-extraction prompt/response and scheme text sent to the embedding model. This can include the user's raw description; do not enable verbose tracing in production or shared logs.

## 7. API routes

Routes are defined in `jankalyan-ai/api/index.py`:

- `GET /api/health`
- `GET /api/schemes`
- `POST /api/intake`
- `POST /api/orchestrator`
- `GET /api/tavily-search`
- `POST /api/document-ocr`
- `POST /api/chat`

## 8. Data and state

- `api/data/schemes.json`: 110 current catalog entries, including native-script title fields for Kannada, Hindi, Tamil, Malayalam and Telugu.
- `api/data/scheme_translations_{ml,ta,te}.json`: supplemental Malayalam, Tamil and Telugu benefit and application-step translations where available.
- `frontend/src/data/schemes.json`: frontend catalog copy.
- `frontend/src/context/LanguageContext.tsx`: selected language and dictionaries.
- `frontend/src/context/CitizenProfileContext.tsx`: citizen profile persistence.
- `frontend/src/context/AppStateContext.tsx`: matches, document evidence, readiness, application tracker and recent search metadata.

Recent searches store state and scheme IDs, not intake text or document details.

Non-English scheme titles are machine-translated/transliterated for readability; the issuing portal remains the authority for official scheme names. Scheme benefits and application details may still fall back to English when a reviewed translation is unavailable.

The application tracker starts empty. A scheme enters the tracker only after the user completes discovery and confirms that they reviewed the full scheme detail page. The entry starts in `DISCOVERED`; it moves to `DOCS_READY` only when every mandatory document required by that scheme is checked or manually marked ready. Saving, clearing or unchecking document evidence recalculates readiness for already tracked discovered schemes. Applied and later stages are not downgraded automatically.

The profile contract now also carries age, gender, disability percentage, monthly salary, government-employee family status, day-scholar status, college type, AICTE approval, quota and attendance/topper indicators where supplied. Each expanded scheme entry stores structured `eligibilityCriteria` and `sourceUrls`; entries with incomplete statutory details remain manual-review candidates.

## 9. Vercel deployment

The repository-root `vercel.json` configures services:

- `api`: root `jankalyan-ai/api`, FastAPI framework.
- `frontend`: root `jankalyan-ai/frontend`, Vite framework.
- `/api/(.*)` is publicly rewritten to `api`.
- `/(.*)` is publicly rewritten to `frontend`.
- Production site: <https://jankalyan-ai.vercel.app/>. The `/` route opens the marketing landing page; `/discover` enters the application.
- The frontend service rewrites client-side routes to `index.html`, so refreshing routes such as `/schemes` and `/tracker` continues to load the app.

No internal service binding is required because the browser calls the API through `/api/*`. Set `GEMINI_API_KEY` and `TAVILY_API_KEY` as Vercel environment variables; do not expose them as frontend `VITE_*` variables.

## 10. Failure and privacy behavior

- Intake extraction can fall back to heuristic parsing; policy chat can use a deterministic answer.
- Gemini embedding or relevance-ranking failure returns HTTP 503; the app does not display an unreranked candidate list. Provider failures such as quota exhaustion or authorization problems are surfaced with actionable messages.
- OCR provider failures return HTTP 502 with provider-specific guidance where available; missing Gemini configuration returns HTTP 503.
- Tavily failure never substitutes fabricated search results.
- Intake, discovery and OCR do not use a client-side mock fallback when the backend is unreachable; errors are surfaced to the user.
- OCR, chat and live search require user-provided API keys/configuration for those services.
- CORS is currently permissive and there is no authentication or rate limiting.
- Document evidence and the profile are browser-local; they are not stored in an application database.
- Identity and bank documents are not accepted for OCR.

## 11. Testing and local development

Backend tests live in `jankalyan-ai/api/tests/` and cover document upload guards, OCR validity and provider errors, multilingual intake, Vercel service-root imports, vector search and orchestration evidence (27 tests).

```powershell
cd "jankalyan-ai"
python -m unittest discover -s api\tests -v
python -m py_compile api\agent\gemini_errors.py api\agent\ocr.py api\agent\orchestrator.py api\index.py

cd frontend
npm run build
```

Run locally:

```powershell
cd "jankalyan-ai"
python -m uvicorn api.index:app --port 8000

cd frontend
npm run dev
```

The Vite development server runs at <http://localhost:3000/>; its `/api` proxy targets the backend on port `8000`.
