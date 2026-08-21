#!/usr/bin/env python3
"""Start a new Lovart project/task and save the Queensland Legal Directory into it."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

LOVART_DIR = Path(__file__).resolve().parent
REPO_ROOT = LOVART_DIR.parent
DIRECTORY_JSON = LOVART_DIR / "directory.json"
DIRECTORY_BRIEF = LOVART_DIR / "directory.brief.md"
TASK_STATE = LOVART_DIR / "task.json"
SKILL_DIR = Path(os.environ.get("LOVART_SKILL_DIR", "/tmp/lovart-skill"))
SKILL_SCRIPT = SKILL_DIR / "skills" / "lovart-skill" / "scripts" / "agent_skill.py"
SKILL_REPO = "https://github.com/lovartai/lovart-skill.git"


class SaveError(RuntimeError):
    pass


def run_skill(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    if not SKILL_SCRIPT.exists():
        raise SaveError(f"Lovart skill not found at {SKILL_SCRIPT}")
    cmd = [sys.executable, str(SKILL_SCRIPT), *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise SaveError(detail or f"lovart command failed: {' '.join(args)}")
    return result


def ensure_catalog() -> dict:
    extract = LOVART_DIR / "extract_directory.js"
    subprocess.run(["node", str(extract)], cwd=REPO_ROOT, check=True)
    if not DIRECTORY_JSON.exists():
        raise SaveError("directory.json was not created")
    return json.loads(DIRECTORY_JSON.read_text())


def ensure_skill() -> None:
    if SKILL_SCRIPT.exists():
        return
    SKILL_DIR.parent.mkdir(parents=True, exist_ok=True)
    if SKILL_DIR.exists():
        shutil.rmtree(SKILL_DIR)
    subprocess.run(["git", "clone", "--depth", "1", SKILL_REPO, str(SKILL_DIR)], check=True)


def write_task(payload: dict) -> None:
    payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    TASK_STATE.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def parse_json_stdout(result: subprocess.CompletedProcess[str]) -> dict:
    text = (result.stdout or "").strip()
    if not text:
        raise SaveError((result.stderr or "empty Lovart response").strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SaveError(f"Could not parse Lovart output: {text}") from exc


def chat_prompt(catalog: dict) -> str:
    brief = DIRECTORY_BRIEF.read_text() if DIRECTORY_BRIEF.exists() else ""
    return (
        "Start a new task. Persist this Queensland Legal Directory catalog into the "
        "current Lovart project as the canonical directory dataset.\n\n"
        "Do not invent extra organisations. Keep names, contacts, and legal areas exact.\n"
        f"Source site: {catalog.get('sourceSite')}\n"
        f"Entry count: {catalog.get('entryCount')}\n\n"
        "Create a clean directory board / canvas that groups organisations by legal area "
        "and lists each organisation with website, email, phone, and address.\n\n"
        f"{brief}\n"
    )


def save_remote(catalog: dict) -> dict:
    ak = os.environ.get("LOVART_ACCESS_KEY", "").strip()
    sk = os.environ.get("LOVART_SECRET_KEY", "").strip()
    if not ak or not sk:
        raise SaveError(
            "Missing LOVART_ACCESS_KEY / LOVART_SECRET_KEY. "
            "Get them from Lovart Avatar menu -> AK/SK Management."
        )

    config = parse_json_stdout(run_skill(["config", "--json"]))
    created = parse_json_stdout(run_skill(["create-project"]))
    project_id = created.get("project_id")
    if not project_id:
        raise SaveError(f"create-project returned no project_id: {created}")

    run_skill(["project-add", "--project-id", project_id, "--name", "theQLD Legal Directory"])

    uploaded = []
    for local in (DIRECTORY_JSON, DIRECTORY_BRIEF):
        try:
            upload = parse_json_stdout(run_skill(["upload", "--file", str(local)]))
            url = upload.get("url")
            if url:
                uploaded.append({"file": local.name, "url": url})
                run_skill(
                    [
                        "upload-artifact",
                        "--project-id",
                        project_id,
                        "--url",
                        url,
                        "--type",
                        "image",
                    ],
                    check=False,
                )
        except SaveError:
            # JSON/markdown may be rejected by the image-oriented upload endpoint.
            pass

    attachments = [item["url"] for item in uploaded]
    chat_args = [
        "chat",
        "--project-id",
        project_id,
        "--prompt",
        chat_prompt(catalog),
        "--mode",
        "thinking",
        "--json",
        "--download",
        "--output-dir",
        str(LOVART_DIR / "artifacts"),
    ]
    if attachments:
        chat_args.extend(["--attachments", *attachments])
    chat = parse_json_stdout(run_skill(chat_args))

    return {
        "status": "saved",
        "previousConfig": config,
        "projectId": project_id,
        "threadId": chat.get("thread_id"),
        "finalStatus": chat.get("final_status"),
        "generationSucceeded": chat.get("generation_succeeded"),
        "canvasUrl": f"https://www.lovart.ai/canvas?projectId={quote(project_id, safe='')}",
        "uploaded": uploaded,
        "downloaded": chat.get("downloaded") or [],
        "agentMessage": next(
            (
                item.get("text")
                for item in chat.get("items", [])
                if item.get("type") == "assistant" and item.get("text")
            ),
            chat.get("agent_message"),
        ),
        "entryCount": catalog.get("entryCount"),
    }


def main() -> int:
    catalog = ensure_catalog()
    local = {
        "status": "local_saved",
        "title": catalog.get("title"),
        "entryCount": catalog.get("entryCount"),
        "directoryJson": str(DIRECTORY_JSON.relative_to(REPO_ROOT)),
        "directoryBrief": str(DIRECTORY_BRIEF.relative_to(REPO_ROOT)),
        "sourceSite": catalog.get("sourceSite"),
        "exportedAt": catalog.get("exportedAt"),
    }
    write_task(local)

    ensure_skill()
    try:
        remote = save_remote(catalog)
    except SaveError as exc:
        local["status"] = "awaiting_lovart_credentials" if "LOVART_ACCESS_KEY" in str(exc) else "lovart_remote_failed"
        local["remoteError"] = str(exc)
        write_task(local)
        print(json.dumps(local, indent=2, ensure_ascii=False))
        return 2 if local["status"] == "awaiting_lovart_credentials" else 1

    write_task(remote)
    print(json.dumps(remote, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
