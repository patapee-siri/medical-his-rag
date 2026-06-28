"""Consultation (RAG) endpoints."""

from fastapi import APIRouter, Query, status

from app.dependencies import Consultations, RequireAuth
from app.schemas.consultation import (
    ConsultationHistoryResponse,
    ConsultationRequest,
    ConsultationResponse,
    ConsultationSummary,
)

router = APIRouter(
    prefix="/consultations",
    tags=["consultations"],
    dependencies=[RequireAuth],
)


@router.post(
    "",
    response_model=ConsultationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an AI-assisted consultation (RAG)",
)
async def create_consultation(
    payload: ConsultationRequest, service: Consultations
) -> ConsultationResponse:
    return await service.create(payload)


@router.get(
    "/detail/{consultation_id}",
    response_model=ConsultationResponse,
    summary="Get a single consultation",
)
def get_consultation(consultation_id: str, service: Consultations) -> ConsultationResponse:
    return ConsultationResponse.model_validate(service.get(consultation_id))


@router.get(
    "/{patient_id}",
    response_model=ConsultationHistoryResponse,
    summary="Get a patient's consultation history",
)
def consultation_history(
    patient_id: str,
    service: Consultations,
    limit: int = Query(10, ge=1, le=50),
) -> ConsultationHistoryResponse:
    rows = service.history(patient_id, limit=limit)
    return ConsultationHistoryResponse(
        patient_id=patient_id,
        total=len(rows),
        consultations=[ConsultationSummary.model_validate(r) for r in rows],
    )
