from tests.conftest import api_headers, create_session, send_text


def test_message_records_include_reasoning_and_valid_chain(client):
    session = create_session(client, worker_id=1)
    message = send_text(client, session, "请解释隔离策略")
    assert message["status"] == "completed"
    assert message["reasoning"][0]["text"]
    assert "[GPT5.6 sol]" in message["output"][0]["text"]
    assert message["usage"]["reasoning_tokens"] > 0
    assert message["usage"]["visible_output_tokens"] > 0

    records = client.get(
        f"/v1/sessions/{session['id']}/records",
        headers=api_headers(token=session["access_token"]),
    )
    assert records.status_code == 200
    body = records.json()
    assert body["chain_valid"] is True
    types = [item["event_type"] for item in body["data"]]
    assert "session.start" in types
    assert "message.user" in types
    assert "assistant.reasoning.delta" in types
    assert "assistant.content.delta" in types
    assert "usage.final" in types


def test_billing_is_per_call_and_survives_reset(client):
    session = create_session(client, worker_id=4)
    send_text(client, session, "第一问")
    send_text(client, session, "第二问")
    live = client.get(
        f"/v1/sessions/{session['id']}/billing",
        headers=api_headers(token=session["access_token"]),
    ).json()
    assert live["status"] == "provisional"
    assert live["event_count"] == 2
    assert live["usage"]["reasoning_tokens"] > 0
    assert float(live["total"]) > 0
    first_total = live["total"]

    client.delete(
        f"/v1/sessions/{session['id']}",
        headers=api_headers(idempotency=True, token=session["access_token"]),
    )
    final = client.get(
        f"/v1/sessions/{session['id']}/billing",
        headers=api_headers(token=session["access_token"]),
    ).json()
    assert final["status"] == "final"
    assert final["event_count"] == 2
    assert final["total"] == first_total
    call_ids = [event["identity"]["model_call_id"] for event in final["events"]]
    assert len(call_ids) == len(set(call_ids))
