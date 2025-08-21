from __future__ import annotations

from typing import Optional, Dict, Any
from django.http import JsonResponse
import logging

from .schemas import error_response

logger = logging.getLogger(__name__)


class ApiError(Exception):
    def __init__(self, code: str, message: str, *, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def api_error_handler(request, exc: ApiError):
    logger.warning(
        "api_error",
        extra={
            "trace_id": getattr(request, "trace_id", ""),
            "code": exc.code,
            "status_code": exc.status_code,
        },
    )
    return JsonResponse(error_response(exc.code, exc.message, exc.details), status=exc.status_code)


def generic_error_handler(request, exc: Exception):
    # 記錄堆疊，對外不洩漏細節
    logger.exception("unhandled_exception", extra={"trace_id": getattr(request, "trace_id", "")})
    return JsonResponse(error_response("internal_error", "Internal Server Error"), status=500)
 