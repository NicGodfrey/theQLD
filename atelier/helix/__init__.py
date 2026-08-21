"""Helix — original Atelier architecture.

Keyring  → local BYOK vault (official provider hosts only)
Spokes   → OpenAI / Gemini / Ollama / OpenAI-compatible adapters
Conductor→ design agent (fast | thinking)
Board    → infinite canvas nodes
Loom     → media weave (image / video stub / demo SVG)
Memory   → SQLite projects, threads, artifacts, usage
"""

__all__ = [
    "store",
    "keyring",
    "usage",
    "conductor",
    "loom",
    "catalog",
]
