# Fable-09 · R17 CI — verified

Verifier: one live `claude-fable-5-thinking-high` agent, branch
`cursor/atelier-byok-studio-d639`, HEAD at `a0b6ba5` (Round 17).
Method: read `.github/workflows/atelier.yml` as text (stdlib only, no
PyYAML — an indentation-aware block walk in the tightened fable-09 test);
run the release gate and the legion discover locally against the live
tree; mutation-test the tightened checks against seven sabotaged copies of
the workflow. No external network, no key read, no paid call, no live-key
smoke job added.

**Verdict: PASS with fixes.** All five claims held as shipped — the
workflow is exactly the two-job, three-trigger, keyless file the round
promised. What did not fully hold was the *pinning*: the shipped fable-09
test was substring greps over the whole file (a `pyproject.toml` mention
anywhere satisfied "trigger"; a job renamed or a third job added passed
silently; `env:` smuggling was invisible), and the release-gate meta test
`Round17to20Meta.test_ci_workflow_exists` — which claim 5 says pins the
above — checked neither `secrets.` nor the workflow self-trigger nor the
name/runner/Python pins of claim 1. Both tightened; no workflow change was
needed.

## Claim by claim

| # | Claim | Verdict |
|---|-------|---------|
| 1 | `atelier.yml` exists, `name: atelier`, Python `"3.11"`, `ubuntu-latest` | PASS — first line is `name: atelier`; both jobs pin `runs-on: ubuntu-latest` and `python-version: "3.11"` via `actions/setup-python@v5` |
| 2 | Two jobs: `gate` runs `python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve`; `legion` runs `python3 -m unittest discover -s atelier/tests/evolve` | PASS — exactly `[gate, legion]` under `jobs:`, one `run:` line each, verbatim |
| 3 | Path triggers `atelier/**`, `pyproject.toml`, `.github/workflows/atelier.yml` on both `push` and `pull_request` | PASS — all three listed under `on.push.paths` *and* `on.pull_request.paths` |
| 4 | No `OPENAI_API_KEY` / `GEMINI_API_KEY` / `secrets.` — CI spends no quota | PASS — case-insensitive scan finds none of those, no `ANTHROPIC_API_KEY`, and no `env:` block anywhere |
| 5 | `Round17to20Meta.test_ci_workflow_exists` pins the above; legion is green locally | PASS with fixes — shipped meta test pinned the run commands, `pyproject.toml`, and the two key names, but not `secrets.`, the self-trigger, `name: atelier`, `ubuntu-latest`, or `"3.11"`; now it pins all of them. Legion discover ran locally: green |

## Path traced

`on:` has exactly two events. `push.paths` and `pull_request.paths` each
list `"atelier/**"`, `"pyproject.toml"`, `".github/workflows/atelier.yml"`
— so any change to the code under test, the packaging metadata, or the
workflow itself re-runs CI on both the branch push and the PR, and the
workflow cannot be edited without CI seeing the edit. Changes touching
*only* unrelated files (README at repo root, other workflows) skip both
jobs — intentional, documented below.

`jobs:` holds `gate` and `legion` and nothing else. Each is four steps of
the same shape: `actions/checkout@v4`, `actions/setup-python@v5` pinned to
`python-version: "3.11"` on `runs-on: ubuntu-latest`, then a single `run:`.
The gate's run line is verbatim
`python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve`;
the legion's is `python3 -m unittest discover -s atelier/tests/evolve`.
Both suites are stdlib-only and fully mocked/loopback, so bare checkout +
setup-python with no `pip install` is sufficient — there is no dependency
step to drift.

Nothing in the file references a provider key, `secrets.`, or even an
`env:` block, so no runner ever holds a credential and no CI minute can
turn into API spend. The belt is two-layer: `CIWorkflow` in
`test_fable_09.py` (legion job) checks structure, and
`Round17to20Meta.test_ci_workflow_exists` in `test_evolve.py` (gate job)
re-checks the same pins — each job guards the file that defines the other,
so hollowing out either job trips the survivor.

## Evidence

Live workflow at `a0b6ba5` (last touched by that commit, per
`git log -- .github/workflows/atelier.yml`): 34 lines, structure as
traced above. Key/secret scan:

```
grep -iE "OPENAI_API_KEY|GEMINI_API_KEY|ANTHROPIC_API_KEY|secrets\.|env:" .github/workflows/  → no matches
ls .github/workflows/  → atelier.yml   (only workflow in the repo)
```

Both CI commands run locally against the live tree (host Python 3.12.3 —
the workflow pins 3.11; nothing in the suites is version-sensitive between
the two):

```
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve \
    atelier.tests.evolve.test_fable_09
Ran 43 tests — OK          (40 before tightening, also OK)

python3 -m unittest discover -s atelier/tests/evolve
Ran 282 tests — OK (expected failures=1, pre-existing)
                           (279 before tightening, also OK)
```

Mutation check — seven sabotaged copies of the workflow, each run through
the tightened fable-09 suite; every one must fail at least one test:

```
BITES  drop pull_request paths                 1 test failed
BITES  rename gate job                         2 tests failed
BITES  gate runs only helix (drops evolve)     1 test failed
BITES  legion job on 3.10                      1 test failed
BITES  smuggle env: OPENAI_API_KEY from secrets  1 test failed
BITES  extra third job appended                1 test failed
BITES  drop workflow self-trigger from push    1 test failed
```

The shipped (pre-tightening) test would have missed "rename gate job",
"extra third job", "drop pull_request paths" (paths only needed to appear
once anywhere), and "drop workflow self-trigger" entirely.

## Holes found and closed

**Substring pins instead of structural pins.** Shipped
`test_fable_09.py` grepped the whole file: `pyproject.toml` appearing
*anywhere* satisfied the trigger check, so the same path under `push` only
— or in a comment — passed; job names were never asserted, so `gate` could
be renamed or a third job (a future live-key smoke job) appended without a
test noticing; `secrets.` was checked but `env:` was not, and the check
was case-sensitive. Now a stdlib indentation walk (`block()`) extracts
`on.push.paths`, `on.pull_request.paths`, `jobs.gate`, `jobs.legion`;
asserts the job list is exactly `["gate", "legion"]`; asserts each job's
`run:` lines equal exactly the one expected command; and the key scan is
case-insensitive and also refuses any `env:` block. 7 tests, up from 4.

**The release-gate meta test under-pinned claim 5.**
`Round17to20Meta.test_ci_workflow_exists` did not check `secrets.`, the
`.github/workflows/atelier.yml` self-trigger, `name: atelier`,
`runs-on: ubuntu-latest`, or `python-version: "3.11"`. Five assertions
added, so the gate job now pins everything claims 1–4 name even if the
legion job is skipped or hollowed out.

### Checked and *not* a hole

- **Path filters skip CI when only unrelated files change** — intentional
  per the round brief; the three filters cover everything either suite
  reads.
- **`actions/checkout` / `setup-python` pinned by major tag, not SHA** —
  matches upstream convention; both are GitHub-owned actions. Noted below.
- **No `pip install` step** — correct, not an omission: both suites import
  stdlib plus the in-repo `atelier` package only, and both commands run
  clean from a bare checkout (proven locally above).
- **`unittest discover` finds the fable tests** — every
  `atelier/tests/evolve/test_fable_*.py` is picked up (282 tests), and the
  directory has the `__init__.py` discover needs.

## Tests

`atelier/tests/evolve/test_fable_09.py` — was 4 tests; now 7, structural
(block walk, exact job list, exact run lines, per-event trigger paths,
case-insensitive key/env scan, meta-test cross-pin).
`Round17to20Meta.test_ci_workflow_exists` in `atelier/tests/test_evolve.py`
gains five assertions. Everything else untouched.

## Remaining holes (none blocking)

- **CI has never run remotely.** Everything here proves the workflow
  *text* and both commands locally; the first real GitHub Actions run
  happens when this lands where Actions is enabled. The commands are
  verbatim what was run here, from a bare checkout, stdlib only.
- **Single Python version.** Only 3.11 in CI (locally green on 3.12.3
  too). A `{3.11, 3.12}` matrix is cheap but doubles CI minutes and would
  need the pins re-worded; left for a round that wants it.
- **No coverage upload / no timeout-minutes** — out of scope for a
  keyless stdlib gate; a hung test is bounded by GitHub's 6-hour default.
- **Actions pinned by major tag** (`@v4` / `@v5`), not by commit SHA.
  Standard practice for GitHub-owned actions; SHA-pinning is the paranoid
  upgrade if supply-chain hardening becomes a round.
