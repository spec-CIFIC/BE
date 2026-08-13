from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import datetime, timezone

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if extra := getattr(record, "extra", None):
            payload.update(extra)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


class RequestResponseLoggerMiddleware(BaseHTTPMiddleware):
    LIMIT = 4096

    def __init__(self, app) -> None:
        super().__init__(app)
        self.log = logging.getLogger("app.request")

    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        raw = await request.body()

        async def receive():
            return {"type": "http.request", "body": raw, "more_body": False}

        request._receive = receive

        self.log.info("request", extra={"extra": {
            "req_id": req_id,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params) or None,
            "body": raw[:self.LIMIT].decode("utf-8", errors="replace") or None,
        }})

        started = time.perf_counter()
        response = await call_next(request)
        elapsed = round((time.perf_counter() - started) * 1000, 2)

        self.log.info("response", extra={"extra": {
            "req_id": req_id,
            "status": response.status_code,
            "elapsed_ms": elapsed,
        }})

        return response


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    for name in ("app", "app.request", "uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers = [handler]
        lg.setLevel(level)
        lg.propagate = False


def get_logger(name: str = "app") -> logging.Logger:
    return logging.getLogger(name)
