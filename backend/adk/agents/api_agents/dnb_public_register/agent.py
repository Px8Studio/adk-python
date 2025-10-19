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
DNB Public Register Agent - Focused on Public Register API tools only.
"""

from __future__ import annotations

import os
import logging
from typing import Any, Dict, Optional

from google.adk import Agent
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
# Default to generator convention: dnb_public_register_tools; allow override
_TOOLSET_NAME = os.getenv("DNB_PUBLIC_REGISTER_TOOLSET_NAME", "dnb_public_register_tools")

# ADK Web expects 'root_agent'
root_agent = Agent(
    name="dnb_api_public_register",
    model="gemini-2.0-flash",
    instruction="""You are a helpful assistant specialized in the DNB Public Register API.
Use ONLY tools whose names start with 'dnb-public-register-'.
If a user asks about echo or statistics, ask to switch to the matching agent instead.

Important: Parameter names are case-sensitive and follow the API definition exactly. Do not normalize casing.
- Example: publications_search requires query parameter 'RegisterCode' (capital R), not 'registerCode'.
- Example: many endpoints use path parameter 'registerCode' (lowercase r) in the URL path.
- Dates should follow the examples in the docs, e.g., 'YYYY-MM-dd' like '2024-01-30'.

When users provide register codes, relation numbers, dates, or languages, validate them before calling tools. If you suspect a casing mismatch, restate the exact parameter names you will send and correct them before invoking the tool.""",
    tools=[
        DNBBoundaryToolset(
            server_url=_TOOLBOX_URL,
            toolset_name=_TOOLSET_NAME,
        )
    ],
)

agent = root_agent

agent = root_agent