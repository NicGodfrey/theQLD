from tests.conftest import api_headers, create_session


def test_create_session_idempotency_returns_same_session(client):
    key = "idem-create-session-001"
    headers = api_headers(token="dev-key")
    headers["Idempotency-Key"] = key
    first = client.post("/v1/sessions", json={"worker_id": 6}, headers=headers)
    second = client.post("/v1/sessions", json={"worker_id": 6}, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    workers = client.get("/v1/workers", headers=api_headers()).json()["data"]
    bound = [item for item in workers if item["status"] != "idle"]
    assert len(bound) == 1


def test_idempotency_conflict_on_different_body(client):
    key = "idem-conflict-body-001"
    headers = api_headers(token="dev-key")
    headers["Idempotency-Key"] = key
    first = client.post("/v1/sessions", json={"worker_id": 7}, headers=headers)
    assert first.status_code == 201
    second = client.post("/v1/sessions", json={"worker_id": 8}, headers=headers)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "IDEMPOTENCY_CONFLICT"


def test_message_idempotency_does_not_double_bill(client):
    session = create_session(client, worker_id=9)
    headers = api_headers(token=session["access_token"])
    headers["Idempotency-Key"] = "idem-message-repeat-001"
    payload = {"mode": "sync", "content": [{"type": "input_text", "text": "只应计费一次"}]}
    url = f"/v1/workers/9/sessions/{session['id']}/messages"
    first = client.post(url, json=payload, headers=headers)
    second = client.post(url, json=payload, headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    billing = client.get(
        f"/v1/sessions/{session['id']}/billing",
        headers=api_headers(token=session["access_token"]),
    ).json()
    assert billing["event_count"] == 1
