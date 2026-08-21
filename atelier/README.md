# Atelier

Local **Helix** design studio: Lovart-class ChatCanvas + design agent, but every model call spends **your** official ChatGPT/OpenAI and Gemini quota.

```bash
python3 -m atelier
# http://127.0.0.1:8765
```

## BYOK

| Provider | Env | Official host |
|---|---|---|
| OpenAI / ChatGPT API | `OPENAI_API_KEY` | `api.openai.com` |
| Google Gemini | `GEMINI_API_KEY` | `generativelanguage.googleapis.com` |
| Ollama | `OLLAMA_HOST` | `127.0.0.1` / `localhost` |

Keys can also be pasted in the Settings rail (stored in `~/.atelier/keyring.json`, mode 0600). ChatGPT Plus website login is **not** used — create an API key at [platform.openai.com](https://platform.openai.com/api-keys) and [aistudio.google.com](https://aistudio.google.com/apikey).

Without keys, **demo mode** still weaves SVG onto the board (zero quota).

## Tests

```bash
python3 -m unittest atelier.tests.test_helix
```

## Layout

- `helix/` — Keyring, Spokes, Conductor, Loom, Memory
- `web/` — Board + conductor dock
- `data/top100.json` — 100 related GitHub projects
- `ARCHITECTURE.md` — original Helix design
- `integrations/` — how patterns are taken, not vendored
