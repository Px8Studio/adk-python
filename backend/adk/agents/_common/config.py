"""Central LLM model configuration for Orkhon/ADK agents.

Single, simple model selection via semantic profiles. No per-agent model envs.

Default profile assignments (opinionated):
    fast   → gemini-2.5-flash (cheap, high throughput, routing / retrieval)
    smart  → gemini-2.5-pro   (higher reasoning: planning, code gen, NL2SQL)
    lite   → gemini-1.5-flash (legacy / ultra low cost fallback)
    embed  → text-embedding-005 (vector creation tasks)

Example usage:
    from _common.config import get_model
    router_agent = Agent(model=get_model("fast"), ...)
    analytics_agent = Agent(model=get_model("smart"), ...)

Environment overrides (highest wins):
    ORKHON_MODEL_<PROFILE_UPPER> (e.g. ORKHON_MODEL_SMART)
    ORKHON_LLM_MODEL (global catch‑all)
"""

from __future__ import annotations

import os

DEFAULT_LLM_MODEL = "gemini-2.5-flash"

PROFILE_DEFAULTS = {
    "fast": "gemini-2.5-flash",
    "smart": "gemini-2.5-pro",
    "lite": "gemini-1.5-flash",
    "embed": "text-embedding-005",
}

def get_model(profile: str) -> str:
    """Return a model name for the given semantic profile.

    Args:
        profile: One of fast|smart|lite|embed (case insensitive). Unknown profiles
                         fall back to global cascade.
    Returns:
        Resolved model name after applying layered overrides.
    """
    key = profile.lower().strip()
    if key not in PROFILE_DEFAULTS:
        return os.getenv("ORKHON_LLM_MODEL") or DEFAULT_LLM_MODEL
    # Layered overrides
    return (
            os.getenv(f"ORKHON_MODEL_{key.upper()}")
            or os.getenv("ORKHON_LLM_MODEL")
            or PROFILE_DEFAULTS[key]
    )