from tests.conftest import api_headers, create_session, send_text


def test_delete_resets_slot_and_clears_context(client):
    first = create_session(client, worker_id=5)
    send_text(client, first, "WRITE:old-session-secret")
    ended = client.delete(
        f"/v1/sessions/{first['id']}",
        headers=api_headers(idempotency=True, token=first["access_token"]),
    )
    assert ended.status_code == 200
    assert ended.json()["state"] == "ended"
    assert ended.json()["reset"]["status"] == "completed"

    workers = client.get("/v1/workers", headers=api_headers()).json()["data"]
    slot = next(item for item in workers if item["id"] == 5)
    assert slot["status"] == "idle"

    second = create_session(client, worker_id=5)
    assert second["id"] != first["id"]
    assert second["epoch"] != first["epoch"]
    replay = send_text(client, second, "READ_NOTE")
    assert "old-session-secret" not in replay["output"][0]["text"]
    assert "没有 note.txt" in replay["output"][0]["text"]


def test_lease_timeout_resets_worker(client, app):
    session = create_session(client, worker_id=8)
    send_text(client, session, "WRITE:should-vanish")
    app.state.broker.sessions[session["id"]].lease_expires_at = 0
    workers = client.get("/v1/workers", headers=api_headers()).json()["data"]
    slot = next(item for item in workers if item["id"] == 8)
    assert slot["status"] == "idle"
    status = client.get(
        f"/v1/sessions/{session['id']}",
        headers=api_headers(token=session["access_token"]),
    )
    assert status.json()["state"] == "ended"
    assert status.json()["reset"]["reason"] == "client_timeout"

    nxt = create_session(client, worker_id=8)
    replay = send_text(client, nxt, "READ_NOTE")
    assert "should-vanish" not in replay["output"][0]["text"]


def test_ended_session_rejects_new_messages(client):
    session = create_session(client, worker_id=2)
    client.delete(
        f"/v1/sessions/{session['id']}",
        headers=api_headers(idempotency=True, token=session["access_token"]),
    )
    response = client.post(
        f"/v1/workers/2/sessions/{session['id']}/messages",
        json={"mode": "sync", "content": [{"type": "input_text", "text": "hi"}]},
        headers=api_headers(idempotency=True, token=session["access_token"]),
    )
    assert response.status_code == 410
    assert response.json()["error"]["code"] == "SESSION_ENDED"
