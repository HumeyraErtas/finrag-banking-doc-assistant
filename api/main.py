from __future__ import annotations

import os
from fastapi import FastAPI, Depends
from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_session, engine, Base
from app.embeddings import Embedder
from app.faiss_index import FaissStore
from app.retriever import Retriever
from app.llm import build_llm
from app.rag import RAG
from functools import lru_cache


app = FastAPI(title="FinRAG Banking Doc Assistant", version="1.0.0")


class AskRequest(BaseModel):
    question: str


class CitationOut(BaseModel):
    chunk_id: int
    source_path: str
    title: str
    page_start: int
    page_end: int
    score: float
    snippet: str


class AskResponse(BaseModel):
    answer: str
    idk: bool
    top_score: float | None
    citations: list[CitationOut]


@app.on_event("startup")
def startup():
    os.makedirs(settings.data_dir, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def build_rag(db: Session) -> RAG:
    if not os.path.exists(settings.faiss_index_path):
        raise RuntimeError(
            f"FAISS index not found at {settings.faiss_index_path}. Run: python scripts/ingest_cli.py"
        )
    embedder = Embedder()
    store = FaissStore.load(settings.faiss_index_path)
    retriever = Retriever(db=db, embedder=embedder, store=store)
    llm = build_llm()
    return RAG(retriever=retriever, llm=llm)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest, db: Session = Depends(get_session)):
    rag = build_rag(db)
    res = rag.answer(req.question)

    return AskResponse(
        answer=res.answer,
        idk=res.idk,
        top_score=res.top_score,
        citations=[
            CitationOut(
                chunk_id=c.chunk_id,
                source_path=c.source_path,
                title=c.title,
                page_start=c.page_start,
                page_end=c.page_end,
                score=c.score,
                snippet=c.snippet,
            )
            for c in res.citations
        ],
    )

@lru_cache(maxsize=1)
def _cached_components():
    if not os.path.exists(settings.faiss_index_path):
        raise RuntimeError(
            f"FAISS index not found at {settings.faiss_index_path}. Run: python scripts/ingest_cli.py"
        )
    embedder = Embedder()
    store = FaissStore.load(settings.faiss_index_path)
    llm = build_llm()
    return embedder, store, llm

def build_rag(db: Session) -> RAG:
    embedder, store, llm = _cached_components()
    retriever = Retriever(db=db, embedder=embedder, store=store)
    return RAG(retriever=retriever, llm=llm)
