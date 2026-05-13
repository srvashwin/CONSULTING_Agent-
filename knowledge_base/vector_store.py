import os
from typing import List, Optional
import chromadb
from chromadb.config import Settings
from core.config import config
from .embeddings import EmbeddingProvider
from .frameworks.loader import FRAMEWORKS


class VectorStore:
    def __init__(self):
        os.makedirs(config.CHROMA_PERSIST_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
        self.embedder = EmbeddingProvider()
        self.collection = self._get_or_create_collection()
        self._seed_frameworks()

    def _get_or_create_collection(self):
        try:
            return self.client.get_collection("consulting_frameworks")
        except (ValueError, Exception):
            return self.client.create_collection(
                "consulting_frameworks",
                metadata={"hnsw:space": "cosine"},
            )

    def _seed_frameworks(self):
        if self.collection.count() > 0:
            return
        documents = []
        metadatas = []
        ids = []
        for i, fw in enumerate(FRAMEWORKS):
            doc = (
                f"Framework: {fw['name']}\n"
                f"Type: {fw['type']}\n"
                f"When to use: {fw['when_to_use']}\n"
                f"Structure: {fw['structure']}\n"
                f"Example questions: {'; '.join(fw['example_questions'])}"
            )
            documents.append(doc)
            metadatas.append({
                "name": fw["name"],
                "type": fw["type"],
            })
            ids.append(f"fw_{i}")
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    def search(self, query: str, n_results: int = 3) -> List[dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        docs = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                docs.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results.get("distances") else 0,
                })
        return docs

    def add_knowledge(self, text: str, metadata: Optional[dict] = None):
        doc_id = f"doc_{self.collection.count()}"
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[doc_id],
        )
