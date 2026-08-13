from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from forced_router.config import load_config
from forced_router.policy import hook_response

ROOT = Path(__file__).resolve().parents[2]


class PolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cfg = load_config(ROOT)

    def test_blocks_auto_prompt(self) -> None:
        resp = hook_response(
            {
                "hook_event_name": "beforeSubmitPrompt",
                "prompt": "hi",
                "model": "auto",
                "model_id": "default",
            },
            self.cfg,
        )
        self.assertFalse(resp["continue"])
        self.assertIn("Auto", resp["user_message"])

    def test_allows_specified_prompt(self) -> None:
        resp = hook_response(
            {
                "hook_event_name": "beforeSubmitPrompt",
                "prompt": "hi",
                "model": "claude-fable-5-thinking-xhigh",
                "model_id": "claude-fable-5",
            },
            self.cfg,
        )
        self.assertTrue(resp["continue"])

    def test_blocks_other_models(self) -> None:
        resp = hook_response(
            {
                "hook_event_name": "beforeSubmitPrompt",
                "prompt": "hi",
                "model": "cursor-grok-4.6-xhigh-fast",
            },
            self.cfg,
        )
        self.assertFalse(resp["continue"])

    def test_missing_model_allowed_by_default(self) -> None:
        resp = hook_response(
            {"hook_event_name": "beforeSubmitPrompt", "prompt": "hi"},
            self.cfg,
        )
        self.assertTrue(resp["continue"])

    def test_denies_inherit_custom_subagent(self) -> None:
        resp = hook_response(
            {
                "hook_event_name": "subagentStart",
                "subagent_type": "generalPurpose",
                "subagent_model": "inherit",
                "task": "do work",
            },
            self.cfg,
        )
        self.assertEqual(resp["permission"], "deny")

    def test_allows_pinned_custom_subagent(self) -> None:
        resp = hook_response(
            {
                "hook_event_name": "subagentStart",
                "subagent_type": "generalPurpose",
                "subagent_model": "claude-fable-5[effort=xhigh]",
                "task": "do work",
            },
            self.cfg,
        )
        self.assertEqual(resp["permission"], "allow")

    def test_allows_builtin_explore(self) -> None:
        resp = hook_response(
            {
                "hook_event_name": "subagentStart",
                "subagent_type": "explore",
                "subagent_model": "composer-2.5",
                "task": "search",
            },
            self.cfg,
        )
        self.assertEqual(resp["permission"], "allow")

    def test_hook_script_blocks_auto(self) -> None:
        payload = json.dumps(
            {
                "hook_event_name": "beforeSubmitPrompt",
                "prompt": "x",
                "model": "auto-smart",
            }
        )
        proc = subprocess.run(
            [sys.executable, str(ROOT / ".cursor" / "hooks" / "force_model.py")],
            input=payload,
            text=True,
            capture_output=True,
            check=True,
            cwd=str(ROOT),
        )
        body = json.loads(proc.stdout)
        self.assertFalse(body["continue"])


if __name__ == "__main__":
    unittest.main()
