from __future__ import annotations
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.embeddings import Embedder
from app.faiss_index import FaissStore
from app.models import Chunk, Document
from app.config import settings


@dataclass
class Retrieved:
    score: float
    chunk_id: int
    source_path: str
    title: str
    page_start: int
    page_end: int
    text: str


class Retriever:
    def __init__(self, db: Session, embedder: Embedder, store: FaissStore):
        self.db = db
        self.embedder = embedder
        self.store = store

    def retrieve(self, query: str, top_k: int | None = None) -> list[Retrieved]:
        k = top_k or settings.top_k
        qv = self.embedder.encode([query])[0]
        scores, vector_ids = self.store.search(qv, k)

        # Filter invalid ids (FAISS can return -1 if empty)
        pairs = [(s, vid) for s, vid in zip(scores, vector_ids) if vid is not None and vid >= 0]
        if not pairs:
            return []

        # Fetch chunks by vector_id
        vids = [vid for _, vid in pairs]
        rows = (
            self.db.query(Chunk, Document)
            .join(Document, Document.id == Chunk.document_id)
            .filter(Chunk.vector_id.in_(vids))
            .all()
        )

        by_vid = {}
        for ch, doc in rows:
            by_vid[ch.vector_id] = (ch, doc)

        out: list[Retrieved] = []
        for score, vid in pairs:
            if vid not in by_vid:
                continue
            ch, doc = by_vid[vid]
            out.append(
                Retrieved(
                    score=float(score),
                    chunk_id=ch.id,
                    source_path=doc.source_path,
                    title=doc.title or "",
                    page_start=ch.page_start,
                    page_end=ch.page_end,
                    text=ch.text,
                )
            )
        return out
