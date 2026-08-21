#!/usr/bin/env python3
"""Opus-07 — Round 14 (launcher) verification.

`python3 -m atelier`, an absolute `atelier/__main__.py` and the `atelier`
console script all have to boot from any cwd, print --help without binding a
port, and honour --host/--port over ATELIER_HOST/ATELIER_PORT. Every process
test here runs a real interpreter in a throwaway cwd; every bind test takes an
ephemeral port and shuts the server down before it returns.
"""

from __future__ import annotations

import contextlib
import io
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import tomllib
import unittest
from http.client import HTTPConnection
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atelier.launch import (  # noqa: E402
    DEFAULT_HOST,
    DEFAULT_PORT,
    build_parser,
    ensure_sys_path,
    env_host,
    env_port,
    env_warnings,
    main as launch_main,
    package_dir,
    parse_args,
    repo_root,
)

PYPROJECT = ROOT / "pyproject.toml"


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def clean_env(**extra) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "ATELIER_HOST", "ATELIER_PORT")}
    env.update({k: v for k, v in extra.items() if v is not None})
    return env


def run(args, cwd, env, timeout=30) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)


class Packaging(unittest.TestCase):
    """Claim 1 — the installable surface is the studio, not the lab."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

    def test_console_script_entry_point(self):
        self.assertEqual(self.cfg["project"]["scripts"], {"atelier": "atelier.launch:main"})

    def test_entry_point_target_is_importable_and_callable(self):
        module, _, attr = "atelier.launch:main".partition(":")
        imported = __import__(module, fromlist=[attr])
        self.assertTrue(callable(getattr(imported, attr)))
        self.assertIs(getattr(imported, attr), launch_main)

    def test_requires_python_is_311(self):
        self.assertEqual(self.cfg["project"]["requires-python"], ">=3.11")
        self.assertGreaterEqual(sys.version_info[:2], (3, 11))

    def test_no_third_party_dependencies(self):
        self.assertFalse(self.cfg["project"].get("dependencies"))
        self.assertFalse(self.cfg["project"].get("optional-dependencies"))

    def test_readme_points_at_the_package_readme(self):
        readme = ROOT / self.cfg["project"]["readme"]
        self.assertTrue(readme.is_file(), readme)

    def test_tests_and_research_are_not_the_installable_surface(self):
        try:
            from setuptools import find_packages
        except ImportError:  # pragma: no cover - stdlib-only machine
            self.skipTest("setuptools not available")
        find = self.cfg["tool"]["setuptools"]["packages"]["find"]
        resolved = set(find_packages(where=str(ROOT), include=find["include"], exclude=find["exclude"]))
        self.assertIn("atelier", resolved)
        self.assertIn("atelier.helix", resolved)
        self.assertFalse([p for p in resolved if "tests" in p or "research" in p], resolved)
        # and the excludes are load-bearing: those packages do exist on disk.
        everything = set(find_packages(where=str(ROOT)))
        self.assertIn("atelier.tests", everything)

    def test_package_data_paths_exist(self):
        patterns = self.cfg["tool"]["setuptools"]["package-data"]["atelier"]
        for pattern in patterns:
            self.assertTrue(list((ROOT / "atelier").glob(pattern)), pattern)
        # the web dir, the demo catalogue and the licence all have to ride along
        for needed in ("web/index.html", "data/top100.json", "LICENSE"):
            self.assertTrue(
                any((ROOT / "atelier" / needed).match(f"atelier/{p}") for p in patterns)
                or any(
                    (ROOT / "atelier" / needed) in set((ROOT / "atelier").glob(p)) for p in patterns
                ),
                needed,
            )


class MainModuleBootstrap(unittest.TestCase):
    """Claim 2 — repo root on sys.path before atelier.launch is imported."""

    def test_repo_root_is_cwd_independent(self):
        self.assertEqual(repo_root(), ROOT)
        self.assertEqual(package_dir(), ROOT / "atelier")
        self.assertEqual(ensure_sys_path(), ROOT)
        self.assertIn(str(ROOT), sys.path)
        with tempfile.TemporaryDirectory() as tmp:
            here = os.getcwd()
            os.chdir(tmp)
            try:
                self.assertEqual(repo_root(), ROOT)
            finally:
                os.chdir(here)

    def test_absolute_main_py_runs_with_no_pythonpath(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run([sys.executable, str(ROOT / "atelier" / "__main__.py"), "--help"], tmp, clean_env())
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("--host", proc.stdout)
        self.assertIn("--port", proc.stdout)
        self.assertNotIn("Atelier Helix on http://", proc.stdout)

    def test_the_sys_path_insert_is_what_makes_that_work(self):
        """Control: script mode only gives you atelier/, which cannot import atelier."""
        with tempfile.TemporaryDirectory() as tmp:
            proc = run(
                [
                    sys.executable,
                    "-c",
                    "import sys; sys.path.insert(0, sys.argv[1]); import atelier.launch",
                    str(ROOT / "atelier"),
                ],
                tmp,
                clean_env(),
            )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("ModuleNotFoundError", proc.stderr)


class HelpDoesNotBind(unittest.TestCase):
    """Claim 3 — --help is a print, not a listener."""

    def test_module_help_from_another_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run([sys.executable, "-m", "atelier", "--help"], tmp, clean_env(PYTHONPATH=str(ROOT)))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("--host", proc.stdout)
        self.assertIn("--port", proc.stdout)
        self.assertNotIn("Atelier Helix on http://", proc.stdout)

    def test_help_holds_no_socket(self):
        """Nothing is listening on the default port after --help returns."""
        with tempfile.TemporaryDirectory() as tmp:
            port = free_port()
            proc = run(
                [sys.executable, "-m", "atelier", "--port", str(port), "--help"],
                tmp,
                clean_env(PYTHONPATH=str(ROOT)),
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        with socket.socket() as sock:  # nothing is listening: the connect is refused
            sock.settimeout(5)
            with self.assertRaises(ConnectionRefusedError):
                sock.connect(("127.0.0.1", port))

    def test_help_survives_a_junk_env_port(self):
        """A stale ATELIER_PORT used to take --help down with a ValueError."""
        for junk in ("abc", "8765.5", "", "70000", "0", "-1"):
            with self.subTest(junk=junk), tempfile.TemporaryDirectory() as tmp:
                proc = run(
                    [sys.executable, "-m", "atelier", "--help"],
                    tmp,
                    clean_env(PYTHONPATH=str(ROOT), ATELIER_PORT=junk),
                )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("--port", proc.stdout)
            self.assertNotIn("Traceback", proc.stderr)

    def test_module_help_needs_the_repo_on_the_path(self):
        """Pinned as current behaviour: `-m atelier` is repo-root or installed."""
        with tempfile.TemporaryDirectory() as tmp:
            proc = run([sys.executable, "-m", "atelier", "--help"], tmp, clean_env())
        self.assertEqual(proc.returncode, 1)
        self.assertIn("No module named atelier", proc.stderr)


class EnvAndFlags(unittest.TestCase):
    """Claim 4 — CLI over env over built-in default."""

    def setUp(self):
        self._saved = {k: os.environ.get(k) for k in ("ATELIER_HOST", "ATELIER_PORT")}

    def tearDown(self):
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def _set(self, host=None, port=None):
        for key, value in (("ATELIER_HOST", host), ("ATELIER_PORT", port)):
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_defaults_when_env_is_unset(self):
        self._set()
        args = parse_args([])
        self.assertEqual((args.host, args.port), ("127.0.0.1", 8765))
        self.assertEqual((DEFAULT_HOST, DEFAULT_PORT), ("127.0.0.1", 8765))

    def test_env_supplies_the_default(self):
        self._set(host="0.0.0.0", port="9000")
        args = parse_args([])
        self.assertEqual((args.host, args.port), ("0.0.0.0", 9000))

    def test_cli_beats_env(self):
        self._set(host="0.0.0.0", port="9000")
        args = parse_args(["--host", "127.0.0.1", "--port", "8766"])
        self.assertEqual((args.host, args.port), ("127.0.0.1", 8766))

    def test_help_text_names_both_flags_and_defaults(self):
        self._set()
        help_text = build_parser().format_help()
        self.assertIn("--host", help_text)
        self.assertIn("--port", help_text)
        self.assertIn("127.0.0.1", help_text)
        self.assertIn("8765", help_text)
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed), self.assertRaises(SystemExit) as ctx:
            parse_args(["--help"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("--host", printed.getvalue())

    def test_a_port_that_cannot_bind_is_refused_at_the_flag(self):
        self._set()
        for bad in ("abc", "0", "70000", "-1", "8765.5", ""):
            complaint = io.StringIO()
            with self.subTest(bad=bad), contextlib.redirect_stderr(complaint):
                with self.assertRaises(SystemExit) as ctx:
                    parse_args(["--port", bad])
            self.assertEqual(ctx.exception.code, 2)
            self.assertIn("--port", complaint.getvalue())
        self.assertEqual(parse_args(["--port", "65535"]).port, 65535)
        self.assertEqual(parse_args(["--port", " 1 "]).port, 1)

    def test_a_blank_or_junk_env_falls_back_and_says_so(self):
        self._set(host="   ", port="abc")
        self.assertIsNone(env_host())
        self.assertIsNone(env_port())
        args = parse_args([])
        self.assertEqual((args.host, args.port), (DEFAULT_HOST, DEFAULT_PORT))
        notes = " ".join(env_warnings())
        self.assertIn("ATELIER_HOST", notes)
        self.assertIn("ATELIER_PORT", notes)

    def test_a_good_env_gets_no_warning(self):
        self._set(host="0.0.0.0", port="9000")
        self.assertEqual(env_warnings(), [])
        self._set()
        self.assertEqual(env_warnings(), [])

    def test_an_out_of_range_env_port_does_not_become_the_bind(self):
        self._set(port="70000")
        self.assertIsNone(env_port())
        self.assertEqual(parse_args([]).port, DEFAULT_PORT)

    def test_an_empty_host_flag_does_not_become_bind_all(self):
        self._set()
        self.assertEqual(parse_args(["--host", " "]).host, DEFAULT_HOST)


class ServerMainTakesTheCliValues(unittest.TestCase):
    """Claim 5 — server.main(host=, port=) really binds what it is handed."""

    def setUp(self):
        self._saved = {k: os.environ.get(k) for k in ("ATELIER_HOST", "ATELIER_PORT", "ATELIER_RUNTIME")}
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["ATELIER_RUNTIME"] = self._tmp.name
        os.environ.pop("ATELIER_HOST", None)
        os.environ.pop("ATELIER_PORT", None)

    def tearDown(self):
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self._tmp.cleanup()

    @contextlib.contextmanager
    def serving(self, **kwargs):
        """Run the real server.main in a thread, hand back (server, banner)."""
        from atelier import server as srv

        made: list = []
        original = srv.ThreadingHTTPServer

        class Recording(original):
            def __init__(self, *a, **kw):
                super().__init__(*a, **kw)
                made.append(self)

        srv.ThreadingHTTPServer = Recording
        banner = io.StringIO()
        stdout = sys.stdout

        def serve():
            with contextlib.redirect_stdout(banner):
                srv.main(**kwargs)

        thread = threading.Thread(target=serve, daemon=True)
        try:
            thread.start()
            deadline = time.time() + 10
            while not made and time.time() < deadline:
                time.sleep(0.02)
            self.assertTrue(made, "server never bound")
            yield made[0], banner
        finally:
            srv.ThreadingHTTPServer = original
            if made:
                made[0].shutdown()
            thread.join(timeout=10)
            sys.stdout = stdout
            self.assertFalse(thread.is_alive(), "server thread outlived the test")

    def get(self, port, path="/api/health", host_header=None):
        conn = HTTPConnection("127.0.0.1", port, timeout=10)
        try:
            headers = {"Host": host_header} if host_header else {}
            conn.request("GET", path, headers=headers)
            response = conn.getresponse()
            return response.status, response.read().decode("utf-8", "replace")
        finally:
            conn.close()

    def test_main_binds_the_port_it_is_given(self):
        port = free_port()
        with self.serving(host="127.0.0.1", port=port) as (server, banner):
            self.assertEqual(server.server_address[1], port)
            status, body = self.get(port)
        self.assertEqual(status, 200)
        self.assertIn('"ok": true', body)
        self.assertIn(f"Atelier Helix on http://127.0.0.1:{port}", banner.getvalue())

    def test_the_banner_reports_the_port_actually_bound(self):
        with self.serving(host="127.0.0.1", port=0) as (server, banner):
            real = server.server_address[1]
            self.assertNotEqual(real, 0)
            status, _ = self.get(real)
        self.assertEqual(status, 200)
        self.assertIn(f":{real}", banner.getvalue())

    def test_cli_host_reaches_the_host_guard(self):
        """--host 0.0.0.0 used to bind the LAN and then 403 every LAN client."""
        with self.serving(host="0.0.0.0", port=0) as (server, _):
            port = server.server_address[1]
            self.assertEqual(os.environ["ATELIER_HOST"], "0.0.0.0")
            self.assertEqual(self.get(port, host_header=f"192.168.1.50:{port}")[0], 200)
            self.assertEqual(self.get(port, host_header="127.0.0.1")[0], 200)

    def test_the_local_bind_still_refuses_a_foreign_host_header(self):
        with self.serving(host="127.0.0.1", port=0) as (server, _):
            port = server.server_address[1]
            status, body = self.get(port, host_header="evil.example")
        self.assertEqual(status, 403)
        self.assertIn("bad_host", body)

    def test_an_unbindable_port_is_a_clean_exit_not_a_traceback(self):
        from atelier import server as srv

        with socket.socket() as hog:
            hog.bind(("127.0.0.1", 0))
            hog.listen(1)
            busy = hog.getsockname()[1]
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as ctx:
                srv.main(host="127.0.0.1", port=busy)
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("cannot bind", err.getvalue())

        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as ctx:
            srv.main(host="127.0.0.1", port=70000)
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("cannot bind", err.getvalue())


class EndToEndProcess(unittest.TestCase):
    """The whole path: a real interpreter, a real socket, a real shutdown."""

    def test_module_serves_then_stops(self):
        port = free_port()
        with tempfile.TemporaryDirectory() as tmp:
            env = clean_env(PYTHONPATH=str(ROOT), ATELIER_RUNTIME=str(Path(tmp) / "rt"))
            proc = subprocess.Popen(
                [sys.executable, "-m", "atelier", "--host", "127.0.0.1", "--port", str(port)],
                cwd=tmp,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                banner = proc.stdout.readline().strip()
                self.assertEqual(banner, f"Atelier Helix on http://127.0.0.1:{port}")
                conn = HTTPConnection("127.0.0.1", port, timeout=10)
                conn.request("GET", "/api/health")
                response = conn.getresponse()
                self.assertEqual(response.status, 200)
                self.assertIn('"ok": true', response.read().decode())
                conn.close()
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:  # pragma: no cover
                    proc.kill()
                    proc.wait(timeout=10)
                proc.stdout.close()
                proc.stderr.close()
        self.assertIsNotNone(proc.poll())

    def test_env_port_drives_the_bind_when_no_flag_is_given(self):
        port = free_port()
        with tempfile.TemporaryDirectory() as tmp:
            env = clean_env(
                PYTHONPATH=str(ROOT),
                ATELIER_RUNTIME=str(Path(tmp) / "rt"),
                ATELIER_HOST="127.0.0.1",
                ATELIER_PORT=str(port),
            )
            proc = subprocess.Popen(
                [sys.executable, "-m", "atelier"],
                cwd=tmp,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                self.assertEqual(
                    proc.stdout.readline().strip(), f"Atelier Helix on http://127.0.0.1:{port}"
                )
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:  # pragma: no cover
                    proc.kill()
                    proc.wait(timeout=10)
                proc.stdout.close()
                proc.stderr.close()

    def test_a_bad_port_flag_exits_2_without_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run(
                [sys.executable, "-m", "atelier", "--port", "70000"],
                tmp,
                clean_env(PYTHONPATH=str(ROOT), ATELIER_RUNTIME=str(Path(tmp) / "rt")),
            )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--port", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
