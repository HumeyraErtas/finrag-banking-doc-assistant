import numpy as np

def test_embedder_encode_monkeypatch(monkeypatch):
    # Stub SentenceTransformer to avoid model download in tests
    class DummyModel:
        def get_sentence_embedding_dimension(self):
            return 3
        def encode(self, texts, **kwargs):
            return np.ones((len(texts), 3), dtype=np.float32)

    import app.embeddings as emb
    monkeypatch.setattr(emb, "SentenceTransformer", lambda *_args, **_kwargs: DummyModel())

    e = emb.Embedder()
    vecs = e.encode(["a", "b"])
    assert vecs.shape == (2, 3)
    assert vecs.dtype == np.float32
