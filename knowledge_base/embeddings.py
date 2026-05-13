from typing import List


class EmbeddingProvider:
    def __init__(self):
        self.model = None

    def _lazy_load(self):
        if self.model is None:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, texts: List[str]) -> List[List[float]]:
        self._lazy_load()
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return [e.tolist() for e in embeddings]

    def embed_query(self, text: str) -> List[float]:
        return self.embed([text])[0]
