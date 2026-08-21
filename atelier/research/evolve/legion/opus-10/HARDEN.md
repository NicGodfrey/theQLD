# Opus-10 · R20 acceptance scorecard — verified

Verifier: one live `claude-opus-5-thinking-high-fast` agent, branch
`cursor/atelier-byok-studio-d639`, HEAD at `1e1a265` (Round 20).
Method: every line of `SCORECARD.json` that makes a claim about behaviour was
re-derived from live modules rather than read — the demo conductor on a
throwaway `Memory`/`Keyring`/artifacts dir, real `ThreadingHTTPServer` binds on
ephemeral ports for the HTTP claims, `OPENAI_API_KEY` / `GEMINI_API_KEY`
absent from this pod entirely. No network, no key read, no paid call. The two
notes that carry numbers (`priced`, remote CI) were measured, and the remote CI
one was checked against GitHub Actions itself.

**Verdict: PASS with fixes.** The card is honest in its headline and was too
rosy in its detail. All five claims hold: the arithmetic is right, every round
carries a live agent note, `lovart_complete` and `paid_loop_proven` are false,
`demo_loop` and `honest` are true, R20's note says what this file is, and
`Round17to20Meta.test_scorecard_gate` still passes untouched. What did not hold
was the leftovers list. Two round notes were wrong or stale — R2 repeated the
`priced` sentence R18 had already disproved, and R17 said remote Actions was
unproven when it had in fact run and gone **red** — and four live product holes
were missing from a list whose whole job is naming them. The red CI was one
root cause: `loom.text_meta` calls a 3.12-only builtin, so the studio crashes on
the Python the workflow pins. That is fixed in this round, and CI is green.

## Claim by claim

| # | Claim | Verdict |
|---|-------|---------|
| 1 | `rounds_total` 20, `len(rounds)` 20, `n` 1..20, `passed >= gate >= 16` | PASS — and `passed` is now *derived* from the rounds rather than typed next to them |
| 2 | Every round `pass: true` for the technical slice a live verifier closed; R1–R19 have notes under `legion/` | PASS — 20 folders, one note each, every one over 400 bytes; owner alternates fable/opus with `n` |
| 3 | `lovart_complete` false, `paid_loop_proven` false, `demo_loop` true, `honest` true, holes name the six | PASS on the booleans, **FAIL on the list** — the six were named, four more live holes were not |
| 4 | Round 20's note says this file is the scorecard and the product is not Lovart-complete | PASS, verbatim, and now pinned |
| 5 | `Round17to20Meta.test_scorecard_gate` still passes | PASS — untouched, and re-run from inside this suite so it cannot rot silently |

## What the tree actually does

Each hole on the card is now reproduced, not asserted. Measured on the demo
lane at this HEAD:

```
raster      board.svg inlines the artwork (<circle> present, vector intact)
            sheet.png does not (<circle> absent), and is 640 px wide whatever
            the board holds — a fixed canvas with node boxes painted onto it
            artifact fmt=png on an SVG -> a 5×7-glyph caption card, not the art
            (an artifact that is already a PNG passes through untouched)

StyleLock   style_lock("a poster", ["#0B3954","#E0A458"], "QLD")
            -> "[StyleLock brand=QLD palette=#0B3954,#E0A458 ground=#0B3954
                ink=#E0A458]\na poster"
            the string "delta_e" / "deltae" does not occur in any product
            module — only in research/. Nothing measures the returned pixels.

stream      app.js: "/run?stream=0", no "stream=1", no EventSource anywhere
            server.py: text/event-stream is live and has no client

undo        run -> 1 node, 1 artifact row, 1 file
            undo -> 0 nodes, artifact row still there, file still on disk
            "redo" does not occur in any product module

caret       app.js edits text through prompt(TEXT_SPEC_LABEL, …);
            no contentEditable, no caret

reference   upload artifact prompt = "client-logo.png" (the filename)
            spot edit on it weaves:
              "Spot-edit of previous artifact (febcbd34…). Direction: restyle
               this in navy. Original brief: client-logo.png. Variant prompt: …"
            openai_spoke posts /v1/images/generations and has no /v1/images/edits
            -> the uploaded bytes never leave the machine

4-up        variants=4 -> 4 artifacts, every parent_id NULL, every node meta {}
            server.py has no /pick, /promote or /winner route
            culling means four undos in reverse

brand kit   update_brand_kit({"name","palette","fonts"}) stores
            {"name","palette","voice"} — fonts is dropped on the way in

download    "静かなポスター" -> deadbeefcafe.svg   (id, not brief)
            "Кириллица"      -> deadbeefcafe.svg
            "a quiet poster" -> a-quiet-poster.svg

keyring     put("openai",        base_url="https://evil.example")  -> ValueError
            put("openai_compat", base_url="http://evil.example/v1") -> stored,
            and public_status() reports it configured
```

Fail-closed and the budget, re-produced rather than inherited from R01/R16:

```
provider=openai, no key       -> 422 {"code":"auth"}  0 artifacts, 0 board nodes
ATELIER daily budget 0.0      -> 402 {"code":"budget_exceeded"}
                                 messages before 0, after 0  (nothing persisted)
provider=openai, no key       -> 422, messages 0 -> 1  (the auth path *does*
                                 persist the user prompt; the 402 path does not)
provider=demo                 -> 200, 1 artifact, provider=demo
/api/usage rows: 0 before, 0 after — a blocked run spends nothing
```

## The eval scorer, and what a "pass" is worth

R19's note said some mentions are brief echoes. They all are, and so is the
palette check. The demo loom writes `html.escape(prompt[:180])` into the SVG as
a caption, and the scorer greps the SVG bytes for the expected hexes — so a
fixture whose brief quotes its own palette inside the first 180 characters
scores a palette hit with no kit and no ink.

```
brief_brand_kit_apply.json     ok=True   Archivo/Inter hit, #1A5FB4/#F5C211 hit
  same fixture, brand kit deleted   ok=True   palette still hit  <- caption echo
  same fixture, kit kept, the words "Archivo"/"Inter" removed from the brief
                                    ok=False  <- the kit alone carries nothing
brief_factsheet_legal_directory.json  ok=False
  request is 459 chars; #0B3954 sits at 304 and #E0A458 at 328, both past the
  180-char caption cut, and the fixture has no "brand" key at all
  bolt a kit onto it -> ok=True, both hexes hit
brief_logo.json   ok=True      brief_poster.json  ok=True
```

The two scrub runs are the honest reading: `must_mention` measures whether the
brief was echoed, and `palette` measures the same thing unless a kit happens to
be set. Both are on the card now.

## Remote CI: the card said unproven, it was red

`gh run list` on this branch shows Actions has been running all along. At
`1e1a265` — the commit the card describes — the `legion` job **failed**:

```
gate    ✓  36 tests OK
legion  ✗  Ran 332 tests — FAILED (failures=1, errors=6, expected failures=1)
```

All six errors are one line of product code:

```
File "atelier/helix/loom.py", line 119, in text_meta
    out["font_size"] = int(size) if size.is_integer() else size
AttributeError: 'int' object has no attribute 'is_integer'
```

`_number()` returns a float, but `min(96, max(12, 99999.0))` returns the *int*
bound `96`, and `int.is_integer()` only exists on 3.12+. The local gate runs
3.12.3, where it is fine; the workflow pins `python-version: "3.11"`, where any
`font_size` outside 12–96 crashes `add_node` — the R12 text layer, through the
UI, the HTTP route or the conductor. A real defect in shipped code that no
local run could see.

Fixed at the call site (`float(size).is_integer()`), behaviour on 3.12
unchanged for every input:

```
99999 -> 96    5 -> 12    42 -> 42    42.5 -> 42.5    True/'x'/nan -> dropped
```

Pinned in `test_opus_06.TextMetaNormaliser.test_the_clamp_never_calls_a_312_only_builtin`,
which asserts the clamp really does hand back an int *and* that the receiver in
the source is wrapped — so the 3.12 gate now fails on the 3.11 bug. Revert the
cast and that test fails.

Remote CI after the fix, run `32529021017` on `f6e8112`:

```
gate    ✓  Ran 36 tests   — OK
legion  ✓  Ran 333 tests  — OK (expected failures=1)
```

The seventh failure at `1e1a265` (`TypeError: fetch failed` in the node DOM
harness) did not recur and passes locally; it is recorded below as flake rather
than fixed.

## Corrections made to the card

1. **R2 repeated a sentence R18 disproved.** The note read "Unknown models
   priced:false". `priced` is `chat_priced and image_priced`, short-circuited
   true for the free lanes. Measured here:

   ```
   openai / gpt-4o-mini         priced=True   $0.0403
   openai / no-such-model-9000  priced=False  $0.0500
   gemini / made-up-9000        priced=False  $0.0500
   ollama / no-such-model-9000  priced=True   $0.0000   <- unknown, priced
   demo   / no-such-model-9000  priced=True   $0.0000   <- unknown, priced
   ```

   R18 fixed this in `CONTRACT.md` and the scorecard kept the old sentence.
   Rewritten to the real rule; the surviving half of the note ("402 does not
   persist the prompt") was re-measured and holds.
2. **R17 was stale in the worse direction.** "Remote Actions unproven from this
   pod" was true when fable-09 wrote it and false by the time the card shipped:
   Actions had run and was red. Now records the green run, its Python, and that
   it was red until this round.
3. **`passed` is now derived.** It was a hand-typed `20` beside a list of
   twenty; the tightened suite recomputes it, so a future round cannot flip a
   `pass` to false and leave the headline at 20.
4. **`remote_ci` added** — run URL, pinned Python, both job results, and the
   reason it was red. A claim about CI that names the run is checkable; "proven
   on workflow text" is not.
5. **R5, R8, R10, R12, R19 notes** now carry the leftovers their own legion
   notes recorded and the card had dropped.

## Holes added to the card

All four are live at this HEAD and none was on the list.

1. **The reference upload never reaches a model.** `POST /:id/upload` stores
   bytes and an artifact whose `prompt` is the filename; a spot edit turns that
   into the sentence quoted above and posts it to a text-to-image endpoint. The
   UI says "next weave uses it as reference", and what it actually sends is the
   filename. For a studio whose whole pitch is "restyle *this*", this is the
   largest single gap between the copy and the wire.
2. **A 4-up cannot be resolved.** Four artifacts with no shared identity, no
   promote route, no cull except undoing in reverse. opus-04 called it "the
   biggest gap" in R8 and the card gave R8 no note at all. (R11 has since added
   click-to-select, so the selection half of opus-04's H1 is closed — the
   identity and promote halves are not.)
3. **The eval palette check can pass on the caption echo**, as measured above.
4. **Brand kits drop `fonts`**, so the one fixture that tests typography is
   scoring the brief, not the kit.

Two further per-round leftovers were promoted onto the list because they are
product behaviour a reader of the card would want up front: non-Latin briefs
slugging to the hex id (R4), and `openai_compat` accepting any base URL (R15).

### Checked and *not* a hole

- **The gates hold.** Fail-closed, quote-before-commit, no-silent-demo and
  stdlib-only were each re-produced (above). The only non-stdlib import under
  `atelier/` outside `research/` is `setuptools` in `test_opus_07`, guarded by
  `skipTest`; no product module imports anything off-stdlib.
- **Nothing on the card is invented.** Every one of the original eight holes
  reproduces. Not one had been quietly fixed and left on the list.
- **The headline is right.** 20 technical slices, each closed by a live
  verifier, is what happened; `lovart_complete: false` is the honest reading of
  the leftovers, and this round did not touch it.
- **R14's launcher note holds.** From `/tmp`, `python3 -m atelier` is
  `No module named atelier`; with `PYTHONPATH=/workspace` it boots. No console
  script is installed in this pod.
- **R7's note holds.** `renderPlan` does `classList.toggle("done")` on click and
  no step state is persisted anywhere.

## Evidence that the tests bite

`atelier/tests/evolve/test_opus_10.py` — was 3 tests in one class, all of them
reading the card and comparing it to itself; now **25 across five classes**,
where the holes list is checked against live behaviour in both directions. If a
hole is quietly closed, the test for that behaviour fails; if the card drops a
line while the behaviour is still live, the `assertHole` in the same test fails.

Sixteen sabotaged cards and three sabotaged product files, each run through
both the shipped suite and the tightened one:

```
                                        shipped        tightened
passed 21 with 20 rounds                OK             1 test failed
R2's disproved priced sentence          OK             1 test failed
R17's stale CI note                     OK             1 test failed
R20 stops saying not-Lovart-complete    OK             1 test failed
round 8 changes owner                   OK             1 test failed
holes reduced to one vague line         1 failed       14 failed
style_lock stops prefixing              OK             1 test failed
```

and, against the tightened suite only:

```
BITES  claim Lovart-complete                    2 tests failed
BITES  claim the paid loop was proven           3 tests failed
BITES  flip honest to false                     2 tests failed
BITES  fail round 8                             3 tests failed
BITES  drop round 20                            5 tests failed
BITES  drop the contact-sheet hole              2 tests failed
BITES  drop the pick-winner hole                1 test failed
BITES  drop the reference-upload hole           1 test failed
BITES  drop the no-redo hole                    2 tests failed
BITES  empty the holes list                    15 tests failed
BITES  flip the fail-closed gate                2 tests failed
BITES  app.js grows an EventSource              1 test failed
BITES  loom drops the 3.11 float cast           1 test failed
```

The shipped file missed six of the seven mutations it was shown.

## Tests

```
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve \
    atelier.tests.evolve.test_opus_10
Ran 61 tests — OK                                   (39 before, also OK)

python3 -m unittest discover -s atelier/tests/evolve
Ran 355 tests — OK (expected failures=1)

python3 -m unittest discover -t . -s atelier/tests -p "test_*.py"
Ran 391 tests — OK (expected failures=1)
```

Local Python 3.12.3; CI 3.11, green on both jobs at `f6e8112`. The whole R20
suite runs in 0.44 s — the conductor calls are demo-lane and offline.

## Folded after this note (conductor close)

Fleet closed. No 21st round. Remaining items are product holes on the
scorecard, not unverified slices.

## Remaining holes

- **The card is a claim about a tree, and this suite only checks the claims the
  card makes.** A hole nobody wrote down is invisible to it. The four added here
  were found by reading ten legion notes' "remaining holes" sections against the
  code, which is not something a test can do.
- **`assertHole` matches substrings.** It proves the card *mentions* the
  behaviour, not that the sentence is a good description of it. Rewording a hole
  into something vaguer but still containing "redo" would pass.
- **`test_the_paid_loop_cannot_be_claimed_from_this_environment` is only half a
  pin.** It asserts `paid_loop_proven` is false and reports which keys are
  present, but a card that claimed a paid run *and* had keys in the environment
  would still need a human to check the run happened. There is no way to prove a
  negative about a network this suite never touches.
- **The `.is_integer()` guard is a source scan.** It catches the one 3.12-only
  builtin that bit us; it is not a 3.11 interpreter. The only real cover for
  version drift is the `legion` job, and it is a single-version job.
- **The node DOM harness flaked once on the runner** (`TypeError: fetch failed`
  against its own loopback server) and has not since. Passes locally every time.
  Unexplained, so it is not fixed — if it recurs it needs a retry or a bind on
  an explicit `127.0.0.1` rather than `localhost`.
- **`honest: true` is self-assessment.** Nothing can test it. What the tests can
  do — and now do — is make every specific claim under it falsifiable, so the
  flag is at least expensive to keep while lying.

## Not started

No 21st round. `FLEET.md` still shows opus-10 as the round's verifier slot for
the conductor to close. No research Board UI swapped onto the live process, no
paid provider contacted, and nothing in `remaining_product_holes` was fixed —
except the 3.11 crash, which was not a product hole but a broken build.
