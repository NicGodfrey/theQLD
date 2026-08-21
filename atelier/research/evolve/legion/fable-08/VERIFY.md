# Fable-08 · R15 host-pin — awaiting live agent

Live leftovers now in the tree:

- `keyring.put` rejects unofficial OpenAI/Gemini hosts and `http://` on those
- Spokes `assert_official_host(..., require_https=True)` for paid APIs
- Credentialed POSTs use `urlopen_no_redirect`; 3xx → `SpokeError`
- OpenAI image URL fetch is pinned to known CDNs and refuses loopback / RFC1918
- `openai_compat` stays free-form (user-set host)

Verifier: one blocking `claude-fable-5-thinking-high` agent. Do not start
R17 until this note is replaced with the agent's own evidence.
