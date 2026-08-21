"""Atelier -> ComfyUI worker client. Stdlib only, HTTP polling, no websockets.

License boundary (ADAPTERS.md #4): ComfyUI is GPL-3.0 and runs as a SEPARATE,
user-installed process. This module contains zero ComfyUI code — it only speaks
ComfyUI's HTTP job API:

    POST /prompt              queue a workflow graph (API format JSON)
    GET  /history/{id}        job status + output metadata
    GET  /view?...            download an output image
    POST /upload/image        upload an input image (img2img/inpaint)
    GET  /object_info         capability probe (models, samplers, nodes)
    POST /interrupt           cancel the running job

Workflow templates are Atelier-authored API-format JSON with string placeholders
like "{prompt}" / "{seed}"; they are our data, under our license.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass


class ComfyError(RuntimeError):
    pass


@dataclass
class ComfyImage:
    filename: str
    subfolder: str
    folder_type: str
    data: bytes


class ComfyClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8188", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client_id = uuid.uuid4().hex

    # -- low-level ----------------------------------------------------------

    def _get(self, path: str) -> bytes:
        with urllib.request.urlopen(self.base_url + path, timeout=self.timeout) as r:
            return r.read()

    def _post_json(self, path: str, payload: dict) -> dict:
        req = urllib.request.Request(
            self.base_url + path,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            body = r.read()
        return json.loads(body) if body else {}

    # -- API surface ---------------------------------------------------------

    def is_available(self) -> bool:
        try:
            self._get("/system_stats")
            return True
        except OSError:
            return False

    def object_info(self) -> dict:
        """Capability probe: which nodes/checkpoints/samplers this worker has."""
        return json.loads(self._get("/object_info"))

    def queue(self, workflow: dict) -> str:
        """Queue an API-format workflow graph; returns the prompt id."""
        resp = self._post_json("/prompt", {"prompt": workflow, "client_id": self.client_id})
        if "prompt_id" not in resp:
            raise ComfyError(f"queue rejected: {resp}")
        return resp["prompt_id"]

    def wait(self, prompt_id: str, *, poll_s: float = 0.5, timeout_s: float = 600.0) -> dict:
        """Poll /history until the job completes; returns its history entry."""
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            history = json.loads(self._get(f"/history/{prompt_id}"))
            entry = history.get(prompt_id)
            if entry:
                status = entry.get("status", {})
                if status.get("status_str") == "error":
                    raise ComfyError(f"workflow failed: {status.get('messages')}")
                if entry.get("outputs"):
                    return entry
            time.sleep(poll_s)
            poll_s = min(poll_s * 1.5, 3.0)
        self.interrupt()
        raise ComfyError(f"timed out after {timeout_s}s waiting for {prompt_id}")

    def fetch_images(self, history_entry: dict) -> list[ComfyImage]:
        images: list[ComfyImage] = []
        for node_output in history_entry.get("outputs", {}).values():
            for meta in node_output.get("images", []):
                qs = urllib.parse.urlencode(
                    {
                        "filename": meta["filename"],
                        "subfolder": meta.get("subfolder", ""),
                        "type": meta.get("type", "output"),
                    }
                )
                images.append(
                    ComfyImage(
                        filename=meta["filename"],
                        subfolder=meta.get("subfolder", ""),
                        folder_type=meta.get("type", "output"),
                        data=self._get(f"/view?{qs}"),
                    )
                )
        return images

    def interrupt(self) -> None:
        try:
            self._post_json("/interrupt", {})
        except OSError:
            pass

    # -- convenience ---------------------------------------------------------

    def run(self, workflow: dict, *, timeout_s: float = 600.0) -> list[ComfyImage]:
        return self.fetch_images(self.wait(self.queue(workflow), timeout_s=timeout_s))


def fill_template(template: dict, params: dict[str, object]) -> dict:
    """Substitute "{name}" placeholders anywhere in an Atelier workflow template.

    Whole-string placeholders keep the parameter's native type (so "{seed}"
    becomes an int, not a string); embedded placeholders do str substitution.
    """

    def walk(node: object) -> object:
        if isinstance(node, dict):
            return {k: walk(v) for k, v in node.items()}
        if isinstance(node, list):
            return [walk(v) for v in node]
        if isinstance(node, str):
            if node.startswith("{") and node.endswith("}") and node[1:-1] in params:
                return params[node[1:-1]]
            out = node
            for key, val in params.items():
                out = out.replace("{%s}" % key, str(val))
            return out
        return node

    return walk(template)  # type: ignore[return-value]


if __name__ == "__main__":
    # Offline self-test of template filling (no worker required).
    tpl = {
        "3": {"class_type": "KSampler", "inputs": {"seed": "{seed}", "steps": 20}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "photo of {prompt}"}},
    }
    filled = fill_template(tpl, {"seed": 42, "prompt": "a lighthouse"})
    assert filled["3"]["inputs"]["seed"] == 42  # native int preserved
    assert filled["6"]["inputs"]["text"] == "photo of a lighthouse"
    print("comfy_client template self-test OK")

    client = ComfyClient()
    print("worker reachable:", client.is_available())
