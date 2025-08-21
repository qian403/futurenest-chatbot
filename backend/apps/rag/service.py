from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from apps.api.schemas import ChatTurn, ChatResponse, ChatSource
from .llm_providers import get_default_llm
from .vectorstore import ChromaVectorStore


@dataclass
class RetrievedChunk:
    id: str
    document_id: Optional[int]
    text: str


class DemoRetriever:
    def __init__(self, corpus: Optional[List[str]] = None):
        self.corpus = corpus or [
            "FutureNest 是一個示範  ChatBot",
            "系統支援健康檢查與聊天 API，並逐步增加 RAG 能力。",
            "目前未啟用使用者驗證，採匿名使用，前端僅保存短期記憶。",
        ]

    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievedChunk]:
        # 極簡檢索：以包含關鍵字判斷
        results: List[RetrievedChunk] = []
        for idx, text in enumerate(self.corpus):
            if any(t.lower() in text.lower() for t in query.split()):
                results.append(RetrievedChunk(id=str(idx), document_id=None, text=text))
            if len(results) >= top_k:
                break
        return results or [RetrievedChunk(id="0", document_id=None, text=self.corpus[0])]


def build_prompt(message: str, history: Optional[List[ChatTurn]], contexts: List[RetrievedChunk]) -> str:
    hist = "\n".join(f"{t.role}: {t.content}" for t in (history or []))
    ctx = "\n- ".join(c.text for c in contexts)
    parts = [
        "You are a helpful assistant.",
        "Context:",
        f"- {ctx}",
        "Conversation:",
        hist,
        f"User: {message}",
        "Answer in Traditional Chinese.",
    ]
    return "\n".join(p for p in parts if p)


def answer_with_rag(message: str, history: Optional[List[ChatTurn]], top_k: int = 5) -> ChatResponse:
    store = None
    try:
        store = ChromaVectorStore()
        results = store.query(message, top_k=top_k)
        contexts = [RetrievedChunk(id=r["id"], document_id=(r.get("metadata") or {}).get("document_id"), text=r["text"]) for r in results]  # type: ignore[index]
    except Exception:
        retriever = DemoRetriever()
        contexts = retriever.retrieve(message, top_k=top_k)
    llm = get_default_llm()
    prompt = build_prompt(message, history, contexts)
    answer = llm.generate(prompt)
    sources = [ChatSource(id=c.id, document_id=c.document_id, snippet=c.text) for c in contexts]
    return ChatResponse(answer=answer, sources=sources)


