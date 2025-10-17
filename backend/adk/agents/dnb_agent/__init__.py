from __future__ import annotations

# Re-export root_agent for ADK discovery when importing the package directly
from .agent import root_agent  # noqa: F401

__all__ = ["root_agent"]
