from uuid import uuid4

from tests.conftest import api_headers, create_session


def test_health(client):
    response = client.get("/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["slots"] == 10
    assert body["idle"] == 10
    assert body["display_name"] == "GPT5.6 sol"


def test_list_workers_requires_key(client):
    assert client.get("/v1/workers").status_code == 401
    response = client.get("/v1/workers", headers=api_headers())
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 10
    assert {item["id"] for item in data} == set(range(1, 11))
    assert all(item["display_name"] == "GPT5.6 sol" for item in data)
    assert all(item["status"] == "idle" for item in data)


def test_create_session_auto_assigns_unique_workers(client):
    first = create_session(client)
    second = create_session(client)
    assert first["worker_id"] != second["worker_id"]
    assert first["access_token"] != second["access_token"]
    workers = client.get("/v1/workers", headers=api_headers()).json()["data"]
    busy = [item for item in workers if item["status"] != "idle"]
    assert len(busy) == 2


def test_specified_worker_and_mismatch_forbidden(client):
    session = create_session(client, worker_id=3)
    assert session["worker_id"] == 3
    other = 4 if session["worker_id"] != 4 else 5
    response = client.post(
        f"/v1/workers/{other}/sessions/{session['id']}/messages",
        json={"mode": "sync", "content": [{"type": "input_text", "text": "hi"}]},
        headers=api_headers(idempotency=True, token=session["access_token"]),
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "WORKER_BINDING_MISMATCH"


def test_session_token_cannot_access_another_session(client):
    alpha = create_session(client, worker_id=1)
    beta = create_session(client, worker_id=2)
    response = client.get(
        f"/v1/sessions/{beta['id']}",
        headers=api_headers(token=alpha["access_token"]),
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SESSION_NOT_FOUND"


def test_capacity_rejects_eleventh_session(client):
    sessions = [create_session(client, worker_id=i) for i in range(1, 11)]
    assert len({item["worker_id"] for item in sessions}) == 10
    response = client.post("/v1/sessions", json={}, headers=api_headers(idempotency=True))
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ALL_WORKERS_BUSY"
    taken = sessions[0]
    client.delete(
        f"/v1/sessions/{taken['id']}",
        headers=api_headers(idempotency=True, token=taken["access_token"]),
    )
    recovered = create_session(client)
    assert recovered["worker_id"] == taken["worker_id"]


def test_missing_idempotency_key(client):
    response = client.post("/v1/sessions", json={}, headers=api_headers())
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "IDEMPOTENCY_KEY_REQUIRED"
