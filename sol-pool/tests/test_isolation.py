from tests.conftest import api_headers, create_session, send_text


def test_sandbox_notes_are_isolated_between_slots(client):
    alpha = create_session(client, worker_id=1)
    beta = create_session(client, worker_id=2)
    send_text(client, alpha, "WRITE:alpha-secret-42")
    send_text(client, beta, "WRITE:beta-secret-99")

    alpha_read = send_text(client, alpha, "READ_NOTE")
    beta_read = send_text(client, beta, "READ_NOTE")
    assert "alpha-secret-42" in alpha_read["output"][0]["text"]
    assert "beta-secret-99" in beta_read["output"][0]["text"]
    assert "beta-secret-99" not in alpha_read["output"][0]["text"]
    assert "alpha-secret-42" not in beta_read["output"][0]["text"]


def test_path_escape_is_denied(client):
    alpha = create_session(client, worker_id=1)
    beta = create_session(client, worker_id=2)
    send_text(client, alpha, "WRITE:do-not-leak")
    leaked = send_text(client, beta, "READ_FILE:../../01/current/note.txt")
    assert leaked["status"] == "completed"
    assert "do-not-leak" not in leaked["output"][0]["text"]
    assert "拒绝" in leaked["output"][0]["text"] or "不存在" in leaked["output"][0]["text"]
