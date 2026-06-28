"""Health-check endpoint with real component probes (DB, Qdrant, LLM)."""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app import __version__
from app.db.session import engine
from app.dependencies import get_llm_service, get_vector_store

router = APIRouter(tags=["health"])


class ComponentStatus(BaseModel):
    api: str = "ok"
    database: str
    vector_db: str
    llm: str


class HealthResponse(BaseModel):
    status: str
    version: str
    components: ComponentStatus
    timestamp: datetime


def _check_database() -> str:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok"
    except Exception:  # noqa: BLE001
        return "error"


@router.get("/health", response_model=HealthResponse, summary="Service health check")
async def health_check() -> HealthResponse:
    db_status = _check_database()
    vector_status = "ok" if get_vector_store().ping() else "error"
    llm_status = "ready" if get_llm_service().is_configured else "mock"

    overall = "healthy" if db_status == "ok" and vector_status == "ok" else "degraded"

    return HealthResponse(
        status=overall,
        version=__version__,
        components=ComponentStatus(
            database=db_status,
            vector_db=vector_status,
            llm=llm_status,
        ),
        timestamp=datetime.now(timezone.utc),
    )
