"""FastAPI application entry point for the Medical HIS RAG backend.

Wires together configuration, structured logging, CORS, global exception
handling, and the API routers. Run locally with:

    uvicorn app.main:app --reload
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import settings
from app.db.session import init_db
from app.routers import consultations, health, knowledge, patients
from app.utils.exceptions import register_exception_handlers
from app.utils.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown hooks: ensure the DB schema exists on boot."""
    init_db()
    logger.info(
        "startup",
        version=__version__,
        env=settings.APP_ENV,
        model=settings.HF_MODEL_ID,
        embedding_model=settings.EMBEDDING_MODEL,
    )
    yield
    logger.info("shutdown")


app = FastAPI(
    title="Medical HIS API",
    version=__version__,
    description=(
        "Healthcare Information System with Retrieval-Augmented Generation. "
        "Provides patient management and AI-assisted clinical consultation "
        "grounded in medical literature."
    ),
    lifespan=lifespan,
)

# --- CORS (allow the React dev server to call the API) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_timing_middleware(request: Request, call_next):
    """Log each request with its method, path, status, and duration."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(duration_ms)
    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    return response


# --- Global error handling ---
register_exception_handlers(app)

# --- Routers ---
app.include_router(health.router)
app.include_router(patients.router)
app.include_router(consultations.router)
app.include_router(knowledge.router)


@app.get("/", tags=["root"], summary="API root")
async def root() -> dict:
    """Friendly landing payload with links to docs and health."""
    return {
        "name": "Medical HIS API",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }
