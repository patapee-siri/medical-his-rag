"""Consultation service — orchestrates the RAG pipeline.

retrieve evidence → assemble a grounded prompt → call the LLM → derive a
confidence score and uncertainty notes → persist and return the result. The
LLM step degrades gracefully: if the provider is unavailable the consultation
still returns the retrieved evidence with a clear note instead of failing.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import Consultation
from app.schemas.consultation import ConsultationRequest, ConsultationResponse, Source
from app.services.llm import ChatMessage, LLMService
from app.services.patients import PatientService
from app.services.retrieval import RetrievalService, RetrievedSource
from app.utils.exceptions import ServiceUnavailableError
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = (
    "You are a clinical decision-support assistant for licensed healthcare "
    "professionals. Use ONLY the provided medical literature as evidence. "
    "Provide a concise assessment, a short differential, and recommended next "
    "steps. Cite sources by their [n] index. If the evidence is insufficient, "
    "say so explicitly. Never fabricate facts or citations. This is decision "
    "support, not a final diagnosis."
)

_MAX_CONFIDENCE = 0.95


def _generate_consultation_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:6].upper()
    return f"C-{stamp}-{suffix}"


def _build_context_block(sources: list[RetrievedSource]) -> str:
    if not sources:
        return "No relevant medical literature was retrieved."
    lines = []
    for i, s in enumerate(sources, start=1):
        meta = s.source_type.replace("_", " ")
        if s.year:
            meta += f", {s.year}"
        lines.append(f"[{i}] {s.title} ({meta})\n{s.excerpt}")
    return "\n\n".join(lines)


def _build_user_message(req: ConsultationRequest, context: str) -> str:
    parts = [f"Chief complaint: {req.chief_complaint}"]
    if req.vital_signs:
        vs = req.vital_signs
        parts.append(
            "Vital signs: BP {bp}, HR {hr}, Temp {t}°C, RR {rr}, SpO2 {o2}%".format(
                bp=vs.blood_pressure,
                hr=vs.heart_rate,
                t=vs.temperature_celsius,
                rr=vs.respiratory_rate,
                o2=vs.oxygen_saturation,
            )
        )
    if req.additional_symptoms:
        parts.append("Additional symptoms: " + ", ".join(req.additional_symptoms))
    if req.current_medications:
        parts.append("Current medications: " + ", ".join(req.current_medications))
    parts.append("\nRetrieved medical literature:\n" + context)
    parts.append(
        "\nProvide your assessment, differential, and next steps, citing [n]."
    )
    return "\n".join(parts)


def _confidence(sources: list[RetrievedSource], *, degraded: bool, mock: bool) -> float:
    if not sources:
        base = 0.3
    else:
        base = sum(s.relevance_score for s in sources) / len(sources)
    if degraded:
        base *= 0.5
    if mock:
        base = min(base, 0.4)
    return round(min(base, _MAX_CONFIDENCE), 3)


def _uncertainty_notes(
    sources: list[RetrievedSource], *, degraded: bool, mock: bool
) -> list[str]:
    notes: list[str] = []
    if mock:
        notes.append("Assessment generated in mock mode (no LLM configured).")
    if degraded:
        notes.append("LLM provider was unavailable; based on retrieved evidence only.")
    if not sources:
        notes.append("No supporting literature retrieved for this query.")
    elif len(sources) < 3:
        notes.append("Limited supporting evidence retrieved.")
    notes.append("Findings require verification by a licensed clinician.")
    return notes


class ConsultationService:
    def __init__(
        self,
        db: Session,
        retrieval: RetrievalService,
        llm: LLMService,
    ):
        self.db = db
        self.retrieval = retrieval
        self.llm = llm
        self.patients = PatientService(db)

    async def create(self, req: ConsultationRequest) -> ConsultationResponse:
        started = datetime.now(timezone.utc)

        # Validate the patient exists (raises NotFoundError otherwise).
        self.patients.get(req.patient_id)

        query = req.chief_complaint
        if req.additional_symptoms:
            query += " " + " ".join(req.additional_symptoms)
        sources, _augmented = await self.retrieval.retrieve_hybrid(query)

        context = _build_context_block(sources)
        messages = [
            ChatMessage(role="system", content=_SYSTEM_PROMPT),
            ChatMessage(role="user", content=_build_user_message(req, context)),
        ]

        degraded = False
        is_mock = False
        model_used = self.llm.model_id
        try:
            result = await self.llm.generate(messages)
            assessment, model_used, is_mock = result.text, result.model, result.is_mock
        except ServiceUnavailableError:
            degraded = True
            assessment = (
                "The language model is currently unavailable. Below are the most "
                "relevant retrieved sources for clinician review."
            )
        except Exception as exc:  # noqa: BLE001 - never let a consultation 500
            logger.error("consultation_llm_unexpected_error", error=str(exc))
            degraded = True
            assessment = (
                "An unexpected error occurred while generating the assessment. "
                "Below are the most relevant retrieved sources for clinician review."
            )

        confidence = _confidence(sources, degraded=degraded, mock=is_mock)
        notes = _uncertainty_notes(sources, degraded=degraded, mock=is_mock)

        elapsed_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)

        response_sources = [
            Source(
                doc_id=s.doc_id,
                title=s.title,
                excerpt=s.excerpt,
                relevance_score=s.relevance_score,
                source_type=s.source_type,
                url=s.url,
                provider=s.provider,
                credibility=s.credibility,
            )
            for s in sources
        ]

        consultation_id = _generate_consultation_id()
        self._persist(consultation_id, req, assessment, response_sources, confidence, notes, model_used, elapsed_ms)

        return ConsultationResponse(
            consultation_id=consultation_id,
            patient_id=req.patient_id,
            chief_complaint=req.chief_complaint,
            ai_assessment=assessment,
            sources=response_sources,
            confidence=confidence,
            uncertainty_notes=notes,
            model_used=model_used,
            processing_time_ms=elapsed_ms,
            created_at=started,
        )

    def _persist(
        self,
        consultation_id: str,
        req: ConsultationRequest,
        assessment: str,
        sources: list[Source],
        confidence: float,
        notes: list[str],
        model_used: str | None,
        elapsed_ms: int,
    ) -> None:
        row = Consultation(
            consultation_id=consultation_id,
            patient_id=req.patient_id,
            chief_complaint=req.chief_complaint,
            vital_signs=req.vital_signs.model_dump(mode="json") if req.vital_signs else None,
            additional_symptoms=req.additional_symptoms,
            ai_assessment=assessment,
            sources=[s.model_dump(mode="json") for s in sources],
            confidence=confidence,
            uncertainty_notes=notes,
            model_used=model_used,
            processing_time_ms=elapsed_ms,
        )
        self.db.add(row)
        self.db.commit()

    def history(self, patient_id: str, limit: int = 10) -> list[Consultation]:
        self.patients.get(patient_id)  # ensures patient exists
        return (
            self.db.query(Consultation)
            .filter(Consultation.patient_id == patient_id)
            .order_by(Consultation.created_at.desc())
            .limit(limit)
            .all()
        )

    def get(self, consultation_id: str) -> Consultation:
        from app.utils.exceptions import NotFoundError

        row = self.db.get(Consultation, consultation_id)
        if row is None:
            raise NotFoundError(f"Consultation '{consultation_id}' not found")
        return row
