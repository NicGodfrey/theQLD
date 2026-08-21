# Opus-07 · R14 launcher — verified

Verifier: one live `claude-opus-5-thinking-high-fast` agent, branch
`cursor/atelier-byok-studio-d639`, HEAD at `2027543` (Round 14).
Method: real interpreters in throwaway cwds, a real `pip wheel` and
`pip install -e .` into a scratch venv, and real `ThreadingHTTPServer` binds on
ephemeral ports that are shut down inside the test that opened them. Demo lane
only — no network, no key read, no paid call.

**Verdict: PASS with fixes.** All five claims held as shipped: the console
script is declared and resolves, `__main__.py`'s `sys.path` insert is
load-bearing, `--help` prints the flags and binds nothing, the flags beat the
env vars, and `server.main(host=, port=)` binds what the CLI hands it. What did
not hold was everything *around* those values: two environment variables could
take `--help` down or quietly publish the studio to the LAN, an out-of-range
port reached the socket layer as a traceback, and `--host` was wired to the
bind but not to the Host guard, so the one flag that opens the studio to the
LAN also broke it.

## Claim by claim

| # | Claim | Verdict |
|---|-------|---------|
| 1 | `[project.scripts] atelier = "atelier.launch:main"`, `requires-python >=3.11`, research/tests not the installable surface | PASS, proven against a built wheel |
| 2 | `__main__.py` puts the repo root on `sys.path` before importing `atelier.launch`; absolute path works from any cwd | PASS, and the insert is what makes it work |
| 3 | `python3 -m atelier --help` from a temp cwd exits 0, prints the flags, does not bind | PASS, with a junk-env crash closed |
| 4 | `--host` / `--port` override `ATELIER_HOST` / `ATELIER_PORT`; defaults 127.0.0.1 / 8765 | PASS, with three env holes closed |
| 5 | `server.main(host=, port=)` accepts the CLI values | PASS, with the Host guard rewired to match |

## Path traced

`atelier --host H --port P` → console script shim → `atelier.launch:main` →
`ensure_sys_path()` (repo root at `sys.path[0]`, a no-op once installed) →
`parse_args` (argparse default = env, CLI wins) → `env_warnings()` to stderr →
lazy `from atelier.server import main as serve` — lazy is why `--help` never
touches sqlite, the keyring or the spokes — → `server.main` resolves
host/port once more for direct callers, publishes the resolved host into
`ATELIER_HOST` so `_check_host` and the bind agree, constructs
`ThreadingHTTPServer`, prints the banner from `server_address`, then
`serve_forever()` with `server_close()` in a `finally`.

`python3 -m atelier` takes the same path through `atelier/__main__.py`, whose
four-line `sys.path` prologue runs *before* `from atelier.launch import main`.

## Packaging evidence (claim 1)

`pip wheel --no-build-isolation --no-index` against the live tree, then the
wheel listed. Not a string search over `pyproject.toml` — the actual artefact:

```
atelier_helix-0.1.0-py3-none-any.whl        34 entries
  atelier/{__init__,__main__,launch,server}.py
  atelier/helix/*.py  atelier/helix/spokes/*.py
  atelier/web/{index.html,app.js,styles.css}  atelier/data/*.json
  atelier/{README.md,OUTPUT_RIGHTS.md,LICENSE}
  atelier_helix-0.1.0.dist-info/entry_points.txt
tests in wheel:     []
research in wheel:  []
Requires-Python: >=3.11        Requires-Dist: None
```

`setuptools.find_packages` with the declared include/exclude resolves to
`{atelier, atelier.helix, atelier.helix.spokes}`; without the excludes the same
scan finds `atelier.tests` and `atelier.tests.evolve`, so the excludes are
doing work. `atelier/integrations/` is two markdown files, not a package.

Then a real `pip install -e .` into a `--system-site-packages` venv, and the
installed script run from `/tmp/probe/away` with `PYTHONPATH`, `ATELIER_HOST`
and `ATELIER_PORT` scrubbed:

```
$ atelier --help                     # cwd=/tmp/probe/away, no PYTHONPATH
usage: atelier [-h] [--host HOST] [--port PORT]        rc=0
entry point: EntryPoint(name='atelier', value='atelier.launch:main',
                        group='console_scripts')  -> <function main>
$ atelier --host 127.0.0.1 --port 44953
Atelier Helix on http://127.0.0.1:44953
GET /api/health -> 200 {"ok": true, "name": "atelier", ...}   # then SIGTERM
```

## Bootstrap evidence (claim 2)

From `/tmp/probe`, `PYTHONPATH` unset, no install:

```
$ python3 /workspace/atelier/__main__.py --help     rc=0, prints both flags
$ python3 -m atelier --help                          rc=1
  /usr/bin/python3: No module named atelier
control: sys.path.insert(0, '/workspace/atelier')    # what script mode gives you
         import atelier.launch -> ModuleNotFoundError: No module named 'atelier'
```

The control is the point: script mode puts `atelier/` — not the repo root — on
`sys.path`, so without the prologue the absolute-path route cannot import its
own package. `-m atelier` without the repo root on the path is *not* a hole to
fix in `__main__.py`; `-m` resolves the package before any of our code runs.
It is repo-root-cwd or installed, and it is now pinned as such and documented.

## Host and port evidence (claims 3–5)

Every line below is captured from a real process or a real socket. The first
column of each pair is the shipped `2027543` behaviour, the second is now.

```
ATELIER_PORT=abc  atelier --help
  before  ValueError: invalid literal for int() with base 10: 'abc'   rc=1
  after   usage: atelier [-h] ...                                     rc=0
          stderr: atelier: ATELIER_PORT='abc' is not a port in 1-65535 — using 8765

atelier --port 70000            (also 0, -1)
  before  OverflowError: bind(): port must be 0-65535   (traceback, rc=1)
  after   atelier: error: argument --port: 70000 is outside 1-65535    rc=2

ATELIER_HOST= (set, empty)  atelier
  before  bound ('0.0.0.0', 36661) on every interface, and
          GET /api/health  Host: attacker.example -> 200 {"ok": true, ...}
  after   Atelier Helix on http://127.0.0.1:39683
          GET /api/health  Host: attacker.example -> 403 {"code":"bad_host"}
          stderr: atelier: ATELIER_HOST is blank — binding 127.0.0.1

atelier --host 0.0.0.0          (ATELIER_HOST unset)
  before  bind 0.0.0.0, then  Host:192.168.1.50 -> 403  Host:studio.local -> 403
          (i.e. bound to the LAN and refused every LAN client)
  after   Host:192.168.1.50 -> 200   Host:127.0.0.1 -> 200
          stderr: atelier: 0.0.0.0 is reachable off this machine — the Host guard is off

port already in use
  before  OSError: [Errno 98] Address already in use   (traceback)
  after   atelier: cannot bind 127.0.0.1:41273 — Address already in use   rc=1
```

`--help` binds nothing, checked by connecting rather than by reading output:
after `python3 -m atelier --port <free> --help` returns 0, a connect to that
port is `ConnectionRefusedError`, and stdout never contains
`Atelier Helix on http://`.

Precedence, resolved through the real parser:

```
env unset                      -> ('127.0.0.1', 8765)
ATELIER_HOST=0.0.0.0 PORT=9000 -> ('0.0.0.0', 9000)
  ... plus --host 127.0.0.1 --port 8766 -> ('127.0.0.1', 8766)
ATELIER_PORT=70000             -> 8765   (out of range never becomes the bind)
--host " "                     -> 127.0.0.1
```

## Holes found and closed

1. **A stale `ATELIER_PORT` killed `--help`.** The env default was read with a
   bare `int(...)` at parser-construction time, so `ATELIER_PORT=abc` — or
   `8765.5`, or a shell that exports the variable empty — turned the one
   command that is supposed to be safe into a `ValueError` traceback with
   exit 1. `env_port()` now returns `None` for anything unusable and the
   built-in default takes over, with a note on stderr when the studio actually
   launches. `--help` output stays clean; the exit code stays 0.
2. **A blank `ATELIER_HOST` published the studio with the guard off.** `""`
   binds `INADDR_ANY`, and `_check_host` only enforces the Host header when the
   bind is in `{127.0.0.1, localhost, ::1}` — an empty string is in neither
   set, so a set-but-empty variable (a sloppy `.env`, `ATELIER_HOST= atelier`)
   both exposed every interface and switched off the only guard. Captured
   above: `Host: attacker.example -> 200`. Blank now resolves to `127.0.0.1`
   on the way in, and `_check_host` strips and defaults on the way out, so a
   blank value cannot mean "bind the world" from either side.
3. **`--host` reached the bind but not the guard.** `_check_host` reads
   `ATELIER_HOST` from the environment, which the flag never set. So
   `atelier --host 0.0.0.0` — the documented way to ask for LAN access — bound
   `0.0.0.0` and then answered 403 to every request that arrived with a real
   LAN Host header. The flag was half-wired: it opened the port and closed the
   door. `main` now publishes the resolved host into `ATELIER_HOST` before the
   socket exists, so bind and guard always agree. The bind is not rewritten —
   if you ask for `0.0.0.0` you get `0.0.0.0`, plus one stderr line saying the
   guard is off.
4. **An unbindable port was a traceback.** `--port 70000` / `0` / `-1` sailed
   through `type=int` into the socket layer (`OverflowError` from `bind()`),
   and a port already in use raised `OSError` out of `main`. Ports are now
   validated at the flag (`argparse` error, exit 2, nothing constructed) and a
   bind that still fails prints one line and exits 1. `0` is refused at the
   CLI because the banner and the Host guard both need the port the user asked
   for; `server.main(port=0)` still works for embedders and tests.
5. **The banner could lie.** It printed the *requested* host and port rather
   than `server_address`, so an ephemeral bind advertised `http://127.0.0.1:0`.
   It now reports what the socket actually got, and brackets an IPv6 literal.
6. **The listener was never closed.** `serve_forever` was wrapped for
   `KeyboardInterrupt` but nothing called `server_close()`, so Ctrl-C left the
   socket to the interpreter's exit. Now a `finally`.
7. **The wheel shipped no licence.** `atelier/LICENSE` exists in the tree and
   was not in `package-data`, so it was absent from the built wheel while
   `OUTPUT_RIGHTS.md` rode along. One line; the wheel above now carries it.

### Checked and *not* a hole

- **`atelier.research` / `atelier.tests` are already out of the wheel**, and
  neither is even a package (`research/` has no `__init__.py`). The exclude
  patterns cover `atelier.tests*`, which is what `find_packages` actually
  finds.
- **No third-party dependencies.** `[project]` has no `dependencies` and no
  `optional-dependencies`; the installed dist reports `Requires-Dist: None`.
  Stdlib-only survives the round.
- **`--help` does not import the server.** `atelier.launch` imports
  `atelier.server` inside `main`, after parsing, so `--help` never opens the
  runtime dir, sqlite or the keyring. Left as is deliberately.
- **`0.0.0.0` is not rewritten.** The user is allowed to ask for it; the change
  is that asking now works and says so.
- **`python3 atelier/server.py` still runs** — `server.py` has had its own
  repo-root `sys.path` insert since before this round, so the new lazy
  `from atelier.launch import ...` inside `main` resolves.

## Evidence that the tests bite

The suite imports `DEFAULT_HOST` / `env_host` / `env_port` / `env_warnings`,
so against the shipped `2027543` launcher it fails at import — 0 of 31 run.
Reverting one product file at a time is the honest measure:

- `atelier/server.py` reverted, everything else new: **3 fail** —
  `test_cli_host_reaches_the_host_guard`,
  `test_the_banner_reports_the_port_actually_bound`,
  `test_an_unbindable_port_is_a_clean_exit_not_a_traceback`.
- `atelier/launch.py` guards reverted (`type=int`, eager `int(os.environ…)`):
  **7 fail** — the junk-env `--help` subprocess, the out-of-range flag, the
  out-of-range env, the blank `--host`, the fallback warnings, and the
  end-to-end `--port 70000` process.
- `pyproject.toml` reverted: **1 fail** — `test_package_data_paths_exist`
  (no licence in the shipped surface).

## Tests

`atelier/tests/evolve/test_opus_07.py` — was 5 tests across three classes, all
of them substring checks over `pyproject.toml` / `__main__.py` plus one
`--help` subprocess; now **31 across six classes**. What changed in kind:
claim 1 is now checked against a `tomllib` parse plus a real `find_packages`
resolution rather than `assertIn('atelier = "atelier.launch:main"', text)`;
claim 2 carries a *control* proving the `sys.path` insert is load-bearing;
claim 5 drives the real `server.main` in a thread (via a recording
`ThreadingHTTPServer` subclass) and over a real socket, and every bind takes an
ephemeral port and is shut down in the same test — the context manager asserts
the serving thread is dead before it returns.
`Round14Launcher` in `atelier/tests/test_evolve.py` still passes untouched.

```
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve \
    atelier.tests.evolve.test_opus_07
Ran 67 tests — OK
```

Full tree (`unittest discover -s atelier/tests`): 298 tests, OK
(1 expected failure, pre-existing).

## Folded after this note (conductor close)

No further launcher code. Remaining items are install-path / process-model,
not bind bugs.

## Remaining holes

- `python3 -m atelier` still needs the repo root on `sys.path` — cwd at the
  repo root, `PYTHONPATH`, or an install. `__main__.py` cannot fix that; `-m`
  resolves the package before any of our code runs. Pinned by a test and now
  stated in the README rather than implied.
- `--host` is not resolved or validated. A typo binds nothing useful and comes
  back as `cannot bind …: Name or service not known`, which is at least a
  clean exit now, but there is no allow-list and no warning for a hostname
  that resolves off-box.
- Nothing stops two studios sharing one `ATELIER_RUNTIME`. The second gets a
  clean "address already in use" only when it also shares the port.
- `pip install -e .` was exercised here in a scratch venv with
  `--no-build-isolation --no-index`; a cold, network-isolated machine with no
  system `setuptools` is untested.
- The Host guard is still keyed off an environment variable rather than the
  server object, which is why claim 5 needed rewiring at all. That is fine for
  one process per machine and fragile the day the handler is reused. Not
  R14 work.
