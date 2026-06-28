"""SQLAlchemy ORM models for patients and consultations.

Structured fields (vital signs, sources, etc.) are stored as JSON columns so
the relational schema stays simple while preserving the rich FHIR-style data.
"""

from datetime import date, datetime, timezone

from sqlalchemy import JSON, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # Lists of dicts (conditions / allergies) kept as JSON.
    medical_history: Mapped[list] = mapped_column(JSON, default=list)
    allergies: Mapped[list] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    consultations: Mapped[list["Consultation"]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan",
        order_by="desc(Consultation.created_at)",
    )


class Consultation(Base):
    __tablename__ = "consultations"

    consultation_id: Mapped[str] = mapped_column(String(40), primary_key=True)
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.patient_id", ondelete="CASCADE"), index=True
    )

    chief_complaint: Mapped[str] = mapped_column(Text, nullable=False)
    vital_signs: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    additional_symptoms: Mapped[list] = mapped_column(JSON, default=list)

    ai_assessment: Mapped[str] = mapped_column(Text, default="")
    sources: Mapped[list] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(default=0.5)
    uncertainty_notes: Mapped[list] = mapped_column(JSON, default=list)
    model_used: Mapped[str | None] = mapped_column(String(120), nullable=True)
    processing_time_ms: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    patient: Mapped["Patient"] = relationship(back_populates="consultations")
