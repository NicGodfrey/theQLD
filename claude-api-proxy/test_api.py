"""Function-level tests for server.py. No network, no port binding."""

import cursor_backend
import server


def test_validation():
    ok = {"model": "claude-fable-5", "max_tokens": 100, "messages": [{"role": "user", "content": "hi"}]}
    assert server.validate_messages_request(ok) is None

    assert "model" in server.validate_messages_request({"max_tokens": 1, "messages": [{"role": "user", "content": "x"}]})
    assert "max_tokens" in server.validate_messages_request({"model": "m", "messages": [{"role": "user", "content": "x"}]})
    assert "max_tokens" in server.validate_messages_request({"model": "m", "max_tokens": 0, "messages": [{"role": "user", "content": "x"}]})
    assert "max_tokens" in server.validate_messages_request({"model": "m", "max_tokens": True, "messages": [{"role": "user", "content": "x"}]})
    assert "messages" in server.validate_messages_request({"model": "m", "max_tokens": 1})
    assert "messages" in server.validate_messages_request({"model": "m", "max_tokens": 1, "messages": []})
    assert "role" in server.validate_messages_request({"model": "m", "max_tokens": 1, "messages": [{"role": "system", "content": "x"}]})
    assert "content" in server.validate_messages_request({"model": "m", "max_tokens": 1, "messages": [{"role": "user"}]})
    assert "system" in server.validate_messages_request(dict(ok, system=42))
    assert server.validate_messages_request("not a dict") == "body: input must be a JSON object"

    content_blocks = dict(ok, messages=[{"role": "user", "content": [{"type": "text", "text": "hi"}]}])
    assert server.validate_messages_request(content_blocks) is None


def test_inject_system():
    proxy = "PROXY PROMPT"

    out = server.inject_system({"model": "m"}, proxy)
    assert out["system"] == [{"type": "text", "text": proxy}]

    out = server.inject_system({"system": "caller prompt"}, proxy)
    assert out["system"] == [
        {"type": "text", "text": proxy},
        {"type": "text", "text": "caller prompt"},
    ]

    caller_blocks = [{"type": "text", "text": "block one"}]
    out = server.inject_system({"system": caller_blocks}, proxy)
    assert out["system"][0]["text"] == proxy
    assert out["system"][1:] == caller_blocks

    original = {"system": "caller"}
    server.inject_system(original, proxy)
    assert original["system"] == "caller"


def test_build_upstream_body():
    body = {
        "model": "claude-fable-5",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "hi"}],
        "temperature": 0.5,
        "totally_unknown_field": {"x": 1},
        "another_junk": True,
    }
    out = server.build_upstream_body(body, "P")
    assert "totally_unknown_field" not in out
    assert "another_junk" not in out
    assert out["temperature"] == 0.5
    assert out["model"] == "claude-fable-5"
    assert out["system"][0] == {"type": "text", "text": "P"}


def test_error_body():
    e = server.error_body("invalid_request_error", "bad")
    assert e == {"type": "error", "error": {"type": "invalid_request_error", "message": "bad"}}


def test_system_prompt_loads():
    text = server.get_system_prompt()
    assert "Claude" in text and "Fable 5" in text


def test_last_user_text():
    assert cursor_backend.last_user_text([{"role": "user", "content": "hi"}]) == "hi"
    assert cursor_backend.last_user_text(
        [
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": "ok"},
            {"role": "user", "content": [{"type": "text", "text": "second"}]},
        ]
    ) == "second"


def test_build_followup_text():
    text = cursor_backend.build_followup_text(
        {"messages": [{"role": "user", "content": "你好，你是什么模型"}]}
    )
    assert "你好，你是什么模型" in text
    assert "claude-api-proxy remote" in text
    assert cursor_backend.DEFAULT_SUBAGENT_ID in text


def test_claude_message_shape():
    msg = cursor_backend.claude_message("hello", "claude-fable-5", "msg_test")
    assert msg["type"] == "message"
    assert msg["role"] == "assistant"
    assert msg["content"] == [{"type": "text", "text": "hello"}]
    assert msg["stop_reason"] == "end_turn"


def test_parse_sse_and_anthropic_stream():
    raw = (
        "event: assistant\n"
        'data: {"text":"Hello"}\n'
        "\n"
        "event: result\n"
        'data: {"runId":"run-1","status":"FINISHED","text":"Hello world"}\n'
        "\n"
    )
    events = cursor_backend.parse_sse_events(raw)
    assert events[0][0] == "assistant"
    assert cursor_backend.cursor_events_to_text(events) == "Hello world"
    opened = cursor_backend.anthropic_stream_open("claude-fable-5", "msg_1")
    assert "event: message_start" in opened
    assert "event: content_block_delta" in cursor_backend.anthropic_stream_delta("Hi")
    assert "event: message_stop" in cursor_backend.anthropic_stream_close()


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS %s" % name)
            except AssertionError as exc:
                failures += 1
                print("FAIL %s: %s" % (name, exc))
    raise SystemExit(1 if failures else 0)
