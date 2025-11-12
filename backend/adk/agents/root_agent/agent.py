# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Root orchestrator agent for the Orkhon multi-agent system.

This agent coordinates between specialized coordinator agents that handle
different API domains (DNB, etc.). It delegates queries to the appropriate
coordinator based on the user's intent.
"""

from __future__ import annotations

import importlib.util
import importlib.machinery
import logging
import sys
from pathlib import Path
from typing import Any, Optional
import types as _pytypes

from google.adk.agents import Agent

from _common.config import get_model
from api_coordinators.dnb_coordinator.agent import (
  get_dnb_coordinator_agent,
)

def _try_import_data_science_agent() -> Optional[object]:
  """Load the data-science agent as a proper package import.

  Why: The sample lives under "agents/data-science/data_science/agent.py" and
  uses relative imports like "from .prompts import ...". Loading by file path
  breaks those. Instead, temporarily add the outer folder to sys.path and
  import "data_science.agent" so Python resolves relatives correctly.
  """
  try:
    here = Path(__file__).resolve()
    outer_dir = here.parent.parent / "data-science"
    inner_pkg = outer_dir / "data_science"
    agent_file = inner_pkg / "agent.py"

    if not agent_file.exists():
      logging.error("Data-science agent file not found at %s", agent_file)
      return None

    # Ensure dataset config has a sane default if not provided by env/CLI
    # This avoids fatal logs inside the data_science module during import.
    os_env = sys.modules.get('os')
    import os as _os  # local import to avoid polluting module scope
    if not _os.getenv("DATASET_CONFIG_FILE"):
      # Prefer a DNB-oriented config if present, else fall back to flights.
      default_cfg = "dnb_dataset_config.json"
      if not (outer_dir / default_cfg).exists():
        default_cfg = "flights_dataset_config.json"
      _os.environ.setdefault("DATASET_CONFIG_FILE", default_cfg)

    # Add the outer folder so that "import data_science.agent" works
    outer_str = str(outer_dir)
    if outer_str not in sys.path:
      sys.path.insert(0, outer_str)

    import importlib as _il
    module = _il.import_module("data_science.agent")

    getter = getattr(module, "get_root_agent", None)
    if callable(getter):
      return getter()
    agent_obj = getattr(module, "root_agent", None)
    if agent_obj is not None:
      return agent_obj
    logging.warning(
        "Data-science module loaded but missing get_root_agent/root_agent"
    )
  except Exception:
    logging.exception(
        "Data-science root agent unavailable; continuing without it"
    )
  return None

# Build root agent / app the standard way.
# If your existing file already defines an app/root_agent, keep that and only
# replace the loader above. Example pattern below if you need it:

try:
  from google.adk.agents import Agent as LlmAgent  # public API import
  from google.adk.apps import App
except Exception as _e:
  logging.exception("Failed to import ADK core")
  raise

# Example: compose your root agent and app. Adjust to your current design.
# If you already have root_agent/app defined, keep them and only ensure the DS
# module is obtained via _try_import_data_science_agent().
_ds = _try_import_data_science_agent()

def get_root_agent() -> Agent:
  """Create the root agent with sub-agents for API coordination."""
  dnb_coordinator = get_dnb_coordinator_agent()

  # Instantiate data science root agent directly
  data_science_root = _try_import_data_science_agent()

  sub_agents: list[Agent] = [dnb_coordinator]
  if data_science_root is not None:
    sub_agents.append(data_science_root)
  else:
    logging.warning(
        "Data-science root agent unavailable; continuing without it"
    )

  model_name = get_model("fast")

  root = Agent(
      model=model_name,
      name="root_agent",
      instruction="""You are the Root Orchestrator for the Orkhon system.

Your role:
1. Understand the user's intent
2. Delegate to the correct sub-agent:
  - dnb_coordinator_agent: DNB API (Echo, Statistics, Public Register)
  - data_science_root_agent: Analytics / NL2SQL / NL2Py workflows
""",
      sub_agents=sub_agents,
  )
  return root


root_agent = get_root_agent()


# filepath: c:\Users\rjjaf\_Projects\orkhon\backend\adk\adk_patch.py
from typing import Iterable

# Add: guard against closed Toolbox aiohttp sessions (remove once deps updated)
def _patch_toolbox_reopen_closed_session() -> None:
  """Reopen a closed aiohttp session in ToolboxClient right before requests.

  This mirrors the intended lifecycle in newer releases and prevents
  RuntimeError: Session is closed during multi-step runs.
  """
  try:
    import aiohttp  # type: ignore
    from toolbox_core.client import ToolboxClient  # type: ignore

    # Prefer using a dedicated helper if it exists; otherwise access the common names.
    def _ensure_open_session(self) -> None:
      # Known private names in toolbox_core
      cand_names = ("_session", "__session", "_ToolboxClient__session")
      sess = None
      for name in cand_names:
        if hasattr(self, name):
          sess = getattr(self, name)
          break
      if sess is None or getattr(sess, "closed", True):
        new_sess = aiohttp.ClientSession()
        # set back on the first found name or default to _session
        if sess is None:
          setattr(self, "_session", new_sess)
        else:
          setattr(self, name, new_sess)

    # Wrap selected HTTP-entry methods to ensure an open session.
    for method_name in ("load_toolset", "list_tools", "get_tool", "call_tool"):
      if hasattr(ToolboxClient, method_name):
        _orig = getattr(ToolboxClient, method_name)
        if getattr(_orig, "__patched_reopen__", False):
          continue

        async def _wrap(self, *args, __orig=_orig, **kwargs):  # type: ignore[no-redef]
          _ensure_open_session(self)
          return await __orig(self, *args, **kwargs)

        setattr(_wrap, "__patched_reopen__", True)
        setattr(ToolboxClient, method_name, _wrap)

  except Exception:
    # Best-effort patch; safe to ignore if toolbox_core not installed/used.
    pass

def apply_runtime_patches() -> None:
  """Apply all runtime patches safely (idempotent)."""
  # existing patches
  # ...existing code...
  _patch_toolbox_reopen_closed_session()
  # ...existing code...