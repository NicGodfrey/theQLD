from __future__ import annotations

import json
import unittest
from pathlib import Path

from forced_router.config import load_config, parse_config
from forced_router.rewrite import (
    is_auto_model,
    is_specified_model,
    rewrite_cli_argv,
    rewrite_cursor_agent,
    rewrite_payload,
)

ROOT = Path(__file__).resolve().parents[2]


class RewriteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cfg = load_config(ROOT)

    def test_repo_default_is_fable5(self) -> None:
        self.assertEqual(self.cfg.specified_key, "fable5")
        self.assertEqual(self.cfg.spec.id, "claude-fable-5")

    def test_auto_aliases_are_detected(self) -> None:
        for alias in ("auto", "Auto", "auto-smart", "default", "DEFAULT", "cursor-auto"):
            with self.subTest(alias=alias):
                self.assertTrue(is_auto_model(alias, self.cfg))

    def test_specified_model_matches_variants(self) -> None:
        for value in (
            "claude-fable-5",
            "claude-fable-5-thinking-xhigh",
            "claude-fable-5[effort=xhigh]",
            {"id": "claude-fable-5"},
        ):
            with self.subTest(value=value):
                self.assertTrue(is_specified_model(value, self.cfg))
                self.assertFalse(is_auto_model(value, self.cfg))

    def test_rewrite_auto_to_cli_model(self) -> None:
        out = rewrite_payload({"model": "auto", "messages": []}, self.cfg)
        self.assertEqual(out["model"], "claude-fable-5-thinking-xhigh")

    def test_rewrite_missing_model(self) -> None:
        out = rewrite_payload({"messages": [{"role": "user", "content": "hi"}]}, self.cfg)
        self.assertEqual(out["model"], "claude-fable-5-thinking-xhigh")

    def test_force_all_rewrites_other_models(self) -> None:
        out = rewrite_payload({"model": "grok-4.5"}, self.cfg)
        self.assertEqual(out["model"], "claude-fable-5-thinking-xhigh")

    def test_force_auto_only_leaves_other_models(self) -> None:
        data = json.loads((ROOT / ".cursor" / "forced-model.json").read_text())
        data["policy"]["force_all_api_models"] = False
        cfg = parse_config(data, ROOT / ".cursor" / "forced-model.json")
        out = rewrite_payload({"model": "grok-4.5"}, cfg)
        self.assertEqual(out["model"], "grok-4.5")
        out_auto = rewrite_payload({"model": "auto-smart"}, cfg)
        self.assertEqual(out_auto["model"], "claude-fable-5-thinking-xhigh")

    def test_cloud_agent_create_injects_api_model(self) -> None:
        out = rewrite_cursor_agent({"prompt": {"text": "hi"}, "model": "auto"}, self.cfg)
        self.assertEqual(out["model"]["id"], "claude-fable-5")
        self.assertEqual(out["model"]["params"][0]["value"], "xhigh")

    def test_cli_argv_strips_caller_model(self) -> None:
        argv = rewrite_cli_argv(["agent", "--model", "auto", "-p", "hello"], self.cfg)
        self.assertEqual(
            argv, ["agent", "--model", "claude-fable-5-thinking-xhigh", "-p", "hello"]
        )

    def test_sol_preset_rewrites_auto(self) -> None:
        data = json.loads((ROOT / ".cursor" / "forced-model.json").read_text())
        data["specified_model"] = "sol"
        cfg = parse_config(data, ROOT / ".cursor" / "forced-model.json")
        out = rewrite_payload({"model": "default"}, cfg)
        self.assertEqual(out["model"], "gpt-5.6-sol-xhigh")
        agent = rewrite_cursor_agent({}, cfg)
        self.assertEqual(agent["model"]["id"], "gpt-5.6-sol")


if __name__ == "__main__":
    unittest.main()
