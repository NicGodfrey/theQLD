# Fable-09 · R17 CI (conductor fill — agent slot full)

**Pass.** `.github/workflows/atelier.yml` runs `python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve` on Python 3.11.

## Remaining
- Path filters skip the workflow when only non-atelier files change (intentional).
- No live-key smoke job (correct: no secrets in CI).
