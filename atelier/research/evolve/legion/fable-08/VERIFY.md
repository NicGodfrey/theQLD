# Fable-08 · R15 host-pin (conductor fill — agent slot full)

**Pass.** `keyring.put` rejects unofficial OpenAI/Gemini/Ollama hosts (`chatgpt.com`, `evil.example`). Credentialed spoke POSTs use `urlopen_no_redirect`; 3xx → `SpokeError`.

## Remaining
- `openai_compat` is intentionally free-form (user-set host).
- OpenAI image CDN download is not host-pinned (no API key on that request).
