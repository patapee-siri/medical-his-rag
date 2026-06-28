"""Patient domain service (repository pattern over SQLAlchemy).

Generates human-readable patient IDs, persists records, and provides
paginated search. All DB access for patients lives here so routers stay thin.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models import Patient
from app.schemas.patient import PatientCreate
from app.utils.exceptions import NotFoundError


def _generate_patient_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = uuid.uuid4().hex[:6].upper()
    return f"P-{stamp}-{suffix}"


class PatientService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: PatientCreate) -> Patient:
        patient = Patient(
            patient_id=_generate_patient_id(),
            name=data.name,
            date_of_birth=data.date_of_birth,
            gender=data.gender.value,
            email=data.email,
            phone=data.phone,
            medical_history=[item.model_dump(mode="json") for item in data.medical_history],
            allergies=[a.model_dump(mode="json") for a in data.allergies],
        )
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def get(self, patient_id: str) -> Patient:
        patient = self.db.get(Patient, patient_id)
        if patient is None:
            raise NotFoundError(f"Patient '{patient_id}' not found")
        return patient

    def list(
        self, page: int = 1, limit: int = 20, search: str | None = None
    ) -> tuple[list[Patient], int]:
        page = max(page, 1)
        limit = max(min(limit, 100), 1)

        stmt = select(Patient)
        count_stmt = select(func.count()).select_from(Patient)

        if search:
            pattern = f"%{search}%"
            condition = or_(
                Patient.name.ilike(pattern),
                Patient.patient_id.ilike(pattern),
            )
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        total = self.db.execute(count_stmt).scalar_one()
        rows = (
            self.db.execute(
                stmt.order_by(Patient.created_at.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )
            .scalars()
            .all()
        )
        return list(rows), total
