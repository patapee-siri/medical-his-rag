"""Consultation schemas: the RAG query input and the AI assessment output.

These mirror the response shape documented in docs/API_SPECIFICATION.md
(simplified for the Week 1-2 foundation; expanded in later phases).
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.patient import VitalSigns


class ConsultationRequest(BaseModel):
    """A clinical query for the RAG system."""

    patient_id: str
    chief_complaint: str = Field(..., min_length=3, max_length=2000)
    vital_signs: VitalSigns | None = None
    additional_symptoms: list[str] = Field(default_factory=list)
    current_medications: list[str] = Field(default_factory=list)
    model_preference: str | None = Field(
        default=None,
        description="Optional override of the configured LLM model id.",
    )


class Source(BaseModel):
    """A retrieved evidence document backing the assessment."""

    doc_id: str
    title: str
    excerpt: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    source_type: str = "unknown"
    url: str | None = None


class ConsultationResponse(BaseModel):
    """The AI-assisted assessment returned to the clinician."""

    consultation_id: str
    patient_id: str
    chief_complaint: str
    ai_assessment: str
    sources: list[Source] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    uncertainty_notes: list[str] = Field(default_factory=list)
    model_used: str | None = None
    processing_time_ms: int = 0
    created_at: datetime
    disclaimer: str = (
        "AI-assisted decision support only. Not a substitute for professional "
        "medical judgment. All recommendations must be reviewed by a licensed "
        "healthcare provider."
    )
