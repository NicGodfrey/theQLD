from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from sol_pool.app import create_app
from sol_pool.settings import Settings


@pytest.fixture
def app(tmp_path):
    return create_app(
        Settings(
            data_dir=tmp_path,
            api_key="dev-key",
            lease_seconds=30,
            sweep_interval_seconds=0.2,
        )
    )


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client


def api_headers(idempotency: bool = False, token: str = "dev-key") -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if idempotency:
        headers["Idempotency-Key"] = str(uuid4())
    return headers


def create_session(client: TestClient, worker_id: int | None = None, token: str = "dev-key") -> dict:
    body = {} if worker_id is None else {"worker_id": worker_id}
    response = client.post("/v1/sessions", json=body, headers=api_headers(idempotency=True, token=token))
    assert response.status_code == 201, response.text
    return response.json()


def send_text(client: TestClient, session: dict, text: str, mode: str = "sync") -> dict:
    response = client.post(
        f"/v1/workers/{session['worker_id']}/sessions/{session['id']}/messages",
        json={"mode": mode, "content": [{"type": "input_text", "text": text}]},
        headers=api_headers(idempotency=True, token=session["access_token"]),
    )
    assert response.status_code in {200, 202}, response.text
    return response.json()
