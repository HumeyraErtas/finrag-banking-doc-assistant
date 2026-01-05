from __future__ import annotations
import os
import numpy as np
import faiss


class FaissStore:
    """
    Maintains a FAISS index where vector_id corresponds to Chunk.vector_id in DB.
    We use IndexFlatIP on normalized embeddings => cosine similarity.
    """
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self._next_id = 0

    @property
    def ntotal(self) -> int:
        return self.index.ntotal

    def add(self, vectors: np.ndarray) -> list[int]:
        if vectors.dtype != np.float32:
            vectors = vectors.astype("float32")
        if vectors.ndim != 2 or vectors.shape[1] != self.dim:
            raise ValueError(f"Bad vectors shape: {vectors.shape}, expected (*, {self.dim})")

        ids = list(range(self._next_id, self._next_id + vectors.shape[0]))
        self.index.add(vectors)
        self._next_id += vectors.shape[0]
        return ids

    def search(self, query_vec: np.ndarray, top_k: int):
        if query_vec.ndim == 1:
            query_vec = query_vec.reshape(1, -1)
        if query_vec.dtype != np.float32:
            query_vec = query_vec.astype("float32")
        scores, idxs = self.index.search(query_vec, top_k)
        return scores[0].tolist(), idxs[0].tolist()

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        faiss.write_index(self.index, path)

    @classmethod
    def load(cls, path: str) -> "FaissStore":
        index = faiss.read_index(path)
        dim = index.d
        obj = cls(dim)
        obj.index = index
        obj._next_id = index.ntotal
        return obj
