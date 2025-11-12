"""
DNB OpenAPI Agent (ADK OpenAPIToolset)

Purpose:
- Loads DNB OpenAPI specs (echo/statistics/public-register).
- Builds runtime tools via ADK's OpenAPIToolset (no Toolbox YAML required).
- Exposes an Agent wired with these tools for direct use in ADK flows.

This sits alongside the existing Toolbox-based agents so you can choose either
approach per environment/use case.

Env vars:
- DNB_OPENAPI_API: one of {echo, statistics, public-register} (default: echo)
- DNB_SUBSCRIPTION_KEY_DEV or DNB_SUBSCRIPTION_KEY: API key value

Notes:
- Authentication: For API key protected endpoints, pass AuthCredential with
  auth_type=API_KEY. The OpenAPI security scheme in the spec determines where
  the key is attached (header vs query).
"""

from __future__ import annotations

import hashlib
import os
from functools import lru_cache
from pathlib import Path

from google.adk.agents import LlmAgent as Agent
from google.adk.tools.openapi_tool.auth.auth_helpers import (
    token_to_scheme_credential,
)
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import (
    OpenAPIToolset,
)


# Resolve repo root relative to this file
_THIS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parents[4]  # .../orkhon
_SPECS_DIR = _REPO_ROOT / "backend" / "apis" / "dnb" / "specs"


_API_TO_SPEC = {
    "echo": "openapi3-echo-api.yaml",
    "statistics": "openapi3_statisticsdatav2024100101.yaml",
    "public-register": "openapi3_publicdatav1.yaml",
}


def _load_spec_content(api: str) -> str:
    api = api.strip().lower()
    if api not in _API_TO_SPEC:
        raise ValueError(
            f"Unsupported DNB API '{api}'. Choose one of: {list(_API_TO_SPEC.keys())}"
        )
    spec_path = _SPECS_DIR / _API_TO_SPEC[api]
    if not spec_path.exists():
        raise FileNotFoundError(f"OpenAPI spec not found: {spec_path}")
    return spec_path.read_text(encoding="utf-8")


def _get_api_key() -> str | None:
    # Prefer DEV key for local workflows, fallback to generic
    return os.getenv("DNB_SUBSCRIPTION_KEY_DEV") or os.getenv("DNB_SUBSCRIPTION_KEY")


def _safe_agent_name(api: str) -> str:
    """Return a valid ADK agent identifier for the given api slug."""
    return f"dnb_openapi_{api.replace('-', '_')}_agent"


# Toolset builder with LRU caching.
# We expose a single, clear implementation using functools.lru_cache to avoid
# duplicate code paths. When credentials change, the cache key changes and the
# toolset is rebuilt.
@lru_cache(maxsize=10)
def _get_cached_toolset(api: str, _api_key_hash: str) -> OpenAPIToolset:
    """LRU-cached toolset builder. api_key_hash forces cache invalidation on credential change."""
    spec_content = _load_spec_content(api)
    api_key = _get_api_key()

    auth_scheme = None
    auth_credential = None
    if api_key:
        auth_scheme, auth_credential = token_to_scheme_credential(
            token_type="apikey",
            location="header",
            name="Ocp-Apim-Subscription-Key",
            credential_value=api_key,
        )

    return OpenAPIToolset(
        spec_str=spec_content,
        spec_str_type="yaml",
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
    )


def build_openapi_toolset(api: str) -> OpenAPIToolset:
    """Build ADK OpenAPIToolset from the local OpenAPI spec file with caching.

    Parses each spec once per process. Subsequent calls return cached instances
    unless credentials change.
    """
    api_key = _get_api_key() or ""
    api_key_hash = hashlib.md5(api_key.encode()).hexdigest()
    return _get_cached_toolset(api, api_key_hash)


def _default_instruction(api: str) -> str:
    return (
        "You are a DNB API specialist using tools generated from an OpenAPI spec.\n"
        "- Prefer calling tools when you need data.\n"
        "- Clearly summarize responses and include key parameters used.\n"
        "- Authentication is handled automatically.\n"
        f"Target API: {api}."
    )


def _unified_instruction() -> str:
    """Instruction for the unified agent with all three APIs."""
    return (
        "You are a comprehensive DNB (De Nederlandsche Bank) API specialist with "
        "access to all available DNB APIs.\n\n"
        "Available APIs:\n"
        "1. **Echo API** - Test connectivity and authentication\n"
        "2. **Statistics API** - Financial data, market rates, economic indicators, "
        "pension funds, insurance data\n"
        "3. **Public Register API** - Organization searches, publications, "
        "regulatory registers\n\n"
        "Guidelines:\n"
        "- Prefer calling tools when you need data\n"
        "- Clearly summarize responses and include key parameters used\n"
        "- Authentication is handled automatically\n"
        "- Choose the appropriate API based on the user's question\n"
        "- For testing: use Echo API\n"
        "- For financial/economic data: use Statistics API\n"
        "- For organizational/regulatory data: use Public Register API"
    )


try:
    from .._common.config import get_llm_model, get_model  # type: ignore
except Exception:  # pragma: no cover
    def get_llm_model() -> str:
        return "gemini-2.5-flash"
    def get_model(profile: str) -> str:
        return get_llm_model()


def build_agent(api: str | None = None, model: str | None = None) -> Agent:
    """Create an Agent wired with the DNB OpenAPI toolset."""
    api = api or os.getenv("DNB_OPENAPI_API", "echo")
    model = model or os.getenv("DNB_OPENAPI_MODEL") or get_model("fast")

    toolset = build_openapi_toolset(api)
    instruction = _default_instruction(api)

    agent = Agent(
        name=_safe_agent_name(api),
        model=model,
        description=f"DNB OpenAPI tools for '{api}'",
        instruction=instruction,
        tools=[toolset],
    )
    return agent


def build_unified_agent(model: str | None = None) -> Agent:
    """Create an Agent with ALL DNB OpenAPI toolsets combined."""
    model = model or os.getenv("DNB_OPENAPI_MODEL") or get_model("fast")

    # Build all three toolsets
    echo_toolset = build_openapi_toolset("echo")
    statistics_toolset = build_openapi_toolset("statistics")
    public_register_toolset = build_openapi_toolset("public-register")

    agent = Agent(
        name="dnb_openapi_unified_agent",
        model=model,
        description="Unified DNB OpenAPI agent with Echo, Statistics, and Public Register APIs",
        instruction=_unified_instruction(),
        tools=[echo_toolset, statistics_toolset, public_register_toolset],
    )
    return agent


# Default exported agent - unified approach ONLY
dnb_openapi_agent = build_unified_agent()

# Remove the individual variants - they're not needed in the hierarchy
# dnb_openapi_echo_agent = build_agent(api="echo")
# dnb_openapi_statistics_agent = build_agent(api="statistics")
# dnb_openapi_public_register_agent = build_agent(api="public-register")

# Keep this for direct testing
dnb_openapi_unified_agent = dnb_openapi_agent  # Alias


if __name__ == "__main__":  # Simple smoke test: list tool names
    import asyncio
    
    async def show_summary():
        print("=" * 70)
        print("DNB OpenAPI Agent - Tool Summary")
        print("=" * 70)
        
        # Show individual API stats
        for api in ["echo", "statistics", "public-register"]:
            ts = build_openapi_toolset(api)
            tools = await ts.get_tools()
            tool_names = [t.name for t in tools]
            print(f"\n{api.upper()} API: {len(tool_names)} tools")
            for name in sorted(tool_names)[:5]:
                print(f"  - {name}")
            if len(tool_names) > 5:
                print(f"  ... and {len(tool_names) - 5} more")
        
        # Show unified agent stats
        print(f"\n{'=' * 70}")
        unified = build_unified_agent()
        all_tools = []
        for toolset in unified.tools:
            tools = await toolset.get_tools()
            all_tools.extend(tools)
        print(f"UNIFIED AGENT: {len(all_tools)} total tools across all APIs")
        print("=" * 70)
    
    asyncio.run(show_summary())
