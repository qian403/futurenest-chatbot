from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class VSConfig:
    persist_dir: str = os.getenv("VECTOR_DIR", "backend/chroma")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")


class GoogleEmbedding:
    def __init__(self, model: str) -> None:
        # Ensure model name follows Google API format
        if model.startswith("models/") or model.startswith("tunedModels/"):
            self.model = model
        else:
            self.model = f"models/{model}"
        # Lazy import
        import google.generativeai as genai  # type: ignore

        self._genai = genai
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            self._genai.configure(api_key=api_key)

    def embed(self, texts: List[str]) -> List[List[float]]:
        # Batch embed via google generative ai
        # API expects one text at a time for embed_content; loop for simplicity
        vectors: List[List[float]] = []
        for t in texts:
            resp = self._genai.embed_content(model=self.model, content=t)
            vectors.append(resp.get("embedding", []) or resp.embedding)  # type: ignore[attr-defined]
        return vectors


class ChromaVectorStore:
    def __init__(self, config: Optional[VSConfig] = None) -> None:
        self.config = config or VSConfig()
        # Ensure telemetry off unless explicitly enabled
        os.environ.setdefault("ANONYMIZED_TELEMETRY", os.getenv("ANONYMIZED_TELEMETRY", "false"))
        # Lazy import and singleton collection reuse
        global _CHROMA_COLLECTION
        if '_CHROMA_COLLECTION' not in globals() or _CHROMA_COLLECTION is None:
            import chromadb  # type: ignore
            os.makedirs(self.config.persist_dir, exist_ok=True)
            _client = chromadb.PersistentClient(path=self.config.persist_dir)
            _CHROMA_COLLECTION = _client.get_or_create_collection(name="documents")
        self._collection = _CHROMA_COLLECTION
        self._embedder = GoogleEmbedding(self.config.embedding_model)

    def upsert(self, ids: List[str], texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        vectors = self._embedder.embed(texts)
        # de-dup same ids to avoid duplicates (delete then upsert)
        try:
            self._collection.delete(ids=ids)
        except Exception:
            pass
        self._collection.upsert(ids=ids, embeddings=vectors, metadatas=metadatas, documents=texts)

    def query(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        qvec = self._embedder.embed([query_text])[0]
        res = self._collection.query(query_embeddings=[qvec], n_results=top_k)
        results: List[Dict[str, Any]] = []
        # Normalize output
        for i in range(len(res.get("ids", [[]])[0])):
            results.append(
                {
                    "id": res["ids"][0][i],
                    "text": res["documents"][0][i],
                    "metadata": (res.get("metadatas") or [[None]])[0][i],
                    "distance": (res.get("distances") or [[None]])[0][i],
                }
            )
        return results


