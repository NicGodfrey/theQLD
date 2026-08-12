from __future__ import annotations


class PoolError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        retryable: bool = False,
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.retryable = retryable
        self.details = details or {}


def error_body(exc: PoolError, request_id: str) -> dict:
    payload = {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "retryable": exc.retryable,
            "request_id": request_id,
        }
    }
    if exc.details:
        payload["error"]["details"] = exc.details
    return payload
