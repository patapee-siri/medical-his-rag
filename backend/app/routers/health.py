"""Health-check endpoints.

Reports liveness plus a best-effort status of downstream components. In this
Week 1-2 foundation, vector DB / LLM checks are placeholders ("pending") and
will be wired to real connectivity probes in Phase 2.
"""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app import __version__

router = APIRouter(tags=["health"])


class ComponentStatus(BaseModel):
    api: str = "ok"
    database: str = "pending"
    vector_db: str = "pending"
    llm: str = "pending"


class HealthResponse(BaseModel):
    status: str
    version: str
    components: ComponentStatus
    timestamp: datetime


@router.get("/health", response_model=HealthResponse, summary="Service health check")
async def health_check() -> HealthResponse:
    """Return overall service health and per-component status."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        components=ComponentStatus(),
        timestamp=datetime.now(timezone.utc),
    )
