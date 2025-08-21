from __future__ import annotations

from typing import Any, Dict, Optional, TypeVar, Generic
from pydantic import BaseModel, Field

from .middleware import get_current_trace_id


class ErrorInfo(BaseModel):
    code: str = Field(..., description="錯誤代碼")
    message: str = Field(..., description="錯誤訊息")
    details: Optional[Dict[str, Any]] = None


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[ErrorInfo] = None
    trace_id: str = Field(default_factory=get_current_trace_id)


def success_response(data: Any) -> Dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "error": None,
        "trace_id": get_current_trace_id(),
    }


def error_response(code: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {
        "success": False,
        "data": None,
        "error": {"code": code, "message": message, "details": details},
        "trace_id": get_current_trace_id(),
    }

