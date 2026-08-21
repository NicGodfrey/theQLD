#!/usr/bin/env python3
"""Opus-07 — Round 14 (launcher) verification.

`python3 -m atelier` and the `atelier` console script both have to boot
from any cwd, print --help without binding a port, and honour --host/--port.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.launch import build_parser, ensure_sys_path, parse_args, repo_root  # noqa: E402


class LauncherFiles(unittest.TestCase):
    def test_pyproject_console_script(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("[project.scripts]", text)
        self.assertIn('atelier = "atelier.launch:main"', text)
        self.assertIn('readme = "atelier/README.md"', text)

    def test_main_module_bootstraps_repo_root(self):
        main_py = (ROOT / "atelier" / "__main__.py").read_text(encoding="utf-8")
        self.assertIn("sys.path", main_py)
        self.assertIn("atelier.launch", main_py)
        self.assertEqual(repo_root(), ROOT)
        self.assertEqual(ensure_sys_path(), ROOT)


class LauncherArgs(unittest.TestCase):
    def test_help_and_defaults(self):
        parser = build_parser()
        help_text = parser.format_help()
        self.assertIn("--host", help_text)
        self.assertIn("--port", help_text)
        with self.assertRaises(SystemExit) as ctx:
            parse_args(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_cli_overrides_env(self):
        saved = {k: os.environ.get(k) for k in ("ATELIER_HOST", "ATELIER_PORT")}
        os.environ["ATELIER_HOST"] = "0.0.0.0"
        os.environ["ATELIER_PORT"] = "9000"
        try:
            env_args = parse_args([])
            self.assertEqual((env_args.host, env_args.port), ("0.0.0.0", 9000))
            cli = parse_args(["--host", "127.0.0.1", "--port", "8766"])
            self.assertEqual((cli.host, cli.port), ("127.0.0.1", 8766))
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


class LauncherProcess(unittest.TestCase):
    def test_module_help_from_another_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, "-m", "atelier", "--help"],
                cwd=tmp,
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "PYTHONPATH": str(ROOT)},
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("--port", proc.stdout)
        self.assertNotIn("Atelier Helix on http://", proc.stdout)


if __name__ == "__main__":
    unittest.main()
