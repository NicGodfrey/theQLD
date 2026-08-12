from __future__ import annotations

import asyncio
import hashlib
import json
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from sol_pool.billing import BillingLedger
from sol_pool.errors import PoolError
from sol_pool.fake_model import stream_reply
from sol_pool.ledger import SessionLedger
from sol_pool.settings import Settings


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _body_hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass
class Message:
    id: str
    session_id: str
    worker_id: int
    status: str = "queued"
    events: list[dict[str, Any]] = field(default_factory=list)
    output_text: str = ""
    reasoning_text: str = ""
    usage: dict[str, int] = field(default_factory=dict)
    created_at: str = field(default_factory=_utcnow)
    completed_at: str | None = None
    subscribers: list[asyncio.Queue] = field(default_factory=list)

    async def publish(self, event: dict[str, Any]) -> None:
        self.events.append(event)
        for queue in list(self.subscribers):
            await queue.put(event)


@dataclass
class Session:
    id: str
    worker_id: int
    epoch: int
    token: str
    token_hash: str
    state: str
    lease_expires_at: float
    created_at: str
    client_session_key: str | None = None
    messages: dict[str, Message] = field(default_factory=dict)
    close_reason: str | None = None


@dataclass
class Slot:
    id: int
    display_name: str
    status: str = "idle"
    session_id: str | None = None
    epoch: int = 0
    fence: int = 0
    sandbox: Path | None = None
    context: list[dict[str, str]] = field(default_factory=list)
    cancel: asyncio.Event = field(default_factory=asyncio.Event)
    status_since: str = field(default_factory=_utcnow)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class Broker:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.ledger = SessionLedger(settings.ledger_dir())
        self.billing = BillingLedger(settings)
        self.alloc_lock = asyncio.Lock()
        self.slots: dict[int, Slot] = {
            i: Slot(id=i, display_name=settings.display_name) for i in range(1, settings.slot_count + 1)
        }
        self.sessions: dict[str, Session] = {}
        self.token_index: dict[str, str] = {}
        self.idempotency: dict[str, dict[str, Any]] = {}
        for slot in self.slots.values():
            self._prepare_sandbox(slot)

    def _prepare_sandbox(self, slot: Slot) -> Path:
        root = self.settings.slots_dir() / f"{slot.id:02d}"
        current = root / "current"
        if current.exists():
            shutil.rmtree(current)
        current.mkdir(parents=True, exist_ok=True)
        slot.sandbox = current
        return current

    def list_workers(self) -> list[dict[str, Any]]:
        return [
            {
                "id": slot.id,
                "display_name": slot.display_name,
                "status": slot.status,
                "status_since": slot.status_since,
            }
            for slot in self.slots.values()
        ]

    def get_session(self, session_id: str) -> Session:
        session = self.sessions.get(session_id)
        if session is None:
            raise PoolError(404, "SESSION_NOT_FOUND", "会话不存在或不属于当前调用者")
        return session

    def get_session_by_token(self, token: str) -> Session | None:
        session_id = self.token_index.get(_hash_token(token))
        if not session_id:
            return None
        return self.sessions.get(session_id)

    def require_active(self, session: Session) -> None:
        if session.state == "ended":
            raise PoolError(410, "SESSION_ENDED", "会话已结束")
        if session.state == "ending":
            raise PoolError(409, "SESSION_ENDING", "会话正在结束")

    def require_worker(self, session: Session, worker_id: int) -> Slot:
        if session.worker_id != worker_id:
            raise PoolError(
                403,
                "WORKER_BINDING_MISMATCH",
                f"该会话绑定的是 worker {session.worker_id}，不能调用 worker {worker_id}",
                details={"session_worker_id": session.worker_id, "requested_worker_id": worker_id},
            )
        return self.slots[session.worker_id]

    def lookup_idempotency(self, key: str, payload: Any) -> dict[str, Any] | None:
        existing = self.idempotency.get(key)
        if existing is None:
            return None
        if existing["body_hash"] != _body_hash(payload):
            raise PoolError(409, "IDEMPOTENCY_CONFLICT", "该幂等键已用于不同请求")
        return existing

    def store_idempotency(self, key: str, payload: Any, status_code: int, body: dict[str, Any]) -> None:
        self.idempotency[key] = {
            "body_hash": _body_hash(payload),
            "status_code": status_code,
            "body": body,
        }

    async def acquire(self, worker_id: int | None, client_session_key: str | None = None) -> Session:
        async with self.alloc_lock:
            if worker_id is not None:
                if worker_id not in self.slots:
                    raise PoolError(422, "VALIDATION_ERROR", "worker_id 必须是 1 到 10")
                slot = self.slots[worker_id]
                if slot.status != "idle":
                    raise PoolError(
                        409,
                        "WORKER_UNAVAILABLE",
                        "指定 worker 当前不可分配",
                        retryable=True,
                        details={"worker_id": worker_id, "status": slot.status},
                    )
            else:
                slot = next((item for item in self.slots.values() if item.status == "idle"), None)
                if slot is None:
                    raise PoolError(409, "ALL_WORKERS_BUSY", "当前没有可分配的 worker", retryable=True)

            slot.epoch += 1
            slot.fence += 1
            slot.cancel = asyncio.Event()
            slot.context = []
            sandbox = self._prepare_sandbox(slot)
            (sandbox / ".session_secret").write_text(uuid4().hex, encoding="utf-8")
            token = "st_" + uuid4().hex + uuid4().hex[:16]
            session = Session(
                id="ses_" + uuid4().hex,
                worker_id=slot.id,
                epoch=slot.epoch,
                token=token,
                token_hash=_hash_token(token),
                state="active",
                lease_expires_at=time.time() + self.settings.lease_seconds,
                created_at=_utcnow(),
                client_session_key=client_session_key,
            )
            slot.session_id = session.id
            slot.status = "bound"
            slot.status_since = _utcnow()
            self.sessions[session.id] = session
            self.token_index[session.token_hash] = session.id
            self.ledger.append(
                session.id,
                "session.start",
                {
                    "worker_id": slot.id,
                    "epoch": slot.epoch,
                    "display_name": slot.display_name,
                    "sandbox": str(sandbox),
                },
            )
            return session

    def heartbeat(self, session: Session) -> dict[str, Any]:
        self.require_active(session)
        session.lease_expires_at = time.time() + self.settings.lease_seconds
        slot = self.slots[session.worker_id]
        return {
            "session_id": session.id,
            "state": session.state,
            "worker_id": session.worker_id,
            "worker_status": slot.status,
            "lease_expires_at": datetime.fromtimestamp(session.lease_expires_at, timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }

    async def expire_stale(self) -> list[str]:
        now = time.time()
        closed: list[str] = []
        for session in list(self.sessions.values()):
            if session.state != "active":
                continue
            if session.lease_expires_at > now:
                continue
            await self.end_session(session, reason="client_timeout")
            closed.append(session.id)
        return closed

    async def end_session(self, session: Session, reason: str = "client_close") -> dict[str, Any]:
        if session.state == "ended":
            slot = self.slots[session.worker_id]
            return self._session_view(session, slot, reset_status="completed")
        session.state = "ending"
        session.close_reason = reason
        slot = self.slots[session.worker_id]
        slot.status = "resetting"
        slot.status_since = _utcnow()
        slot.cancel.set()
        # Let any in-flight generation observe the cancel flag.
        await asyncio.sleep(0)
        self.ledger.append(
            session.id,
            "session.reset_requested",
            {"reason": reason, "epoch": session.epoch, "worker_id": slot.id},
        )
        await self._wipe_slot(slot)
        session.state = "ended"
        slot.session_id = None
        slot.status = "idle"
        slot.fence += 1
        slot.status_since = _utcnow()
        self.ledger.append(
            session.id,
            "session.close",
            {"reason": reason, "epoch": session.epoch, "chain_valid": self.ledger.verify_chain(session.id)},
        )
        return self._session_view(session, slot, reset_status="completed")

    async def _wipe_slot(self, slot: Slot) -> None:
        slot.context.clear()
        if slot.sandbox and slot.sandbox.exists():
            shutil.rmtree(slot.sandbox, ignore_errors=True)
        self._prepare_sandbox(slot)

    async def send_message(self, session: Session, worker_id: int, text: str, mode: str) -> Message:
        self.require_active(session)
        slot = self.require_worker(session, worker_id)
        async with slot.lock:
            if slot.status == "busy":
                raise PoolError(409, "SESSION_BUSY", "该会话已有生成任务正在运行", retryable=True)
            message = Message(
                id="msg_" + uuid4().hex,
                session_id=session.id,
                worker_id=worker_id,
            )
            session.messages[message.id] = message
            slot.status = "busy"
            slot.status_since = _utcnow()
            slot.cancel.clear()
        self.ledger.append(session.id, "message.user", {"message_id": message.id, "text": text})
        slot.context.append({"role": "user", "content": text})
        started = time.perf_counter()
        model_call_id = "call_" + uuid4().hex

        async def run() -> None:
            try:
                await self._generate(session, slot, message, text, model_call_id, started)
            finally:
                if session.state == "active" and slot.session_id == session.id:
                    slot.status = "bound"
                    slot.status_since = _utcnow()

        if mode == "stream":
            asyncio.create_task(run())
            return message
        await run()
        return message

    async def _generate(
        self,
        session: Session,
        slot: Slot,
        message: Message,
        text: str,
        model_call_id: str,
        started: float,
    ) -> None:
        message.status = "in_progress"
        seq = 0
        interrupted = False
        usage = {
            "input_tokens": 0,
            "cached_input_tokens": 0,
            "visible_output_tokens": 0,
            "reasoning_tokens": 0,
        }
        assert slot.sandbox is not None
        try:
            async for event in stream_reply(text, slot.sandbox):
                if slot.cancel.is_set() or session.state != "active":
                    interrupted = True
                    break
                seq += 1
                event = {**event, "message_id": message.id, "seq": seq}
                if event["type"] == "response.reasoning.delta":
                    message.reasoning_text += event["delta"]
                    self.ledger.append(
                        session.id,
                        "assistant.reasoning.delta",
                        {"message_id": message.id, "seq": seq, "text": event["delta"]},
                    )
                elif event["type"] == "response.output_text.delta":
                    message.output_text += event["delta"]
                    self.ledger.append(
                        session.id,
                        "assistant.content.delta",
                        {"message_id": message.id, "seq": seq, "text": event["delta"]},
                    )
                elif event["type"] == "response.completed":
                    usage = event["usage"]
                    message.usage = usage
                await message.publish(event)
            if interrupted:
                usage["visible_output_tokens"] = max(
                    usage.get("visible_output_tokens", 0),
                    max(0, (len(message.output_text) + 3) // 4) if message.output_text else 0,
                )
                usage["reasoning_tokens"] = max(
                    usage.get("reasoning_tokens", 0),
                    max(0, (len(message.reasoning_text) + 3) // 4) if message.reasoning_text else 0,
                )
                usage["input_tokens"] = usage.get("input_tokens") or max(1, (len(text) + 3) // 4)
                seq += 1
                abort_event = {
                    "type": "response.completed",
                    "message_id": message.id,
                    "seq": seq,
                    "status": "aborted",
                    "usage": usage,
                }
                await message.publish(abort_event)
                message.status = "aborted"
                termination = session.close_reason or "cancelled"
            else:
                message.status = "completed"
                termination = "completed"
            message.completed_at = _utcnow()
            slot.context.append({"role": "assistant", "content": message.output_text})
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            billing_event = self.billing.finalize_call(
                session_id=session.id,
                session_epoch=session.epoch,
                worker_id=slot.id,
                model_call_id=model_call_id,
                logical_request_id=message.id,
                termination=termination,
                input_tokens=int(usage.get("input_tokens") or 0),
                cached_input_tokens=int(usage.get("cached_input_tokens") or 0),
                visible_output_tokens=int(usage.get("visible_output_tokens") or 0),
                reasoning_tokens=int(usage.get("reasoning_tokens") or 0),
                bound_wall_clock_ms=elapsed_ms,
                stream_interrupted=interrupted,
            )
            self.ledger.append(
                session.id,
                "usage.final",
                {"message_id": message.id, "model_call_id": model_call_id, "usage": usage, "billing_event_id": billing_event["event_id"]},
            )
        except Exception as exc:  # pragma: no cover - defensive
            message.status = "failed"
            seq += 1
            await message.publish(
                {
                    "type": "response.failed",
                    "message_id": message.id,
                    "seq": seq,
                    "status": "failed",
                    "error": str(exc),
                }
            )
            raise

    def session_public(self, session: Session) -> dict[str, Any]:
        slot = self.slots[session.worker_id]
        reset_status = "completed" if session.state == "ended" else ("running" if session.state == "ending" else None)
        return self._session_view(session, slot, reset_status=reset_status)

    def _session_view(self, session: Session, slot: Slot, reset_status: str | None = None) -> dict[str, Any]:
        body = {
            "id": session.id,
            "object": "session",
            "state": session.state,
            "worker_id": session.worker_id,
            "worker_status": slot.status,
            "display_name": slot.display_name,
            "epoch": session.epoch,
            "lease": {
                "heartbeat_interval_seconds": max(1, int(self.settings.lease_seconds / 3)),
                "expires_at": datetime.fromtimestamp(session.lease_expires_at, timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            },
            "created_at": session.created_at,
        }
        if session.token and session.state == "active":
            body["access_token"] = session.token
        if session.state in {"ending", "ended"}:
            body["reset"] = {
                "status": reset_status or "completed",
                "reason": session.close_reason,
            }
        return body

    def records(self, session: Session) -> dict[str, Any]:
        events = self.ledger.read_all(session.id)
        return {
            "session_id": session.id,
            "chain_valid": self.ledger.verify_chain(session.id),
            "data": events,
        }

    def billing_summary(self, session: Session) -> dict[str, Any]:
        summary = self.billing.session_summary(session.id)
        if session.state == "active":
            summary["status"] = "provisional"
        else:
            summary["status"] = "final"
        return summary
