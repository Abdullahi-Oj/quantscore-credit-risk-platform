import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("request-logger")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "path=%s method=%s status=%s latency_ms=%.2f",
            request.url.path,
            request.method,
            response.status_code,
            elapsed_ms,
        )
        return response
