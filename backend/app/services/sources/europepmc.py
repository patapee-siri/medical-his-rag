"""Europe PMC provider via its REST search API.

Open, no API key. We restrict results to peer-reviewed sources (MED = MEDLINE,
PMC = PubMed Central) and explicitly exclude the preprint server (PPR) both in
the query and in code, per the credibility hard rule.
"""

from __future__ import annotations

import httpx

from app.config import settings
from app.services.sources.base import CREDIBILITY_PEER_REVIEWED, FetchedDoc
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_SEARCH_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
_PEER_REVIEWED_SRC = {"MED", "PMC"}  # never "PPR" (preprints)


class EuropePMCProvider:
    name = "europepmc"

    def __init__(self) -> None:
        self.enabled = settings.SOURCE_EUROPEPMC

    async def search(self, query: str, limit: int) -> list[FetchedDoc]:
        try:
            async with httpx.AsyncClient(timeout=settings.LIVE_TIMEOUT_SECONDS) as client:
                resp = await client.get(
                    _SEARCH_URL,
                    params={
                        # Restrict to peer-reviewed sources at the API level too.
                        "query": f"({query}) AND (SRC:MED OR SRC:PMC)",
                        "format": "json",
                        "pageSize": limit,
                        "resultType": "core",
                    },
                )
                resp.raise_for_status()
                results = resp.json().get("resultList", {}).get("result", [])
        except Exception as exc:  # noqa: BLE001
            logger.warning("europepmc_provider_failed", error=str(exc))
            return []

        docs: list[FetchedDoc] = []
        for r in results:
            src = r.get("source")
            text = (r.get("abstractText") or "").strip()
            # Hard guard: drop anything not from a peer-reviewed source.
            if src not in _PEER_REVIEWED_SRC or not text:
                continue

            doc_id = f"PMID:{r['pmid']}" if r.get("pmid") else f"EPMC:{r.get('id')}"
            doi = r.get("doi")
            year = r.get("pubYear")
            authors = [a.strip() for a in (r.get("authorString") or "").split(",") if a.strip()]

            docs.append(
                FetchedDoc(
                    doc_id=doc_id,
                    title=(r.get("title") or "Untitled").strip().rstrip("."),
                    text=text,
                    provider="europepmc",
                    credibility=CREDIBILITY_PEER_REVIEWED,
                    source_type="research_article",
                    url=f"https://doi.org/{doi}" if doi else None,
                    authors=authors[:6],
                    year=int(year) if year and str(year).isdigit() else None,
                )
            )
        return docs
