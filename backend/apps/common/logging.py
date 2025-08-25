from __future__ import annotations

from logging import Filter
from .middleware import get_current_trace_id


class TraceIdLogFilter(Filter):
    def filter(self, record):
        try:
            trace_id = get_current_trace_id()
        except Exception:
            trace_id = ""
        # 給 log 加上 trace_id ，避免格式器報錯
        setattr(record, "trace_id", getattr(record, "trace_id", None) or trace_id)
        return True

