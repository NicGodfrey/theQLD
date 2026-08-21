"""Test doubles for the Atelier spoke suite. No sockets are ever opened:
spokes take a `transport` argument and tests inject FakeTransport."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (ROOT, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from spokes_base import HttpResponse  # noqa: E402  (needs the path bootstrap)

FIXTURES = os.path.join(HERE, "fixtures")


def fixture_bytes(name):
    with open(os.path.join(FIXTURES, name), "rb") as fh:
        return fh.read()


def fixture_json(name):
    return json.loads(fixture_bytes(name).decode("utf-8"))


class Call:
    """One recorded request."""

    def __init__(self, method, url, headers, body, stream):
        self.method = method
        self.url = url
        self.headers = dict(headers or {})
        self.body = body
        self.stream = stream

    def body_json(self):
        return json.loads(self.body.decode("utf-8"))

    def __repr__(self):  # pragma: no cover - debugging aid
        return f"Call({self.method} {self.url} stream={self.stream})"


class FakeTransport:
    """Scripted transport: responses are dequeued in FIFO order and every
    request is recorded for assertions."""

    def __init__(self):
        self.calls = []
        self._queue = []

    # -- scripting ------------------------------------------------------------

    def enqueue(self, body=b"", status=200, headers=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self._queue.append(HttpResponse(status, dict(headers or {}), body))

    def enqueue_json(self, obj, status=200, headers=None):
        self.enqueue(json.dumps(obj), status=status, headers=headers)

    def enqueue_fixture(self, name, status=200, headers=None):
        self.enqueue(fixture_bytes(name), status=status, headers=headers)

    # -- transport interface ----------------------------------------------------

    def request(self, method, url, *, headers=None, body=None,
                timeout=0.0, stream=False):
        self.calls.append(Call(method, url, headers, body, stream))
        if not self._queue:
            raise AssertionError(f"FakeTransport: unexpected request "
                                 f"{method} {url}")
        return self._queue.pop(0)
