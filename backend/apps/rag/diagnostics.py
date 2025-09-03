"""RAG system diagnostics utilities"""
from __future__ import annotations

import os
import logging
from typing import Dict, Any, List, Optional
from .vectorstore import ChromaVectorStore, LocalEmbedding, GoogleEmbedding

logger = logging.getLogger(__name__)


def diagnose_rag_system() -> Dict[str, Any]:
    """診斷 RAG 系統狀態，返回詳細信息"""
    diagnostics = {
        "status": "unknown",
        "embedding_type": "unknown", 
        "vector_store": {"status": "unknown", "collection_count": 0},
        "issues": [],
        "recommendations": []
    }
    
    try:
        # 檢查嵌入器類型
        if os.getenv("GOOGLE_API_KEY"):
            try:
                GoogleEmbedding("models/text-embedding-004")
                diagnostics["embedding_type"] = "google"
            except Exception as e:
                diagnostics["embedding_type"] = "local"
                diagnostics["issues"].append(f"Google Embedding unavailable: {e}")
        else:
            diagnostics["embedding_type"] = "local"
            diagnostics["issues"].append("GOOGLE_API_KEY not set, using local embedding")
            
        # 檢查向量存儲
        try:
            store = ChromaVectorStore()
            # 執行測試查詢
            results = store.query("test query", top_k=1)
            diagnostics["vector_store"]["status"] = "operational"
            diagnostics["vector_store"]["collection_count"] = len(results)
            
            if len(results) == 0:
                diagnostics["issues"].append("Vector store is empty - no documents indexed")
                diagnostics["recommendations"].append("Ingest some documents using /ingest endpoint")
                
        except Exception as e:
            diagnostics["vector_store"]["status"] = "error"
            diagnostics["issues"].append(f"Vector store error: {e}")
            diagnostics["recommendations"].append("Check ChromaDB installation and data directory")
            
        # 整體狀態評估
        if not diagnostics["issues"]:
            diagnostics["status"] = "healthy"
        elif diagnostics["vector_store"]["status"] == "operational":
            diagnostics["status"] = "degraded"
        else:
            diagnostics["status"] = "error"
            
    except Exception as e:
        logger.exception("RAG diagnostics failed")
        diagnostics["status"] = "error"
        diagnostics["issues"].append(f"Diagnostics failed: {e}")
        
    return diagnostics


def get_embedding_info() -> Dict[str, Any]:
    """獲取當前嵌入器的詳細信息"""
    info = {"type": "unknown", "model": "unknown", "dimension": 0}
    
    try:
        if os.getenv("GOOGLE_API_KEY"):
            try:
                embedder = GoogleEmbedding("models/text-embedding-004")
                info["type"] = "google"
                info["model"] = "models/text-embedding-004"
                # Test embedding to get dimension
                test_vec = embedder.embed(["test"])[0]
                info["dimension"] = len(test_vec)
            except Exception:
                embedder = LocalEmbedding()
                info["type"] = "local"
                info["dimension"] = embedder.dimension
        else:
            embedder = LocalEmbedding()
            info["type"] = "local" 
            info["dimension"] = embedder.dimension
            
    except Exception as e:
        info["error"] = str(e)
        
    return info