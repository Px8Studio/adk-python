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

"""
DNB Statistics Agent

Specialized agent for DNB Statistics API operations.
Handles economic datasets, exchange rates, and financial statistics.

Hierarchy:
  root_agent → dnb_coordinator → dnb_statistics_agent (this)
"""

from __future__ import annotations

from typing import Any, Dict, Optional  # standard libs first
import os
import logging

from google.adk import Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset


logger = logging.getLogger(__name__)


class DNBStatsBoundaryToolset(ToolboxToolset):
  """
  Boundary toolset for DNB Statistics tools:
  - Normalizes/validates arguments before delegating to ToolboxToolset.
  - Ensures async client shutdown is scheduled/awaited to avoid warnings.
  """

  # Best-effort close to prevent "coroutine was never awaited" warnings during hot-reload.
  def close(self) -> None:
    """Schedules async client close if available."""
    # ToolboxToolset creates _toolbox_client with an async close() in most versions.
    client = getattr(self, "_toolbox_client", None)
    close_coro = getattr(client, "close", None)
    if callable(close_coro):
      try:
        import asyncio
        loop = asyncio.get_running_loop()
      except RuntimeError:
        # No running loop; run to completion.
        try:
          import asyncio
          asyncio.run(close_coro())
        except Exception:  # keep shutdown resilient on server reload
          logger.exception("Error while closing toolbox client (no loop).")
      else:
        # In event loop: schedule task so it is awaited by the loop.
        try:
          loop.create_task(close_coro())
        except Exception:
          logger.exception("Error scheduling toolbox client close task.")

  async def invoke_tool_async(
      self, tool_name: str, args: Optional[Dict[str, Any]] = None
  ):
    """Validate tool name, normalize args, and delegate."""
    if not tool_name.startswith("dnb-statistics-"):
      raise ValueError(
          f"Refusing to call non-statistics tool '{tool_name}'. "
          "Allowed tools must start with 'dnb-statistics-'."
      )

    args = dict(args or {})

    # Normalize common pagination fields expected by DNB Statistics endpoints.
    # Many toolbox tools expect ints; models sometimes produce strings/floats.
    def _to_int_safe(value: Any) -> Optional[int]:
      if value is None:
        return None
      try:
        # Permit "10", 10.0, 10
        return int(float(value))
      except Exception:
        return None

    # pageSize normalization with fallback removal if invalid.
    if "pageSize" in args:
      ps = _to_int_safe(args.get("pageSize"))
      if ps is not None and ps > 0:
        args["pageSize"] = ps
      else:
        # Drop invalid pageSize to avoid 400s from backend.
        args.pop("pageSize", None)

    # pageNumber normalization
    if "pageNumber" in args:
      pn = _to_int_safe(args.get("pageNumber"))
      if pn is not None and pn >= 0:
        args["pageNumber"] = pn
      else:
        args.pop("pageNumber", None)

    # Add any other known numeric fields here similarly:
    # for key in ("limit", "offset"):
    #   val = _to_int_safe(args.get(key))
    #   if val is not None and val >= 0:
    #     args[key] = val
    #   else:
    #     args.pop(key, None)

    # Log the normalized call for diagnostics when the toolbox returns 400.
    logger.debug("Invoking tool %s with args: %s", tool_name, args)

    try:
      return await super().invoke_tool_async(tool_name, args)
    except Exception:
      # Surface more insight in server logs; original stack is preserved.
      logger.exception(
          "Tool invocation failed for %s with args=%s. Check toolbox server logs for 400 details.",
          tool_name, args
      )
      raise

_TOOLBOX_URL = os.getenv("TOOLBOX_SERVER_URL", "http://localhost:5000")
_TOOLSET_NAME = os.getenv("DNB_STATISTICS_TOOLSET_NAME", "dnb_statistics_tools")
MODEL = os.getenv("DNB_STATISTICS_MODEL", "gemini-2.0-flash")

dnb_statistics_agent = Agent(
  name="dnb_statistics_agent",
  model=MODEL,
  description="Specialist for DNB Statistics API - economic datasets, exchange rates, and financial statistics.",
  instruction="""You are a specialist in DNB Statistics API operations.

CAPABILITIES:
- Economic datasets and indicators
- Exchange rates and currency data
- Financial statistics and balance of payments
- Pension fund data
- Time-series data

TOOLS AVAILABLE:
Use ONLY tools whose names start with 'dnb-statistics-'.

GUIDELINES:
- Summarize datasets clearly with units and time ranges
- Provide context for economic indicators
- Format large datasets for readability
- For echo or public register operations, inform user to route through coordinator""",
  tools=[
    DNBStatsBoundaryToolset(
      server_url=_TOOLBOX_URL,
      toolset_name=_TOOLSET_NAME
    )
  ]
)

# Backwards compatibility aliases
root_agent = dnb_statistics_agent
agent = dnb_statistics_agent