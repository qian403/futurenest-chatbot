from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import hashlib
import math


@dataclass
class VSConfig:
    persist_dir: str = os.getenv("VECTOR_DIR", "backend/chroma")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")


class GoogleEmbedding:
    def __init__(self, model: str) -> None:
        self.model = model
        self._enabled = bool(os.getenv("GOOGLE_API_KEY"))
        if self._enabled:
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                self._genai = genai
            except ImportError:
                self._enabled = False
                raise RuntimeError("Google GenerativeAI SDK not installed. Run: pip install google-generativeai")
        else:
            raise RuntimeError("GOOGLE_API_KEY not set")

    def embed(self, texts: List[str]) -> List[List[float]]:
        # Batch embed via google generative ai
        # API expects one text at a time for embed_content; loop for simplicity
        if not self._enabled:
            raise RuntimeError("GOOGLE_API_KEY not set")
        vectors: List[List[float]] = []
        for t in texts:
            resp = self._genai.embed_content(model=self.model, content=t)
            # Normalize different SDK response shapes
            try:
                emb = resp.get("embedding")  # type: ignore[attr-defined]
            except Exception:
                emb = getattr(resp, "embedding", None)
            # Some versions return {"embedding": {"values": [...]}}
            if isinstance(emb, dict) and "values" in emb:
                emb = emb.get("values")
            if not isinstance(emb, list):
                emb = []
            vectors.append(emb)  # type: ignore[list-item]
        return vectors


class LocalEmbedding:
    """
    簡易本地嵌入（無外部依賴）：
    - 將 tokens hash 到固定維度（默認 256）做累加，並做 L2 正規化。
    - 僅用於無 Google API key 的開發/測試環境，效果有限但可用於檢索驗證。
    """

    def __init__(self, dimension: int = 256) -> None:
        self.dimension = max(16, dimension)

    def _tokenize(self, text: str) -> List[str]:
        # 中文/無空白語言：使用字元 bi-gram + 單字元
        s = ''.join(ch for ch in text.lower() if not ch.isspace())
        unigrams = list(s)
        bigrams = [s[i:i+2] for i in range(len(s)-1)] if len(s) >= 2 else []
        return unigrams + bigrams

    def _hash_token(self, token: str) -> int:
        # 使用 sha1 對 token 做 hash，取整數
        return int(hashlib.sha1(token.encode("utf-8")).hexdigest(), 16)

    def _vectorize(self, text: str) -> List[float]:
        vec = [0.0] * self.dimension
        for tok in self._tokenize(text):
            h = self._hash_token(tok)
            idx = h % self.dimension
            vec[idx] += 1.0
        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [self._vectorize(t) for t in texts]


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
            
            # 檢查是否需要重建collection以匹配embedding維度
            try:
                existing_collection = _client.get_collection(name="documents")
                # 測試維度兼容性：使用與當前相同的嵌入器
                try:
                    if os.getenv("GOOGLE_API_KEY"):
                        test_embedder = GoogleEmbedding(self.config.embedding_model)
                    else:
                        test_embedder = LocalEmbedding()
                except RuntimeError:
                    test_embedder = LocalEmbedding()
                
                # 嘗試用當前embedder查詢，看是否有維度衝突
                test_vec = test_embedder.embed(["test"])[0]
                existing_collection.query(query_embeddings=[test_vec], n_results=1)
                _CHROMA_COLLECTION = existing_collection
            except Exception:
                # 維度不匹配，刪除並重建collection
                try:
                    _client.delete_collection(name="documents")
                except Exception:
                    pass
                _CHROMA_COLLECTION = _client.create_collection(name="documents")
                
        self._collection = _CHROMA_COLLECTION
        # 選擇嵌入器：優先使用 Google Embedding，回退到本地嵌入
        try:
            if os.getenv("GOOGLE_API_KEY"):
                self._embedder = GoogleEmbedding(self.config.embedding_model)
            else:
                self._embedder = LocalEmbedding()
        except RuntimeError:
            # Google API 不可用時回退到本地嵌入
            self._embedder = LocalEmbedding()

    def upsert(self, ids: List[str], texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        vectors = self._embedder.embed(texts)
        # de-dup same ids to avoid duplicates (delete then upsert)
        try:
            self._collection.delete(ids=ids)
        except Exception:
            pass
        self._collection.upsert(ids=ids, embeddings=vectors, metadatas=metadatas, documents=texts)

    def query(self, query_text: str, top_k: int = 5, filter_document_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        qvec = self._embedder.embed([query_text])[0]
        where: Optional[Dict[str, Any]] = None
        if filter_document_ids:
            # Chroma where-filter on metadatas
            where = {"document_id": {"$in": filter_document_ids}}
        
        search_k = min(top_k * 10, 100)  
        res = self._collection.query(query_embeddings=[qvec], n_results=search_k, where=where)
        
        results: List[Dict[str, Any]] = []
        for i in range(len(res.get("ids", [[]])[0])):
            distance = (res.get("distances") or [[1.0]])[0][i]


            if isinstance(self._embedder, LocalEmbedding):
                # For local embedding: lower distance = higher similarity, scale to 0-1 range
                similarity = max(0.0, 1.0 / (1.0 + distance))
            else:
                # For Google embedding: standard distance to similarity conversion  
                similarity = max(0.0, 1.0 - distance) if distance is not None else 0.0
            
            results.append(
                {
                    "id": res["ids"][0][i],
                    "text": res["documents"][0][i],
                    "metadata": (res.get("metadatas") or [[None]])[0][i],
                    "distance": distance,
                    "similarity": similarity,
                }
            )
        
        # 根據相似度過濾低品質結果 - 進一步放寬閾值以支援更廣泛的問題
        # 本地嵌入需要更寬鬆的閾值來支援語意相關但字詞不同的查詢
        min_similarity = 0.1 if isinstance(self._embedder, GoogleEmbedding) else 0.0
        filtered_results = [r for r in results if r["similarity"] > min_similarity]
        
        # 返回top_k個結果
        return filtered_results[:top_k]


