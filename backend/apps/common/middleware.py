from __future__ import annotations

import uuid
from typing import Callable
from contextvars import ContextVar


_current_trace_id: ContextVar[str] = ContextVar("trace_id", default="")


def get_current_trace_id() -> str:
    value = _current_trace_id.get()
    return value or ""




class TraceIdMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response


    def __call__(self, request):
        trace_id = uuid.uuid4().hex
        request.trace_id = trace_id
        token = _current_trace_id.set(trace_id)
        try:
            response = self.get_response(request)
        finally:
            _current_trace_id.reset(token)
        response["X-Trace-Id"] = trace_id
        return response

