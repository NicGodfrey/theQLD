# Fable-01 — ROUND 1 (fail-closed) verification

Scope: `atelier/helix/conductor.py` paid `SpokeError` path, `Round01FailClosed`
in `atelier/tests/test_evolve.py`, `atelier/research/evolve/ROUNDS.md` row 1.
Read-only over the live tree; unique test added at
`atelier/tests/evolve/test_fable_01.py`.

## Verdict: PASS (with residual holes below)

## What was confirmed

1. **Paid image failure never mints demo SVG.** In `Conductor.run`, when the
   image weave raises `SpokeError` and `route_provider != "demo"`, the loop
   `continue`s (conductor.py ~line 252–257) instead of falling into the demo
   spoke retry. If nothing was produced, `ConductorError(code="spoke_error")`
   is raised (~line 301). Zero rows land in `artifacts`, so no paid-looking
   demo output exists. Verified for **openai** by the shared
   `Round01FailClosed` test and for **gemini** by
   `test_gemini_image_failure_never_mints_demo` in the unique test.
2. **Planner cannot downgrade `route.provider` to demo.** For any
   user-selected `provider != "demo"`, the plan's route is unconditionally
   overwritten with the user's provider (~line 182–184) *after* the planner
   JSON is merged, so a planner response carrying `"route": {"provider":
   "demo"}` is repinned. Verified by
   `test_planner_cannot_downgrade_route_to_demo`, which also asserts
   `build_spoke` is never called with `"demo"` during the weave.
3. **Demo provider still works.** `provider="demo"` runs end-to-end, mints an
   SVG artifact stamped `provider="demo"`, and the demo-lane `SpokeError`
   retry (~line 258) remains available. Verified by
   `test_demo_lane_still_mints_svg`.

## Gate

```
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve
Ran 28 tests ... OK
python3 -m unittest atelier.tests.evolve.test_fable_01
Ran 3 tests ... OK
```

## Remaining holes

1. **Unknown provider strings fail OPEN via the spoke factory.**
   `build_spoke` (spokes/__init__.py) falls through to `DemoSpoke()` for any
   unrecognized name, and `server.py` passes `body.get("provider")` through
   unvalidated. A client sending `" openai"` (whitespace), `"OpenAI "` or
   `"open-ai"` misses every branch after `.lower()` (no `.strip()`, no
   allowlist), so the whole run — planner *and* image — executes on the demo
   spoke and happily mints SVG while the caller believes a paid lane was
   selected. This bypasses ROUND 1's intent without ever raising
   `SpokeError`. The route pin doesn't help: the pinned value is the same
   malformed string.
2. **The route pin is one-directional.** When `provider == "demo"` the code
   uses `plan["route"].setdefault("provider", provider)`, so a planner-supplied
   `route.provider` of `"openai"` would be *trusted* and drive the image
   weave onto a paid lane (upgrade, the mirror of the downgrade). Unreachable
   today because `DemoSpoke.chat` always returns `"demo"`, but nothing
   structural prevents it if the demo planner ever changes.
3. **Mixed weave demotes paid failure to a warning.** If the planner emits a
   `note`/`text` item alongside images and every paid image call fails, the
   guard at ~line 301 does not fire (a non-image node exists), so the run
   returns `ok=True` / HTTP 200 with the failure only as a "Warnings:" line
   in the summary. No demo SVG is minted, so fail-closed holds for minting,
   but the failure signal is soft.
4. Cosmetic: `_image_model` returns `"demo-svg"` for `ollama` and any unknown
   provider, mislabeling the model on non-demo lanes (moot today because the
   ollama spoke's `image()` raises).

## Suggested diff (NOT applied — hard rules forbid editing these files)

```diff
--- a/atelier/helix/spokes/__init__.py
+++ b/atelier/helix/spokes/__init__.py
@@
 def build_spoke(provider: str, keyring) -> Spoke:
-    provider = (provider or "demo").lower()
+    provider = (provider or "demo").strip().lower()
     if provider == "openai":
         return OpenAISpoke(keyring)
     if provider == "gemini":
         return GeminiSpoke(keyring)
     if provider == "ollama":
         return OllamaSpoke(keyring)
     if provider in {"openai_compat", "compat"}:
         return OpenAISpoke(keyring, provider_name="openai_compat")
-    from .base import DemoSpoke
+    if provider != "demo":
+        # Fail closed: an unknown lane must never silently become demo.
+        raise SpokeError(f"Unknown provider '{provider}'")
+    from .base import DemoSpoke
 
     return DemoSpoke()
--- a/atelier/helix/conductor.py
+++ b/atelier/helix/conductor.py
@@ def run(self, ...):
-        provider = (provider or "demo").lower()
+        provider = (provider or "demo").strip().lower()
@@
-        if provider != "demo":
-            # User-selected paid lane stays pinned — planner cannot downgrade to demo.
-            plan["route"]["provider"] = provider
-        else:
-            plan["route"].setdefault("provider", provider)
+        # Pin both directions: planner may not downgrade a paid lane to demo,
+        # nor upgrade the demo lane onto a paid spoke.
+        plan["route"]["provider"] = provider
```

With the factory change, `Round01FailClosed` still passes (its mock replaces
`build_spoke`), the demo lane is untouched, and typo'd providers surface as
`SpokeError` instead of minting demo SVG.
