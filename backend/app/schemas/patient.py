"""Patient-related schemas (FHIR-inspired Patient + Observation concepts).

Vital signs include validation bounds so that physiologically impossible
values are rejected at the API boundary.
"""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    unknown = "unknown"


class VitalSigns(BaseModel):
    """A snapshot of patient vital signs (FHIR Observation-like)."""

    blood_pressure: str = Field(
        ...,
        examples=["120/80"],
        description="Systolic/diastolic in mmHg, e.g. '120/80'.",
    )
    heart_rate: int = Field(..., ge=20, le=300, description="Beats per minute")
    temperature_celsius: float = Field(..., ge=25.0, le=45.0)
    respiratory_rate: int = Field(..., ge=4, le=80, description="Breaths per minute")
    oxygen_saturation: float = Field(
        ..., ge=50.0, le=100.0, description="SpO2 percentage"
    )

    @field_validator("blood_pressure")
    @classmethod
    def validate_bp(cls, v: str) -> str:
        parts = v.split("/")
        if len(parts) != 2:
            raise ValueError("blood_pressure must look like 'systolic/diastolic'")
        try:
            systolic, diastolic = int(parts[0]), int(parts[1])
        except ValueError as exc:
            raise ValueError("blood_pressure values must be integers") from exc
        if not (40 <= systolic <= 300) or not (20 <= diastolic <= 200):
            raise ValueError("blood_pressure values out of physiological range")
        if diastolic >= systolic:
            raise ValueError("diastolic must be lower than systolic")
        return v


class MedicalHistoryItem(BaseModel):
    condition: str
    onset_date: date | None = None
    status: str = Field(default="active", examples=["active", "resolved"])


class Allergy(BaseModel):
    substance: str
    reaction: str | None = None


class PatientCreate(BaseModel):
    """Payload for creating a patient."""

    name: str = Field(..., min_length=1, max_length=200)
    date_of_birth: date
    gender: Gender
    email: str | None = None
    phone: str | None = None
    medical_history: list[MedicalHistoryItem] = Field(default_factory=list)
    allergies: list[Allergy] = Field(default_factory=list)


class PatientResponse(BaseModel):
    """Patient resource returned by the API."""

    patient_id: str
    resource_type: str = "Patient"
    name: str
    date_of_birth: date
    gender: Gender
    email: str | None = None
    phone: str | None = None
    medical_history: list[MedicalHistoryItem] = Field(default_factory=list)
    allergies: list[Allergy] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}


class PatientSummary(BaseModel):
    """Compact patient representation for list endpoints."""

    patient_id: str
    name: str
    gender: Gender
    date_of_birth: date

    model_config = {"from_attributes": True}


class PatientListResponse(BaseModel):
    total: int
    page: int
    limit: int
    results: list[PatientSummary]
