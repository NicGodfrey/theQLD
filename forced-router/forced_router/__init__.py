"""Force Cursor Auto / Router aliases onto a repo-specified model."""

from .config import ForcedModelConfig, load_config
from .rewrite import rewrite_cli_argv, rewrite_payload
from .policy import allow_prompt, allow_subagent

__all__ = [
    "ForcedModelConfig",
    "load_config",
    "rewrite_payload",
    "rewrite_cli_argv",
    "allow_prompt",
    "allow_subagent",
]
