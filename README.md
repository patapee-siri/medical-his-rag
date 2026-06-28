# 🏥 Medical HIS RAG

A production-grade **Healthcare Information System** with Retrieval-Augmented
Generation. Patient management + AI-assisted clinical consultation grounded in
medical literature, with citations and confidence scoring.

> ⚠️ AI-assisted decision support only — not a substitute for professional
> medical judgment.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 · Vite · Tailwind CSS v4 · Axios |
| Backend | FastAPI · Pydantic v2 · SQLAlchemy · structlog |
| LLM | HuggingFace Inference API (Llama-3.1-8B-Instruct) |
| Embeddings | fastembed (ONNX) · bge-small-en-v1.5 |
| Vector DB | Qdrant (Docker) |
| Retrieval | Dense + BM25 re-ranking · hybrid live augmentation |
| Live sources | PubMed · Europe PMC · ClinicalTrials.gov |
| Database | SQLite |
| Standards | FHIR-inspired schemas |

## Live multi-source RAG (hybrid)

Retrieval runs over a local Qdrant corpus first. When local results are weak,
the system fetches fresh literature **live** from PubMed, Europe PMC, and
ClinicalTrials.gov, embeds and caches it in Qdrant, then re-searches — so the
knowledge base grows with use.

> **Credibility hard rule:** only peer-reviewed / authoritative sources may ever
> surface. Non-peer-reviewed content (preprints such as bioRxiv/medRxiv) is
> excluded **in code** (a credibility allowlist enforced at ingestion *and*
> search), not by convention. Set `NCBI_API_KEY` to raise PubMed's rate limit.

## Project Structure

```
medical-his-rag/
├── backend/          FastAPI app (API, schemas, services, routers)
│   ├── app/
│   │   ├── main.py           App entry (CORS, logging, error handling)
│   │   ├── config.py         Typed settings from .env
│   │   ├── schemas/          Pydantic models (patient, consultation)
│   │   ├── routers/          API routes (health, …)
│   │   └── utils/            Logging + exception handlers
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         React + Vite + Tailwind UI
│   └── src/
│       ├── pages/            Dashboard, Patients, New Consultation
│       ├── components/       Layout, ApiStatus
│       └── services/api.js   Axios client
├── docs/             Full planning docs (architecture, API spec, etc.)
└── docker-compose.yml  Qdrant vector DB
```

## Quick Start

### 1. Vector DB (Docker)
```bash
docker compose up -d        # starts Qdrant on :6333
```

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate         # Windows  (source venv/bin/activate on Unix)
pip install -r requirements.txt
copy .env.example .env        # then add your HF_API_TOKEN
python scripts/ingest_knowledge.py   # embed + index real PubMed docs into Qdrant
uvicorn app.main:app --reload
```
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

> The LLM uses the HuggingFace Inference API. MedGemma is not on the free
> serverless providers; the default is `meta-llama/Llama-3.1-8B-Instruct`
> (or `Qwen/Qwen2.5-7B-Instruct`). Without a token the app runs in a clearly
> labelled **mock mode** so it stays fully demoable.

### 3. Frontend
```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173
```
The Vite dev server proxies `/api/*` to the backend, so no CORS setup is
needed in development.

## Status

**Phase 1 (Foundation) — complete:** backend scaffold with FHIR schemas,
structured logging, global error handling, health check; React frontend with
routing, Tailwind UI, and a live API-status indicator.

**Phase 2 (RAG) — complete:** SQLAlchemy persistence (patients +
consultations), fastembed embeddings, Qdrant two-stage retrieval (dense + BM25
re-ranking), HuggingFace LLM service with graceful mock fallback, API-key auth,
and the full RAG consultation endpoint — grounded answers with citations,
confidence scoring, and uncertainty notes over **real PubMed literature**.

**Phase 3 (Frontend) — complete:** React UI wired to the live API — patient
management, the consultation RAG flow (assessment, evidence with DOI links,
confidence, uncertainty notes), and a semantic knowledge-search page.

**Phase 4 (Live RAG + Testing) — complete:** hybrid live multi-source retrieval
(PubMed / Europe PMC / ClinicalTrials.gov) with a credibility hard rule,
hardened LLM handling (consultations degrade gracefully — never 500), provider/
credibility badges in the UI, and an offline pytest suite.

**Next (Phase 5):** the Medium benchmark article from the working code.

See [`docs/PROJECT.md`](docs/PROJECT.md) for the full 8-week plan.

## Testing

```bash
cd backend
pytest -q        # offline suite: auth, validation, CRUD, RAG, credibility guard
```
