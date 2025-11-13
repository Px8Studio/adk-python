### `backend/adk/agents/orkhon_root/__init__.py`

from __future__ import annotations

from .agent import root_agent

__all__ = ["root_agent"]

# ADK requires this: expose the agent module itself, not the variable here.
from . import agent
