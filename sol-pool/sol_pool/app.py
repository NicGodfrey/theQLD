from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from sol_pool.broker import Broker, Session
from sol_pool.errors import PoolError, error_body
from sol_pool.settings import Settings


class SessionCreate(BaseModel):
    worker_id: int | None = Field(default=None, ge=1, le=10)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageCreate(BaseModel):
    mode: str = "sync"
    content: list[dict[str, Any]]


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings(
        data_dir=Path(os.environ.get("SOL_POOL_DATA_DIR", "./data")).resolve(),
        api_key=os.environ.get("SOL_POOL_API_KEY", "dev-key"),
        lease_seconds=float(os.environ.get("SOL_POOL_LEASE_SECONDS", "30")),
    )
    broker = Broker(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = settings
        app.state.broker = broker
        stop = asyncio.Event()

        async def sweep() -> None:
            while not stop.is_set():
                try:
                    await broker.expire_stale()
                except Exception:
                    pass
                try:
                    await asyncio.wait_for(stop.wait(), timeout=settings.sweep_interval_seconds)
                except asyncio.TimeoutError:
                    continue

        task = asyncio.create_task(sweep())
        try:
            yield
        finally:
            stop.set()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    app = FastAPI(title="GPT5.6 sol 10-slot gateway", version="0.1.0", lifespan=lifespan)
    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():
        app.mount("/demo", StaticFiles(directory=static_dir, html=True), name="demo")

    @app.middleware("http")
    async def sweep_expired_leases(request: Request, call_next):
        await broker.expire_stale()
        return await call_next(request)

    def request_id_of(request: Request) -> str:
        return request.headers.get("x-request-id") or "req_" + uuid4().hex[:12]

    def bearer(authorization: str | None) -> str:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise PoolError(401, "AUTH_REQUIRED", "需要 Bearer token")
        token = authorization.split(" ", 1)[1].strip()
        if not token:
            raise PoolError(401, "TOKEN_INVALID", "token 无效")
        return token

    def require_api_key(authorization: str | None) -> None:
        token = bearer(authorization)
        if token != settings.api_key:
            raise PoolError(401, "TOKEN_INVALID", "API key 无效")

    def require_session(authorization: str | None, session_id: str) -> Session:
        token = bearer(authorization)
        session = broker.get_session_by_token(token)
        if session is None or session.id != session_id:
            raise PoolError(404, "SESSION_NOT_FOUND", "会话不存在或不属于当前调用者")
        return session

    def require_idempotency(idempotency_key: str | None) -> str:
        if not idempotency_key:
            raise PoolError(400, "IDEMPOTENCY_KEY_REQUIRED", "缺少 Idempotency-Key")
        if not (8 <= len(idempotency_key) <= 128):
            raise PoolError(400, "INVALID_REQUEST", "Idempotency-Key 长度必须在 8 到 128 之间")
        return idempotency_key

    def message_text(body: MessageCreate) -> str:
        parts = []
        for item in body.content:
            if item.get("type") == "input_text":
                parts.append(str(item.get("text") or ""))
        text = "\n".join(parts).strip()
        if not text:
            raise PoolError(422, "VALIDATION_ERROR", "content 必须包含 input_text")
        return text

    @app.exception_handler(PoolError)
    async def handle_pool_error(request: Request, exc: PoolError) -> JSONResponse:
        rid = request_id_of(request)
        headers = {}
        if exc.code in {"ALL_WORKERS_BUSY", "WORKER_UNAVAILABLE", "POOL_FULL"}:
            headers["Retry-After"] = "5"
        return JSONResponse(status_code=exc.status_code, content=error_body(exc, rid), headers=headers)

    @app.get("/v1/health")
    async def health() -> dict[str, Any]:
        idle = sum(1 for slot in broker.slots.values() if slot.status == "idle")
        return {
            "ok": True,
            "display_name": settings.display_name,
            "slots": settings.slot_count,
            "idle": idle,
        }

    @app.get("/v1/workers")
    async def list_workers(authorization: str | None = Header(default=None)) -> dict[str, Any]:
        require_api_key(authorization)
        return {"object": "list", "data": broker.list_workers()}

    @app.post("/v1/sessions", status_code=201)
    async def create_session(
        body: SessionCreate,
        authorization: str | None = Header(default=None),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> dict[str, Any]:
        require_api_key(authorization)
        key = require_idempotency(idempotency_key)
        cached = broker.lookup_idempotency(key, body.model_dump())
        if cached:
            return JSONResponse(status_code=cached["status_code"], content=cached["body"])
        client_key = None
        if isinstance(body.metadata, dict):
            client_key = body.metadata.get("client_session_id")
        session = await broker.acquire(body.worker_id, client_session_key=client_key)
        payload = broker.session_public(session)
        broker.store_idempotency(key, body.model_dump(), 201, payload)
        return payload

    @app.get("/v1/sessions/{session_id}")
    async def get_session(
        session_id: str,
        authorization: str | None = Header(default=None),
    ) -> dict[str, Any]:
        session = require_session(authorization, session_id)
        return broker.session_public(session)

    @app.post("/v1/sessions/{session_id}/heartbeat")
    async def heartbeat(
        session_id: str,
        authorization: str | None = Header(default=None),
    ) -> dict[str, Any]:
        session = require_session(authorization, session_id)
        return broker.heartbeat(session)

    @app.delete("/v1/sessions/{session_id}")
    async def end_session(
        session_id: str,
        authorization: str | None = Header(default=None),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> dict[str, Any]:
        session = require_session(authorization, session_id)
        key = require_idempotency(idempotency_key)
        cached = broker.lookup_idempotency(key, {"session_id": session_id})
        if cached:
            return cached["body"]
        payload = await broker.end_session(session, reason="client_close")
        broker.store_idempotency(key, {"session_id": session_id}, 200, payload)
        return payload

    @app.post("/v1/workers/{worker_id}/sessions/{session_id}/messages")
    async def send_message(
        worker_id: int,
        session_id: str,
        body: MessageCreate,
        authorization: str | None = Header(default=None),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> Any:
        session = require_session(authorization, session_id)
        key = require_idempotency(idempotency_key)
        cached = broker.lookup_idempotency(key, {"worker_id": worker_id, **body.model_dump()})
        if cached:
            return JSONResponse(status_code=cached["status_code"], content=cached["body"])
        if body.mode not in {"sync", "stream"}:
            raise PoolError(422, "VALIDATION_ERROR", "mode 必须是 sync 或 stream")
        text = message_text(body)
        message = await broker.send_message(session, worker_id, text, body.mode)
        if body.mode == "stream":
            payload = {
                "id": message.id,
                "status": message.status,
                "events_url": f"/v1/workers/{worker_id}/sessions/{session_id}/messages/{message.id}/events",
            }
            status = 202
        else:
            payload = _message_body(message)
            status = 200
        broker.store_idempotency(key, {"worker_id": worker_id, **body.model_dump()}, status, payload)
        return JSONResponse(status_code=status, content=payload)

    @app.get("/v1/workers/{worker_id}/sessions/{session_id}/messages/{message_id}")
    async def get_message(
        worker_id: int,
        session_id: str,
        message_id: str,
        authorization: str | None = Header(default=None),
    ) -> dict[str, Any]:
        session = require_session(authorization, session_id)
        broker.require_worker(session, worker_id)
        message = session.messages.get(message_id)
        if message is None:
            raise PoolError(404, "MESSAGE_NOT_FOUND", "消息不存在")
        return _message_body(message)

    @app.get("/v1/workers/{worker_id}/sessions/{session_id}/messages/{message_id}/events")
    async def stream_events(
        worker_id: int,
        session_id: str,
        message_id: str,
        authorization: str | None = Header(default=None),
        last_event_id: str | None = Header(default=None, alias="Last-Event-ID"),
    ) -> StreamingResponse:
        session = require_session(authorization, session_id)
        broker.require_worker(session, worker_id)
        message = session.messages.get(message_id)
        if message is None:
            raise PoolError(404, "MESSAGE_NOT_FOUND", "消息不存在")

        async def event_source():
            start = 0
            if last_event_id and last_event_id.isdigit():
                start = int(last_event_id)
            queue: asyncio.Queue = asyncio.Queue()
            message.subscribers.append(queue)
            try:
                for event in message.events:
                    if int(event.get("seq") or 0) > start:
                        yield _sse(event)
                if message.status in {"completed", "aborted", "failed"}:
                    return
                while True:
                    event = await queue.get()
                    yield _sse(event)
                    if event.get("type") in {"response.completed", "response.failed"}:
                        return
            finally:
                if queue in message.subscribers:
                    message.subscribers.remove(queue)

        return StreamingResponse(event_source(), media_type="text/event-stream")

    @app.get("/v1/sessions/{session_id}/records")
    async def records(
        session_id: str,
        authorization: str | None = Header(default=None),
    ) -> dict[str, Any]:
        session = require_session(authorization, session_id)
        return broker.records(session)

    @app.get("/v1/sessions/{session_id}/billing")
    async def billing(
        session_id: str,
        authorization: str | None = Header(default=None),
    ) -> dict[str, Any]:
        session = require_session(authorization, session_id)
        return broker.billing_summary(session)

    return app


def _message_body(message) -> dict[str, Any]:
    return {
        "id": message.id,
        "object": "message",
        "session_id": message.session_id,
        "worker_id": message.worker_id,
        "status": message.status,
        "output": [{"type": "output_text", "text": message.output_text}],
        "reasoning": [{"type": "reasoning_text", "text": message.reasoning_text}],
        "usage": message.usage,
        "created_at": message.created_at,
        "completed_at": message.completed_at,
    }


def _sse(event: dict[str, Any]) -> str:
    seq = event.get("seq", 0)
    name = event.get("type", "message")
    import json

    return f"id: {seq}\nevent: {name}\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"
