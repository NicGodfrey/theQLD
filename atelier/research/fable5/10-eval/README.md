# 10-eval — Atelier Helix test & evaluation harness (Fable5#10)

Offline, keyless verification for the Atelier Helix fleet: store schema,
conductor parsing/routing, usage ledger, demo loom, and canvas pinning.

## Contents

| file | purpose |
|------|---------|
| `test_helix.py` | Runnable unittest suite (58 tests) + `--eval` qualitative scorecard. Auto-binds to the real fleet components; falls back to the bundled reference where a component is missing. |
| `helix_ref.py` | Reference implementation of `05-conductor/PROTOCOL.md` with deterministic scripted spokes — the executable spec the tests were written against, and the offline demo-loom runner. |
| `fixtures/` | Four sample briefs: logo, poster, fact-sheet layout for The Queensland Legal Directory (with real entries), brand-kit apply. See `fixtures/README.md` for the schema. |
| `EVAL.md` | Qualitative evaluation: rubric, 2026-08-21 results (40/40), brief→plan commentary, routing matrix, canvas-pin findings, gaps. |
| `ACCEPTANCE_CHECKLIST.md` | Component acceptance checklist with the verifying test named per item, plus the sign-off gate. |

## Run

```bash
cd /tmp/atelier-fable/10-eval
python3 test_helix.py -v        # unit suite — stdlib only, no keys, no network
python3 test_helix.py --eval    # qualitative scorecard (markdown to stdout)
```

Point the harness elsewhere with environment variables:

```bash
ATELIER_ROOT=/path/to/fleet python3 test_helix.py          # whole fleet root
ATELIER_CONDUCTOR=/path/to/conductor.py python3 test_helix.py
ATELIER_SCHEMA=... ATELIER_USAGE=... ATELIER_LOOM=... python3 test_helix.py
```

Missing components skip their classes with an explanatory reason (except the
conductor, which falls back to `helix_ref.py`), so the suite exits green at
any stage of fleet integration and tightens automatically as siblings ship.

## Guarantees enforced

- **No live keys, no network**: provider key env vars are scrubbed in setup
  and `socket.socket.connect` is monkeypatched to fail during every demo run.
- **Determinism**: demo runs with a fixed run id and injected clock are
  byte-identical, per PROTOCOL.md §5.
- **Not vacuous**: a mutation check (deliberately misrouting conductor) makes
  the routing tests fail — recorded in `EVAL.md` §5.
