from __future__ import annotations

from typing import List, Tuple

from .vectorstore import ChromaVectorStore


def split_text(text: str, chunk_size: int = 600, overlap: int = 150) -> List[str]:
    """改進的文本切分策略，更適合中文內容"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks: List[str] = []
    sentences = _split_sentences(text)
    
    current_chunk = ""
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        
        # 如果加入當前句子會超過chunk_size，先保存當前chunk
        if current_length + sentence_length > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # 計算重疊部分
            if overlap > 0 and len(current_chunk) > overlap:
                overlap_text = current_chunk[-overlap:]
                current_chunk = overlap_text + sentence
                current_length = len(current_chunk)
            else:
                current_chunk = sentence
                current_length = sentence_length
        else:
            current_chunk += sentence
            current_length += sentence_length
    
    # 添加最後一個chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def _split_sentences(text: str) -> List[str]:
    """簡單的句子分割，適合中文文本"""
    import re
    # 使用中文標點符號分割句子
    sentences = re.split(r'[。！？；\n]+', text)
    # 過濾空句子，保留標點符號
    result = []
    for i, sentence in enumerate(sentences):
        if sentence.strip():
            # 添加原始標點符號（除了最後一個）
            if i < len(sentences) - 1:
                result.append(sentence + '。')
            else:
                result.append(sentence)
    return result


def ingest_text(doc_id: str, text: str) -> Tuple[int, int]:
    """Ingest raw text into vector store; returns (#chunks, #upserts)."""
    chunks = split_text(text)
    ids = [f"{doc_id}:{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": doc_id, "chunk": i} for i in range(len(chunks))]
    store = ChromaVectorStore()
    store.upsert(ids=ids, texts=chunks, metadatas=metadatas)
    return len(chunks), len(chunks)


