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
DNB Public Register Agent

Specialized agent for DNB Public Register API operations.
Handles license searches, registration data, and regulatory information.

Hierarchy:
  root_agent → dnb_coordinator → dnb_public_register_agent (this)
"""

from __future__ import annotations

import os
import logging
from typing import Any, Dict, Optional

from google.adk.agents import LlmAgent as Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.base_tool import BaseTool
from google.adk.agents.readonly_context import ReadonlyContext
from typing_extensions import override


class DNBBoundaryToolset(ToolboxToolset):
    """Wraps ToolboxToolset to normalize known Public Register quirks.

    - publications_search requires 'RegisterCode' (capital R). If the model
      emits 'registerCode', remap it.
    - Clamp pagination and validate simple date shapes when present.
    """

    class _PublicationsSearchAdapter:
        """Adapter that preserves the original signature/docs while normalizing args."""

        def __init__(self, underlying_callable):
            self._underlying = underlying_callable
            # Mirror metadata for FunctionTool/LLM declaration
            self.__name__ = getattr(underlying_callable, "__name__", "publications_search")
            self.__doc__ = getattr(underlying_callable, "__doc__", "")
            self.__signature__ = getattr(underlying_callable, "__signature__", None)
            self.__annotations__ = getattr(underlying_callable, "__annotations__", {})

        async def __call__(self, **kwargs):
            args: Dict[str, Any] = dict(kwargs)

            def _first_present(keys: list[str]) -> Optional[str]:
                for k in keys:
                    if k in args:
                        return k
                return None

            # Normalize RegisterCode casing/aliasing
            rc_key = _first_present([
                "RegisterCode", "registerCode", "registercode", "Registercode", "register_code",
            ])
            if rc_key and rc_key != "RegisterCode":
                args["RegisterCode"] = args.pop(rc_key)

            # Normalize languageCode; default to NL
            lang_key = _first_present([
                "languageCode", "LanguageCode", "language", "lang", "language_code",
            ])
            if lang_key and lang_key != "languageCode":
                args["languageCode"] = args.pop(lang_key)
            if "languageCode" not in args:
                args["languageCode"] = "NL"

            # Simple page/pageSize guardrails
            if "pageSize" in args:
                try:
                    ps = int(args["pageSize"])  # type: ignore[arg-type]
                    if ps < 0:
                        ps = 0
                    args["pageSize"] = ps
                except (TypeError, ValueError):
                    args.pop("pageSize", None)
            if "page" in args:
                try:
                    p = int(args["page"])  # type: ignore[arg-type]
                    if p < 1:
                        p = 1
                    args["page"] = p
                except (TypeError, ValueError):
                    args.pop("page", None)

            try:
                return await self._underlying(**args)
            except Exception as exc:
                safe_args = {k: ("***" if k.lower().endswith("key") else v) for k, v in args.items()}
                error_msg = str(exc)
                
                # Check for invalid register code error
                if "register code" in error_msg.lower() and "not valid" in error_msg.lower():
                    register_code = args.get("RegisterCode", "UNKNOWN")
                    enhanced_msg = (
                        f"Invalid register code '{register_code}'. "
                        f"Use dnb_public_register_api_publicregister_registers tool to get valid register codes. "
                        f"Original error: {error_msg}"
                    )
                    logging.warning("Invalid register code detected. args=%s error=%s", safe_args, exc)
                    raise ValueError(enhanced_msg) from exc
                
                logging.warning("Publications search failed. args=%s error=%s", safe_args, exc)
                raise

    @override
    async def get_tools(self, readonly_context: Optional[ReadonlyContext] = None) -> list[BaseTool]:
        # Load tools from toolbox
        tools = await super().get_tools(readonly_context)
        wrapped: list[BaseTool] = []
        for t in tools:
            # Only wrap FunctionTool instances; preserve all others
            if isinstance(t, FunctionTool) and t.name.endswith("publications_search"):
                adapter = DNBBoundaryToolset._PublicationsSearchAdapter(t.func)
                wrapped.append(FunctionTool(adapter))
            else:
                wrapped.append(t)
        return wrapped

_TOOLBOX_URL = os.getenv("TOOLBOX_SERVER_URL", "http://localhost:5000")
_TOOLSET_NAME = os.getenv("DNB_PUBLIC_REGISTER_TOOLSET_NAME", "dnb_public_register_tools")
MODEL = os.getenv("DNB_PUBLIC_REGISTER_MODEL", "gemini-2.0-flash")

dnb_public_register_agent = Agent(
    name="dnb_public_register_agent",
    model=MODEL,
    description="Specialist for DNB Public Register API - license searches, registration data, and regulatory information.",
    instruction="""You are a specialist in DNB Public Register API operations.

CAPABILITIES:
- License and registration searches
- Entity details and regulatory information
- Publications and announcements
- Institutional data

TOOLS AVAILABLE:
Use ONLY tools whose names start with 'dnb-public-register-'.

CRITICAL - DISCOVERING VALID REGISTER CODES:
Before searching publications or entities, you MUST first discover valid register codes:
1. Call dnb_public_register_api_publicregister_registers to get the list of available registers
2. This returns register codes like 'WFTAF', 'WFT', etc. with their names and types
3. Use the EXACT register code from this list in subsequent API calls
4. Common mistake: Do NOT assume 'AFM' is a valid register code - always check first!

IMPORTANT - PARAMETER CASING:
Parameter names are case-sensitive and follow the API definition exactly:
- publications_search requires 'RegisterCode' (capital R), not 'registerCode'
- Many endpoints use path parameter 'registerCode' (lowercase r) in the URL path
- Dates should follow format 'YYYY-MM-dd' (e.g., '2024-01-30')
- languageCode defaults to 'NL'

GUIDELINES:
- ALWAYS fetch available registers first if you don't know the valid register codes
- Validate register codes, relation numbers, dates before calling tools
- Restate exact parameter names if casing mismatch is suspected
- Format search results clearly with register names and codes
- For echo or statistics operations, inform user to route through coordinator

EXAMPLE WORKFLOW:
User: "Find financial institutions in the AFM register"
Step 1: Call dnb_public_register_api_publicregister_registers to discover valid codes
Step 2: Use the correct register code (e.g., 'WFTAF' for financial services) in search
Step 3: Return results with clear explanation of which register was searched""",
    tools=[
        DNBBoundaryToolset(
            server_url=_TOOLBOX_URL,
            toolset_name=_TOOLSET_NAME,
        )
    ],
)