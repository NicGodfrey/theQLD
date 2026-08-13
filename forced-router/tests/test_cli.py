from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from forced_router.cli import main
from forced_router.config import load_config
from forced_router.sync_cursor import sync_cursor_files

ROOT = Path(__file__).resolve().parents[2]


class CliTests(unittest.TestCase):
    def test_print_model(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--root", str(ROOT), "print-model"])
        self.assertEqual(code, 0)
        body = json.loads(buf.getvalue())
        self.assertEqual(body["specified_model"], "fable5")
        self.assertEqual(body["cli_model"], "claude-fable-5-thinking-xhigh")

    def test_rewrite_cli(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--root", str(ROOT), "rewrite", '{"model":"auto"}'])
        self.assertEqual(code, 0)
        body = json.loads(buf.getvalue())
        self.assertEqual(body["model"], "claude-fable-5-thinking-xhigh")

    def test_sync_is_idempotent(self) -> None:
        cfg = load_config(ROOT)
        sync_cursor_files(cfg)
        self.assertEqual(sync_cursor_files(cfg), [])
        coder = (ROOT / ".cursor" / "agents" / "forced-coder.md").read_text()
        self.assertIn("model: claude-fable-5[effort=xhigh]", coder)
        self.assertIn("forced-coder", coder)


if __name__ == "__main__":
    unittest.main()
