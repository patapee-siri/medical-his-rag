"""FastAPI dependency providers and API-key authentication.

Expensive, stateless services (embedding model, Qdrant client) are cached as
process singletons; per-request services (DB session, consultation service)
are created fresh each call.
"""

from __future__ import annotations

import secrets
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.services.consultations import ConsultationService
from app.services.embeddings import EmbeddingService
from app.services.llm import LLMService
from app.services.patients import PatientService
from app.services.retrieval import RetrievalService
from app.services.vector_store import VectorStore
from app.utils.exceptions import HISException

_bearer = HTTPBearer(auto_error=True)


class UnauthorizedError(HISException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "UNAUTHORIZED"


def verify_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(_bearer)],
) -> None:
    """Validate the Bearer token against the configured API key."""
    if not secrets.compare_digest(credentials.credentials, settings.API_KEY):
        raise UnauthorizedError("Invalid or missing API key")


# --- cached singletons ---
@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()


@lru_cache
def get_vector_store() -> VectorStore:
    return VectorStore()


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService()


# --- per-request services ---
def get_retrieval_service() -> RetrievalService:
    return RetrievalService(get_embedding_service(), get_vector_store())


def get_patient_service(db: Annotated[Session, Depends(get_db)]) -> PatientService:
    return PatientService(db)


def get_consultation_service(
    db: Annotated[Session, Depends(get_db)],
) -> ConsultationService:
    return ConsultationService(
        db=db,
        retrieval=get_retrieval_service(),
        llm=get_llm_service(),
    )


# Convenience aliases for route signatures.
RequireAuth = Depends(verify_api_key)
DbSession = Annotated[Session, Depends(get_db)]
Patients = Annotated[PatientService, Depends(get_patient_service)]
Consultations = Annotated[ConsultationService, Depends(get_consultation_service)]
