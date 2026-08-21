# Fable-10 · R19 eval fixtures — awaiting live agent

Live leftovers now in the tree:

- `atelier/data/eval/brief_*.json` still load with `request` + `expected`
- `atelier/helix/evalrun.py` runs a fixture through the demo conductor
  and scores `must_mention` + palette hexes in the SVG
- `crafts_required` / `lanes_required` stay documentary (research graph)

Verifier: one blocking `claude-fable-5-thinking-high` agent. Do not start
R20 until this note is replaced with the agent's own evidence.
