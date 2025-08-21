from __future__ import annotations

import time
from functools import wraps
from typing import Callable

from django.core.cache import cache
from django.http import JsonResponse

from .schemas import error_response




def rate_limit(key: str, limit: int, window_seconds: int = 60) -> Callable:
    """
    簡易限流：以 cache 計數。
    key 可用格式字串，例如: "chat:{ip}"。
    """

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            xff = request.META.get('HTTP_X_FORWARDED_FOR')
            client_ip = (xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', 'unknown'))
            resolved_key = key.format(ip=client_ip)
            now = int(time.time())
            window = now // window_seconds
            cache_key = f"rl:{resolved_key}:{window}"
            count = cache.get(cache_key, 0)
            if count >= limit:
                return JsonResponse(
                    error_response("rate_limit", f"Too many requests, limit={limit}/{window_seconds}s"),
                    status=429,
                )
            cache.add(cache_key, 0, timeout=window_seconds)
            cache.incr(cache_key)
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


