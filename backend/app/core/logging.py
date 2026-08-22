import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    # Quiet noisy third-party loggers a bit; keep our own app.* loggers at INFO.
    logging.getLogger("httpx").setLevel(logging.WARNING)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs every request with a correlation id, path, status code, and latency.

    This is the 'Logs + Monitoring' layer from the mandated architecture -
    it wraps every request, including the /resume/generate orchestrator calls.
    """

    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("app.request")

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        response = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            status_code = response.status_code if response else 500

            self.logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )