import uuid
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import json
from app.utils.logger_ import request_id_ctx_var, logger


# Middleware to attach request_id and log requests
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request_id_ctx_var.set(request_id)

        # Log incoming request
        try:
            body_bytes = await request.body()
            body_text = body_bytes.decode("utf-8") if body_bytes else ""
            body_preview = body_text if len(body_text) < 500 else body_text[:500] + "..."
        except Exception:
            body_preview = "<could not read body>"

        logger.info(
            f"Incoming request: {request.method} {request.url.path} "
            f"query={dict(request.query_params)} body={body_preview}"
        )

        # Process request
        response: Response = await call_next(request)

        # Log response status
        logger.info(
            f"Completed request: {request.method} {request.url.path} "
            f"status_code={response.status_code}"
        )

        # Include request ID in response headers
        response.headers["X-Request-ID"] = request_id
        return response