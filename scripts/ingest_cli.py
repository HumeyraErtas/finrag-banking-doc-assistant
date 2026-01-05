from __future__ import annotations

import os
import glob
from tqdm import tqdm

from sqlalchemy.orm import Session

from app.config import settings
from app.db import engine, SessionLocal, Base
from app.models import Document, Chunk
from app.pdf_reader import read_pdf_pages
from app.chunking import chunk_pages
from app.embeddings import Embedder
from app.faiss_index import FaissStore


def ensure_db():
    os.makedirs(settings.data_dir, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def load_or_create_store(embedder: Embedder) -> FaissStore:
    if os.path.exists(settings.faiss_index_path):
        return FaissStore.load(settings.faiss_index_path)
    return FaissStore(embedder.dim())


def ingest_pdf(db: Session, store: FaissStore, embedder: Embedder, pdf_path: str, title: str = ""):
    pdf_path = os.path.abspath(pdf_path)

    existing = db.query(Document).filter(Document.source_path == pdf_path).first()
    if existing:
        # Simple strategy: skip if already ingested
        return

    pages = read_pdf_pages(pdf_path)
    tuples = [(p.page_number, p.text) for p in pages]
    chunks = chunk_pages(tuples, chunk_size=900, overlap=150)

    if not chunks:
        return

    doc = Document(source_path=pdf_path, title=title or os.path.basename(pdf_path))
    db.add(doc)
    db.flush()  # get doc.id

    texts = [c.text for c in chunks]
    vecs = embedder.encode(texts)
    vector_ids = store.add(vecs)

    for c, vid in zip(chunks, vector_ids):
        row = Chunk(
            document_id=doc.id,
            chunk_index=c.chunk_index,
            page_start=c.page_start,
            page_end=c.page_end,
            text=c.text,
            vector_id=vid,
        )
        db.add(row)

    db.commit()


def main():
    ensure_db()
    embedder = Embedder()
    store = load_or_create_store(embedder)

    # Ingest PDFs from DATA_DIR/pdfs by default
    pdf_dir = os.path.join(settings.data_dir, "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)

    pdfs = sorted(glob.glob(os.path.join(pdf_dir, "*.pdf")))
    if not pdfs:
        print(f"No PDFs found in: {pdf_dir}")
        print("Put your banking documents as PDF files into that folder and re-run.")
        return

    db = SessionLocal()
    try:
        for p in tqdm(pdfs, desc="Ingesting PDFs"):
            ingest_pdf(db, store, embedder, p)
    finally:
        db.close()

    store.save(settings.faiss_index_path)
    print(f"Done. FAISS index saved to: {settings.faiss_index_path}")


if __name__ == "__main__":
    main()
