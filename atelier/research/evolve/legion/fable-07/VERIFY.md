# Fable-07 · R13 designer export — awaiting live agent

Live leftovers now in the tree:

- `GET /api/projects/:id/export?fmt=zip|svg|png|pdf&scale=1|2|4`
- Zip includes `board.svg` (text stays `<text>`), `sheet.png`, `sheet.pdf`, `RIGHTS.txt`
- `GET /api/artifacts/:id/export?fmt=native|svg|png|pdf`
- JPEG is 415. Export dialog + per-card Export link. Rights line in the UI.

Verifier: one blocking `claude-fable-5-thinking-high` agent. Do not start
R14 until this note is replaced with the agent's own evidence.
