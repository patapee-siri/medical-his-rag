"""PubMed provider via NCBI E-utilities (esearch + efetch).

Peer-reviewed biomedical literature. No API key required, though one raises the
rate limit; pass it via ``settings.NCBI_API_KEY``.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx

from app.config import settings
from app.services.sources.base import CREDIBILITY_PEER_REVIEWED, FetchedDoc
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


class PubMedProvider:
    name = "pubmed"

    def __init__(self) -> None:
        self.enabled = settings.SOURCE_PUBMED
        self._api_key = settings.NCBI_API_KEY or None

    def _params(self, extra: dict) -> dict:
        params = dict(extra)
        if self._api_key:
            params["api_key"] = self._api_key
        return params

    async def search(self, query: str, limit: int) -> list[FetchedDoc]:
        try:
            async with httpx.AsyncClient(timeout=settings.LIVE_TIMEOUT_SECONDS) as client:
                ids = await self._esearch(client, query, limit)
                if not ids:
                    return []
                return await self._efetch(client, ids)
        except Exception as exc:  # noqa: BLE001 - provider must never break a request
            logger.warning("pubmed_provider_failed", error=str(exc))
            return []

    async def _esearch(self, client: httpx.AsyncClient, query: str, limit: int) -> list[str]:
        resp = await client.get(
            f"{_EUTILS}/esearch.fcgi",
            params=self._params(
                {
                    "db": "pubmed",
                    "term": query,
                    "retmax": limit,
                    "retmode": "json",
                    "sort": "relevance",
                }
            ),
        )
        resp.raise_for_status()
        return resp.json().get("esearchresult", {}).get("idlist", [])

    async def _efetch(self, client: httpx.AsyncClient, ids: list[str]) -> list[FetchedDoc]:
        resp = await client.get(
            f"{_EUTILS}/efetch.fcgi",
            params=self._params({"db": "pubmed", "id": ",".join(ids), "retmode": "xml"}),
        )
        resp.raise_for_status()
        return self._parse(resp.text)

    @staticmethod
    def _parse(xml_text: str) -> list[FetchedDoc]:
        root = ET.fromstring(xml_text)
        docs: list[FetchedDoc] = []
        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//MedlineCitation/PMID")
            title = article.findtext(".//Article/ArticleTitle") or "Untitled"

            # Abstracts may be split into multiple labelled segments.
            segments = [
                (el.text or "").strip()
                for el in article.findall(".//Abstract/AbstractText")
            ]
            text = " ".join(s for s in segments if s)
            if not pmid or not text:
                continue

            authors = []
            for author in article.findall(".//AuthorList/Author"):
                last = author.findtext("LastName")
                initials = author.findtext("Initials")
                if last:
                    authors.append(f"{last} {initials}".strip())

            year = article.findtext(".//Journal/JournalIssue/PubDate/Year")
            doi = None
            for aid in article.findall(".//ArticleIdList/ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = aid.text
                    break

            docs.append(
                FetchedDoc(
                    doc_id=f"PMID:{pmid}",
                    title=title.strip(),
                    text=text,
                    provider="pubmed",
                    credibility=CREDIBILITY_PEER_REVIEWED,
                    source_type="research_article",
                    url=f"https://doi.org/{doi}" if doi else f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    authors=authors[:6],
                    year=int(year) if year and year.isdigit() else None,
                )
            )
        return docs
