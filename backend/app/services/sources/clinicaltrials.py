"""ClinicalTrials.gov provider via the v2 REST API.

An authoritative NIH registry (credibility tier ``clinical_registry``). We build
a searchable text blob from the brief summary, conditions, and interventions.
"""

from __future__ import annotations

import httpx

from app.config import settings
from app.services.sources.base import CREDIBILITY_CLINICAL_REGISTRY, FetchedDoc
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_STUDIES_URL = "https://clinicaltrials.gov/api/v2/studies"


class ClinicalTrialsProvider:
    name = "clinicaltrials"

    def __init__(self) -> None:
        self.enabled = settings.SOURCE_CLINICALTRIALS

    async def search(self, query: str, limit: int) -> list[FetchedDoc]:
        try:
            async with httpx.AsyncClient(timeout=settings.LIVE_TIMEOUT_SECONDS) as client:
                resp = await client.get(
                    _STUDIES_URL,
                    params={"query.term": query, "pageSize": limit, "format": "json"},
                )
                resp.raise_for_status()
                studies = resp.json().get("studies", [])
        except Exception as exc:  # noqa: BLE001
            logger.warning("clinicaltrials_provider_failed", error=str(exc))
            return []

        docs: list[FetchedDoc] = []
        for study in studies:
            ps = study.get("protocolSection", {})
            ident = ps.get("identificationModule", {})
            nct = ident.get("nctId")
            title = ident.get("briefTitle") or ident.get("officialTitle") or "Untitled trial"

            summary = ps.get("descriptionModule", {}).get("briefSummary", "")
            conditions = ps.get("conditionsModule", {}).get("conditions", [])
            interventions = [
                i.get("name", "")
                for i in ps.get("armsInterventionsModule", {}).get("interventions", [])
            ]
            parts = [summary]
            if conditions:
                parts.append("Conditions: " + ", ".join(conditions))
            if interventions:
                parts.append("Interventions: " + ", ".join(i for i in interventions if i))
            text = "\n".join(p for p in parts if p).strip()

            if not nct or not text:
                continue

            year = None
            start = ps.get("statusModule", {}).get("startDateStruct", {}).get("date", "")
            if start[:4].isdigit():
                year = int(start[:4])

            docs.append(
                FetchedDoc(
                    doc_id=f"NCT:{nct}",
                    title=title.strip(),
                    text=text,
                    provider="clinicaltrials",
                    credibility=CREDIBILITY_CLINICAL_REGISTRY,
                    source_type="clinical_trial",
                    url=f"https://clinicaltrials.gov/study/{nct}",
                    authors=[],
                    year=year,
                )
            )
        return docs
