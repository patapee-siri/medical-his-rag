"""Patient management endpoints."""

from fastapi import APIRouter, Query, status

from app.dependencies import Patients, RequireAuth
from app.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientSummary,
)

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
    dependencies=[RequireAuth],
)


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a patient",
)
def create_patient(payload: PatientCreate, service: Patients) -> PatientResponse:
    patient = service.create(payload)
    return PatientResponse.model_validate(patient)


@router.get("/{patient_id}", response_model=PatientResponse, summary="Get a patient")
def get_patient(patient_id: str, service: Patients) -> PatientResponse:
    return PatientResponse.model_validate(service.get(patient_id))


@router.get("", response_model=PatientListResponse, summary="List / search patients")
def list_patients(
    service: Patients,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
) -> PatientListResponse:
    patients, total = service.list(page=page, limit=limit, search=search)
    return PatientListResponse(
        total=total,
        page=page,
        limit=limit,
        results=[PatientSummary.model_validate(p) for p in patients],
    )
