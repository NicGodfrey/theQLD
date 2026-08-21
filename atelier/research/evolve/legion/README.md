# 20-round verification legion

Parent implemented live R1–R20 on `cursor/atelier-byok-studio-d639`.

Each agent writes **only** under its own folder:

- `fable-01` … `fable-10`
- `opus-01` … `opus-10`

Allowed extra tests: `atelier/tests/evolve/test_<id>.py` (unique filename).
Do **not** edit `atelier/helix/*.py`, `atelier/server.py`, or `atelier/web/*`.
Do **not** git commit or push.

Release gate (must stay green):

```bash
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve
```
