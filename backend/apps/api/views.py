from ninja import NinjaAPI
from typing import List
from .schemas import (
    HealthResponse,
    ChatRequest,
    ChatResponse,
    IngestRequest,
    IngestResponse,
    IngestResult,
    TemplateMetaOut,
    IngestTemplateRequest,
)
from apps.common.schemas import success_response
from apps.common.exceptions import ApiError, api_error_handler, generic_error_handler
from apps.common.limits import MAX_PAYLOAD_BYTES
from apps.common.rate_limit import rate_limit
from apps.rag.service import answer_with_rag
from ninja.errors import ValidationError
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)
from apps.rag.ingest import ingest_text
from apps.rag.templates_registry import list_templates, load_template_text
from apps.rag.diagnostics import diagnose_rag_system

api = NinjaAPI(
    title="FutureNest RAG API",
    version="0.1.0",
    description="RAG Chatbot 的後端 API，提供健康檢查與聊天端點。",
)


@api.exception_handler(ApiError)
def _handle_api_error(request, exc: ApiError):
    return api_error_handler(request, exc)


@api.exception_handler(Exception)
def _handle_generic_error(request, exc: Exception):
    return generic_error_handler(request, exc)


@api.exception_handler(ValidationError)
def _handle_validation_error(request, exc: ValidationError):


    from django.http import JsonResponse
    try:
        details = exc.errors() if callable(getattr(exc, "errors", None)) else getattr(exc, "errors", None)
    except Exception:
        details = None
    logger.warning("validation_error", extra={"trace_id": getattr(request, "trace_id", "")})
    return JsonResponse(
        {
            "success": False,
            "data": None,
            "error": {"code": "validation_error", "message": "Invalid request", "details": details},
            "trace_id": getattr(request, "trace_id", ""),
        },
        status=422,
    )


@api.get("/health")
def health(request):
    return success_response(HealthResponse().model_dump())


@api.post("/chat")
@rate_limit(key="chat:{ip}", limit=20, window_seconds=60)
def chat(request, payload: ChatRequest):
    # 載荷大小基本檢查（非嚴格，Django 已解析完畢；仍可作為保護）
    try:
        meta_len = int(request.META.get("CONTENT_LENGTH") or 0)
    except Exception:
        meta_len = 0
    try:
        body_len = len(request.body or b"")
    except Exception:
        body_len = 0

    effective_len = max(meta_len, body_len)
    if effective_len > MAX_PAYLOAD_BYTES:
        raise ApiError(
            code="payload_too_large",
            message=f"payload exceeds {MAX_PAYLOAD_BYTES} bytes",
            status_code=413,
        )

    # 呼叫服務層，傳遞可選 doc_ids 與 inline_citations
    try:
        result = answer_with_rag(
            payload.message,
            payload.history,
            top_k=payload.top_k,
            doc_ids=[str(i) for i in (payload.doc_ids or [])] or None,
            inline_citations=payload.inline_citations,
        )
        return success_response(result.model_dump())
    except Exception:
        logger.exception("answer_with_rag_failed", extra={"trace_id": getattr(request, "trace_id", "")})
        from apps.api.schemas import ChatResponse, ChatSource
        fallback_response = ChatResponse(
            answer="抱歉，處理您的問題時發生了錯誤。請稍後再試，或簡化您的問題。",
            sources=[]
        )
        return success_response(fallback_response.model_dump())


@api.post("/ingest")
@rate_limit(key="ingest:{ip}", limit=10, window_seconds=60)
def ingest(request, payload: IngestRequest):
    results: list[IngestResult] = []
    for doc in payload.documents:
        try:
            chunks, upserts = ingest_text(doc.doc_id, doc.text)
            results.append(IngestResult(doc_id=doc.doc_id, chunks=chunks, upserts=upserts))
        except Exception as e:  
            logger.exception("ingest_failed", extra={"doc_id": doc.doc_id, "trace_id": getattr(request, "trace_id", "")})
            results.append(IngestResult(doc_id=doc.doc_id, ok=False, error=str(e)))
    return success_response(IngestResponse(results=results).model_dump())


@api.get("/templates")
def templates(request):
    metas = list_templates()
    items = [
        TemplateMetaOut(template_id=m.template_id, title=m.title, description=m.description).model_dump()
        for m in metas
    ]
    return success_response(items)


@api.post("/ingest-template")
@rate_limit(key="ingest:{ip}", limit=10, window_seconds=60)
def ingest_template(request, payload: IngestTemplateRequest):
    try:
        text = load_template_text(payload.template_id)
        chunks, upserts = ingest_text(payload.template_id, text)
        return success_response({"doc_id": payload.template_id, "chunks": chunks, "upserts": upserts})
    except Exception as e:  # pragma: no cover
        logger.exception("ingest_template_failed", extra={"template_id": payload.template_id, "trace_id": getattr(request, "trace_id", "")})
        raise ApiError(code="ingest_failed", message=str(e), status_code=400)


@api.get("/diagnostics")
def rag_diagnostics(request):
    """RAG 系統診斷端點"""
    diagnostics = diagnose_rag_system()
    return success_response(diagnostics)


# Plain Django health endpoint for compatibility with tests
def health_plain(request):
    return JsonResponse({"status": "ok"})
