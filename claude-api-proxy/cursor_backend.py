"""Translate official Claude Messages API calls onto this Cursor Cloud Agent."""

import base64
import json
import os
import time
import uuid
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

DEFAULT_AGENT_ID = "bc-f222349c-ced0-4c32-9a8e-c15d699654d3"
DEFAULT_SUBAGENT_ID = "bc-d7e40036-32de-5eb9-9a6a-16494909aee1"
DEFAULT_CURSOR_API = "https://api.cursor.com"
POLL_INTERVAL_S = 2
BUSY_RETRY_S = 3
MAX_BUSY_RETRIES = 20

REMOTE_PREFIX = (
    "[claude-api-proxy remote]\n"
    "This message is from a remote caller using the official Claude Messages API.\n"
    "Answer as the Fable 5 thinking xhigh Claude Code agent. "
    "If you can resume subagent %s, do that and relay its reply. "
    "Do not mention Cursor, Grok, or the parent agent unless the user asks.\n\n"
    "User message:\n"
) % DEFAULT_SUBAGENT_ID


def cursor_config():
    key = os.environ.get("CURSOR_API_KEY") or os.environ.get("CURSOR_API_TOKEN")
    agent_id = os.environ.get("CURSOR_AGENT_ID", DEFAULT_AGENT_ID)
    base = (os.environ.get("CURSOR_API_BASE") or DEFAULT_CURSOR_API).rstrip("/")
    return key, agent_id, base


def content_to_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text") or "")
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return "" if content is None else str(content)


def last_user_text(messages):
    for msg in reversed(messages or []):
        if isinstance(msg, dict) and msg.get("role") == "user":
            return content_to_text(msg.get("content"))
    return ""


def build_followup_text(body, proxy_system=""):
    user_text = last_user_text(body.get("messages") or [])
    parts = [REMOTE_PREFIX, user_text]
    caller_system = body.get("system")
    extra = content_to_text(caller_system) if caller_system else ""
    if proxy_system:
        parts = [REMOTE_PREFIX, "Preset system layer is already on this agent.\n\n", user_text]
    if extra:
        parts.append("\n\nCaller system:\n")
        parts.append(extra)
    return "".join(parts)


def basic_auth_header(api_key):
    token = base64.b64encode(("%s:" % api_key).encode("utf-8")).decode("ascii")
    return "Basic %s" % token


def cursor_request(method, url, api_key, body=None, accept="application/json", timeout=600):
    headers = {
        "authorization": basic_auth_header(api_key),
        "accept": accept,
    }
    data = None
    if body is not None:
        headers["content-type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    req = urlrequest.Request(url, data=data, method=method, headers=headers)
    return urlrequest.urlopen(req, timeout=timeout)


def create_run(api_key, agent_id, base, prompt_text):
    url = "%s/v1/agents/%s/runs" % (base, agent_id)
    last_err = None
    for _ in range(MAX_BUSY_RETRIES):
        try:
            with cursor_request("POST", url, api_key, {"prompt": {"text": prompt_text}}) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            run = payload.get("run") or payload
            run_id = run.get("id")
            if not run_id:
                raise RuntimeError("cursor create-run response missing run id")
            return run_id
        except HTTPError as e:
            raw = e.read()
            last_err = RuntimeError("cursor API %s: %s" % (e.code, raw.decode("utf-8", "replace")))
            if e.code == 409:
                time.sleep(BUSY_RETRY_S)
                continue
            raise last_err
    if last_err is not None:
        raise last_err
    raise RuntimeError("cursor agent stayed busy")


def get_run(api_key, agent_id, base, run_id):
    url = "%s/v1/agents/%s/runs/%s" % (base, agent_id, run_id)
    with cursor_request("GET", url, api_key) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wait_for_run(api_key, agent_id, base, run_id, timeout_s=600):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        run = get_run(api_key, agent_id, base, run_id)
        status = (run.get("status") or "").upper()
        if status in ("FINISHED", "ERROR", "CANCELLED", "EXPIRED"):
            return run
        time.sleep(POLL_INTERVAL_S)
    raise TimeoutError("cursor run %s timed out" % run_id)


def claude_message(text, model, message_id=None):
    return {
        "id": message_id or ("msg_%s" % uuid.uuid4().hex),
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": [{"type": "text", "text": text or ""}],
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": 0, "output_tokens": 0},
    }


def sse_line(event, data):
    return "event: %s\ndata: %s\n\n" % (event, json.dumps(data, ensure_ascii=False))


def anthropic_stream_open(model, message_id):
    chunks = [
        sse_line(
            "message_start",
            {
                "type": "message_start",
                "message": {
                    "id": message_id,
                    "type": "message",
                    "role": "assistant",
                    "model": model,
                    "content": [],
                    "stop_reason": None,
                    "stop_sequence": None,
                    "usage": {"input_tokens": 0, "output_tokens": 0},
                },
            },
        ),
        sse_line(
            "content_block_start",
            {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
        ),
    ]
    return "".join(chunks)


def anthropic_stream_delta(text):
    return sse_line(
        "content_block_delta",
        {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": text}},
    )


def anthropic_stream_close():
    return "".join(
        [
            sse_line("content_block_stop", {"type": "content_block_stop", "index": 0}),
            sse_line(
                "message_delta",
                {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": 0}},
            ),
            sse_line("message_stop", {"type": "message_stop"}),
        ]
    )


def parse_sse_events(raw_text):
    events = []
    event_name = None
    data_lines = []
    for line in raw_text.splitlines():
        if line.startswith("event:"):
            event_name = line[6:].strip()
        elif line.startswith("data:"):
            data_lines.append(line[5:].lstrip())
        elif line == "":
            if event_name is not None:
                data = "\n".join(data_lines)
                try:
                    payload = json.loads(data) if data else {}
                except ValueError:
                    payload = {"raw": data}
                events.append((event_name, payload))
            event_name = None
            data_lines = []
    if event_name is not None:
        data = "\n".join(data_lines)
        try:
            payload = json.loads(data) if data else {}
        except ValueError:
            payload = {"raw": data}
        events.append((event_name, payload))
    return events


def cursor_events_to_text(events):
    parts = []
    result_text = None
    for name, payload in events:
        if name == "assistant" and isinstance(payload, dict) and payload.get("text"):
            parts.append(payload["text"])
        elif name == "result" and isinstance(payload, dict) and payload.get("text"):
            result_text = payload["text"]
    if result_text:
        return result_text
    return "".join(parts)
