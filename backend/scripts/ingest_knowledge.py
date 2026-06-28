"""Ingest the medical knowledge base into Qdrant.

Reads ``data/knowledge_base.json`` (real PubMed abstracts), embeds each
document with fastembed, and upserts the vectors into the Qdrant collection.

Run from the backend directory:

    python scripts/ingest_knowledge.py
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

# Allow "import app.*" when run as a plain script from the backend dir.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings  # noqa: E402
from app.services.embeddings import EmbeddingService  # noqa: E402
from app.services.vector_store import Document, VectorStore  # noqa: E402

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "knowledge_base.json"


def load_documents() -> list[Document]:
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    docs: list[Document] = []
    for item in raw["documents"]:
        docs.append(
            Document(
                doc_id=item["doc_id"],
                title=html.unescape(item["title"]),
                text=html.unescape(item["text"]),
                source_type=item.get("source_type", "research_article"),
                url=item.get("url"),
                authors=item.get("authors"),
                year=item.get("year"),
                # Curated seed corpus: hand-picked peer-reviewed literature.
                provider=item.get("provider", "curated"),
                credibility=item.get("credibility", "peer_reviewed"),
            )
        )
    return docs


def main() -> None:
    print(f"Loading documents from {DATA_FILE.name} …")
    documents = load_documents()
    print(f"  {len(documents)} documents loaded.")

    embeddings = EmbeddingService()
    store = VectorStore()

    print(f"Ensuring Qdrant collection '{settings.QDRANT_COLLECTION}' "
          f"(dim={embeddings.dimension}) …")
    store.ensure_collection(embeddings.dimension)

    print(f"Embedding with {settings.EMBEDDING_MODEL} (first run downloads the model) …")
    texts = [f"{d.title}. {d.text}" for d in documents]
    vectors = embeddings.embed_documents(texts)

    print("Upserting into Qdrant …")
    count = store.upsert(documents, vectors)

    total = store.count()
    print(f"Done. Upserted {count} documents. Collection now holds {total} points.")


if __name__ == "__main__":
    main()
