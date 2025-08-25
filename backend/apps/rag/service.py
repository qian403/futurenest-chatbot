from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import os

from apps.api.schemas import ChatTurn, ChatResponse, ChatSource
from .ingest import split_text
from .templates_registry import list_templates, load_template_text, extract_article_text, find_article_any
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


def build_prompt(message: str, history: Optional[List[ChatTurn]], contexts: List[RetrievedChunk], *, inline_citations: Optional[bool] = None) -> str:
    # Use only env-provided system prompt; omit System line if not set/empty.
    system_prompt = (os.getenv("SYSTEM_PROMPT") or "").strip()

    # Determine whether to include inline citations
    if inline_citations is None:
        inline_default = (os.getenv("INLINE_CITATIONS_DEFAULT") or "").strip()
        inline_citations = inline_default == "1"

    # 改進的上下文處理：根據相關性排序和去重
    filtered_contexts = _filter_and_rank_contexts(message, contexts)
    
    # Present sources; if inline citations requested, append markers [n]
    sources_list = "\n".join(
        (
            f"- {c.text[:200]}{'…' if len(c.text) > 200 else ''}"
            if not inline_citations
            else f"- [source] {c.text[:200]}{'…' if len(c.text) > 200 else ''}"
        )
        for c in filtered_contexts
    )

    hist = "\n".join(f"{t.role}: {t.content}" for t in (history or []))

    # 改進的指令集
    instructions = [
        "請基於提供的資料來源回答問題。",
        "如果資料來源不足以回答問題，請明確說明並提供你能給出的相關資訊。",
        "使用繁體中文回答，保持專業和準確。",
        "回答要簡潔明瞭，先給結論再說明細節。"
    ]
    if not inline_citations:
        instructions.append("不要使用數字標註如[1]、[2]等引用格式。")
    
    # 檢查是否有相關上下文
    if not filtered_contexts:
        instructions.insert(0, "注意：沒有找到直接相關的資料來源，請根據一般知識謹慎回答。")
    
    parts = [
        (f"系統提示: {system_prompt}" if system_prompt else ""),
        "相關資料來源:",
        sources_list if sources_list else "無直接相關資料",
        "對話記錄:",
        hist,
        f"用戶問題: {message}",
        "回答指引: " + " ".join(instructions),
    ]
    return "\n".join(p for p in parts if p)


def _calculate_text_similarity(query: str, text: str) -> float:
    """計算查詢與文本的相似度分數 (0-1)"""
    import re
    
    # 中文分詞處理：提取中文字符和英文單詞
    def extract_tokens(text):
        # 提取中文字符
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        # 提取英文單詞
        english_words = re.findall(r'[a-zA-Z]+', text.lower())
        return set(chinese_chars + english_words)
    
    query_tokens = extract_tokens(query)
    text_tokens = extract_tokens(text)
    
    if not query_tokens or not text_tokens:
        return 0.0
    
    # 計算詞彙重疊度
    intersection = query_tokens.intersection(text_tokens)
    union = query_tokens.union(text_tokens)
    jaccard = len(intersection) / len(union) if union else 0.0
    
    # 檢查關鍵字匹配（直接字符串包含）
    keyword_matches = sum(1 for token in query_tokens if token in text)
    keyword_score = keyword_matches / len(query_tokens) if query_tokens else 0.0
    
    # 檢查完整詞語匹配（對於中文特別重要）
    query_phrases = re.findall(r'[\u4e00-\u9fff]{2,}', query)
    phrase_matches = sum(1 for phrase in query_phrases if phrase in text)
    phrase_score = phrase_matches / len(query_phrases) if query_phrases else 0.0
    
    # 組合分數：詞彙重疊 + 關鍵字匹配 + 詞語匹配
    return 0.4 * jaccard + 0.3 * keyword_score + 0.3 * phrase_score

def _filter_and_rank_contexts(query: str, contexts: List[RetrievedChunk]) -> List[RetrievedChunk]:
    """過濾和排序上下文，移除重複和低相關性內容"""
    if not contexts:
        return []
    
    # 計算相似度分數
    scored_contexts = []
    for ctx in contexts:
        similarity = _calculate_text_similarity(query, ctx.text)
        scored_contexts.append((similarity, ctx))
    
    # 按相似度排序
    scored_contexts.sort(key=lambda x: x[0], reverse=True)
    
    # 去除重複和低相關性內容
    filtered = []
    seen_texts = set()
    for score, ctx in scored_contexts:
        # 跳過相似度太低的內容
        if score < 0.1:
            continue
            
        # 簡單去重：檢查文本相似度
        text_key = ctx.text[:100].lower().strip()
        if text_key in seen_texts:
            continue
            
        seen_texts.add(text_key)
        filtered.append(ctx)
        
        # 限制返回數量
        if len(filtered) >= 3:
            break
    
    return filtered

def answer_with_rag(message: str, history: Optional[List[ChatTurn]], top_k: int = 5, *, doc_ids: Optional[List[str]] = None, inline_citations: Optional[bool] = None) -> ChatResponse:
    # 快速路徑：若查詢明確指定「第N條」，先嘗試直接取得條文全文
    import re as _re_fast
    m_fast = _re_fast.findall(r"第\s*([0-9０-９]+)\s*條", message)
    if m_fast:
        hit = find_article_any(m_fast[0])
        if hit:
            tid, full = hit
            # 產生「解釋版」回覆（避免直接貼全文）
            llm = get_default_llm()
            summarize_instructions = (
                "請嚴格依據下列條文，用繁體中文回答：\n"
                "1) 先給一句話結論。\n"
                "2) 接著條列重點 3-6 點（精簡、準確）。\n"
                "3) 不要貼出全文，不要使用數字型內文引用。\n"
                "4) 若條文有列舉項目，請歸納而非照抄。\n"
            )
            prompt = f"{summarize_instructions}\n--- 條文開始 ---\n{full}\n--- 條文結束 ---\n"
            answer = llm.generate(prompt)
            # 來源 snippet（短）
            MAX_SNIPPET_CHARS = int(os.getenv("SNIPPET_MAX_CHARS", "300"))
            def _truncate(text: str) -> str:
                return (text[:MAX_SNIPPET_CHARS] + "…") if len(text) > MAX_SNIPPET_CHARS else text
            
            # 提取條文編號作為引用
            article_ref = f"勞基法第{m_fast[0]}條"
            sources = [ChatSource(id=f"article:{m_fast[0]}", document_id=tid, snippet=_truncate(full), article_reference=article_ref)]
            return ChatResponse(answer=answer, sources=sources)
    store = None
    try:
        store = ChromaVectorStore()
        results = store.query(message, top_k=top_k, filter_document_ids=doc_ids)
        contexts = [RetrievedChunk(id=r["id"], document_id=(r.get("metadata") or {}).get("document_id"), text=r["text"]) for r in results]  # type: ignore[index]
    except Exception:
        retriever = DemoRetriever()
        contexts = retriever.retrieve(message, top_k=top_k)
    # 後置關鍵字過濾，提高精確度：若詢問含有「第70條」等模式，優先保留包含該關鍵字的 context
    try:
        import re as _re
        m = _re.findall(r"第\s*([0-9０-９]+)\s*條", message)
        if m:
            pat = f"第{m[0]}條"
            prioritized = [c for c in contexts if pat in c.text]
            if prioritized:
                # 將匹配者排到最前並去重
                ids = set()
                new_list: List[RetrievedChunk] = []
                for c in prioritized + contexts:
                    if c.id not in ids:
                        new_list.append(c)
                        ids.add(c.id)
                contexts = new_list[:top_k]
            else:
                # 模板後備：如能解析條文號，直接抽取條文全文並優先提供
                fallback: List[RetrievedChunk] = []
                for meta in list_templates():
                    full = extract_article_text(meta.template_id, m[0])
                    if full:
                        fallback.append(
                            RetrievedChunk(id=f"template:{meta.template_id}:article:{m[0]}", document_id=meta.template_id, text=full)
                        )
                        break
                if fallback:
                    contexts = (fallback + contexts)[:top_k]
    except Exception:
        pass
    llm = get_default_llm()
    prompt = build_prompt(message, history, contexts, inline_citations=inline_citations)
    answer = llm.generate(prompt)
    # 無條件清除模型回傳中的 [n] 圖樣（防守性處理）
    import re
    if not inline_citations:
        answer = re.sub(r"\[(\s*\d+(\s*,\s*\d+)*)\]", "", answer)
    # 截斷 snippet，避免回應過大
    MAX_SNIPPET_CHARS = int(os.getenv("SNIPPET_MAX_CHARS", "300"))
    def _truncate(text: str) -> str:
        return (text[:MAX_SNIPPET_CHARS] + "…") if len(text) > MAX_SNIPPET_CHARS else text

    # 建立來源列表，提取條文編號作為引用
    def _extract_article_reference(text: str, context_id: str) -> Optional[str]:
        import re
        # 在文本中尋找條文編號
        article_matches = re.findall(r"第\s*([0-9０-９]+)\s*條", text)
        if article_matches:
            return f"勞基法第{article_matches[0]}條"
        # 如果 ID 中包含 article 資訊
        if "article:" in context_id:
            article_num = context_id.split("article:")[-1]
            return f"勞基法第{article_num}條"
        return None

    sources = []
    for c in contexts:
        article_ref = _extract_article_reference(c.text, c.id)
        sources.append(ChatSource(
            id=c.id, 
            document_id=c.document_id, 
            snippet=_truncate(c.text),
            article_reference=article_ref
        ))
    return ChatResponse(answer=answer, sources=sources)


