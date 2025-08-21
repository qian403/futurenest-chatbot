from __future__ import annotations

from typing import List, Tuple

from .vectorstore import ChromaVectorStore


def split_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + chunk_size)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == n:
            break
        start = max(end - overlap, start + 1)
    return chunks


def ingest_text(doc_id: str, text: str) -> Tuple[int, int]:
    """Ingest raw text into vector store; returns (#chunks, #upserts)."""
    chunks = split_text(text)
    ids = [f"{doc_id}:{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": doc_id, "chunk": i} for i in range(len(chunks))]
    store = ChromaVectorStore()
    store.upsert(ids=ids, texts=chunks, metadatas=metadatas)
    return len(chunks), len(chunks)


