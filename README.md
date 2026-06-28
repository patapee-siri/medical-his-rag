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
| LLM | HuggingFace Inference API (MedGemma-7B) |
| Vector DB | Qdrant (Docker) |
| Database | SQLite |
| Standards | FHIR-inspired schemas |

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
uvicorn app.main:app --reload
```
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

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

**Next (Phase 2):** patient CRUD, Qdrant retrieval, HuggingFace LLM
integration, and the consultation endpoint.

See [`docs/PROJECT.md`](docs/PROJECT.md) for the full 8-week plan.
