import uuid

from starlette.middleware.base import BaseHTTPMiddleware


class RequestTracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["x-trace-id"] = trace_id
        return response
