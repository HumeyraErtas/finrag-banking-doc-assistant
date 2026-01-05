from __future__ import annotations
from sentence_transformers import SentenceTransformer
import numpy as np
from app.config import settings


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)

    def encode(self, texts: list[str]) -> np.ndarray:
        vecs = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,  # cosine similarity via dot product
        )
        return vecs.astype("float32")

    def dim(self) -> int:
        # encode a dummy string once if needed
        return int(self.model.get_sentence_embedding_dimension())
