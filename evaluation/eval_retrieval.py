from __future__ import annotations

import os
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app.embeddings import Embedder
from app.faiss_index import FaissStore
from app.retriever import Retriever
from app.models import RetrievalGold


def parse_ids(csv: str) -> set[int]:
    return set(int(x.strip()) for x in csv.split(",") if x.strip())


def precision_recall_at_k(retrieved_ids: list[int], relevant_ids: set[int], k: int):
    topk = retrieved_ids[:k]
    if not topk:
        return 0.0, 0.0
    hits = sum(1 for x in topk if x in relevant_ids)
    precision = hits / len(topk)
    recall = hits / max(1, len(relevant_ids))
    return precision, recall


def main():
    if not os.path.exists(settings.faiss_index_path):
        raise RuntimeError("FAISS index not found. Run ingest first.")

    db: Session = SessionLocal()
    try:
        gold = db.query(RetrievalGold).all()
        if not gold:
            print("No evaluation data found in retrieval_gold table.")
            print("Insert rows: query + relevant_chunk_ids_csv (e.g., '12,15,88')")
            return

        embedder = Embedder()
        store = FaissStore.load(settings.faiss_index_path)
        retriever = Retriever(db=db, embedder=embedder, store=store)

        ks = [1, 3, 5, 10]
        totals = {k: {"p": 0.0, "r": 0.0} for k in ks}

        for row in gold:
            rel = parse_ids(row.relevant_chunk_ids_csv)
            ctxs = retriever.retrieve(row.query, top_k=max(ks))
            retrieved_chunk_ids = [c.chunk_id for c in ctxs]

            for k in ks:
                p, r = precision_recall_at_k(retrieved_chunk_ids, rel, k)
                totals[k]["p"] += p
                totals[k]["r"] += r

        n = len(gold)
        print(f"Eval samples: {n}")
        for k in ks:
            print(f"precision@{k}: {totals[k]['p']/n:.4f} | recall@{k}: {totals[k]['r']/n:.4f}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
