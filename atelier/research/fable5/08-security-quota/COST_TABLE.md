# Cost Table — Public List Prices (OpenAI + Gemini)

**Prices retrieved: 2026-08-21.** Standard (non-batch) tier, USD.
Sources: [OpenAI API pricing](https://developers.openai.com/api/docs/pricing) and
[Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing).

These numbers feed `usage.py` (`PRICES`, `PRICES_AS_OF = "2026-08-21"`). They are
**estimates for budgeting** — the provider's invoice is authoritative. Providers
reprice frequently; re-verify this table whenever `PRICES_AS_OF` is older than ~30
days or a new model is added, and update both files together.

## OpenAI — text / multimodal (per 1M tokens, short context)

| Model | Input | Cached input | Output | Notes |
|---|---:|---:|---:|---|
| `gpt-5.6-sol` | $5.00 | $0.50 | $30.00 | flagship |
| `gpt-5.6-terra` | $2.00 | $0.20 | $12.00 | balanced default |
| `gpt-5.6-luna` | $0.20 | $0.02 | $1.20 | high-volume / drafts |
| `gpt-4.1` | $2.00 | $0.50 | $8.00 | legacy, still listed |

Long-context requests on the GPT-5.6 family bill at roughly 2x the short-context
rates (e.g. sol: $10.00 in / $45.00 out). Batch API is ~50% of standard. Regional
data-residency endpoints add a 10% uplift on eligible models.

## OpenAI — image generation (token-billed, per 1M tokens)

| Model | Image input | Cached image in | Text input | Image output |
|---|---:|---:|---:|---:|
| `gpt-image-2` | $8.00 | $2.00 | $5.00 ($1.25 cached) | $30.00 |
| `gpt-image-1.5` | $8.00 | $2.00 | — | $32.00 |
| `gpt-image-1-mini` | $2.50 | $0.25 | — | $8.00 |

## Gemini — text / multimodal (paid tier, per 1M tokens)

| Model | Input | Output (incl. thinking) | Cached input | Notes |
|---|---:|---:|---:|---|
| `gemini-3.1-pro-preview` | $2.00 | $12.00 | $0.20 | prompts ≤ 200k tokens; >200k: $4.00 in / $18.00 out |
| `gemini-3.5-flash` | $1.50 | $9.00 | $0.15 | batch: $0.75 / $4.50 |
| `gemini-3.1-flash-lite` | $0.25 (text/image/video), $0.50 audio | $1.50 | $0.025 | cheapest current text model |

Grounding with Google Search: 5,000 prompts/month free (shared across Gemini 3
models), then $14 per 1,000 search queries.

## Gemini — image generation

Token-billed like OpenAI, but Google publishes per-image equivalents (used as the
`images_*` convenience units in `usage.py`):

| Model | Input (per 1M tok) | Image output (per 1M tok) | Per-image equivalents |
|---|---:|---:|---|
| `gemini-3-pro-image` (Nano Banana Pro) | $2.00 (≈$0.0011/input image) | $120.00 (text out $12.00) | $0.134 per 1K/2K image (1120 tok), $0.24 per 4K (2000 tok) |
| `gemini-3.1-flash-image` (Nano Banana 2) | $0.50 | $60.00 (text out $3.00) | $0.045 / 0.5K, $0.067 / 1K, $0.101 / 2K, $0.151 / 4K |
| `gemini-3.1-flash-lite-image` | $0.25 | $30.00 (text out $1.50) | $0.0336 per 1K image |
| `imagen-4.0-fast / -generate / -ultra` | flat per image | — | $0.02 / $0.04 / $0.06 per image (deprecated, shutdown 2026-08-17 — keep only for historical ledger rows) |

## Rule-of-thumb costs for studio operations (derived)

| Operation | Assumed usage | Est. cost |
|---|---|---:|
| Canvas chat turn (terra) | 5k in + 1k out | $0.022 |
| Canvas chat turn (luna) | 5k in + 1k out | $0.0022 |
| Hero image, 2K (gemini-3-pro-image) | 1 image + 1k in | $0.136 |
| Draft image (gemini-3.1-flash-image, 1K) | 1 image | $0.067 |
| Moodboard describe (3.5-flash, 4 images ≈ 2k tok in, 500 out) | | $0.0075 |

Defaults chosen for `usage.py`'s `BudgetGuard` from these: **$10/day global,
$2/thread** — roughly 70 pro-quality hero images or ~450 terra chat turns per day
before a hard stop.
