"""
CLI smoke test for the DNB OpenAPI Agent (ADK-native OpenAPIToolset).

Usage (env-driven):
  - Set DNB_OPENAPI_API to one of: echo | statistics | public-register
  - Optionally set DNB_SUBSCRIPTION_KEY_DEV or DNB_SUBSCRIPTION_KEY
  - Then run this script to list tools and execute a simple prompt.

Example:
  $env:DNB_OPENAPI_API = "echo"; python backend/adk/run_dnb_openapi_agent.py
"""

from __future__ import annotations

import asyncio
import os
from typing import Optional

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Import the agent builder from our OpenAPI-based agent
from agents.api_agents.dnb_openapi.agent import build_agent, build_openapi_toolset  # type: ignore


def _sample_query_for(api: str) -> str:
    api = api.strip().lower()
    if api == "echo":
        return "Please call the echo hello world endpoint and summarize the result."
    if api == "statistics":
        return (
            "List available statistics metadata and show a couple of dataset names."
        )
    if api == "public-register":
        return (
            "Discover available registers, then search publications with a small page size."
        )
    return "What can you do? List your available tools."


async def main(app_name: str = "dnb_openapi_agent") -> None:
    api = os.getenv("DNB_OPENAPI_API", "echo")

    # Build toolset and print tool names as a smoke test
    toolset = build_openapi_toolset(api)
    # get_tools is async; list a few names for a quick smoke test
    tools = await toolset.get_tools()
    tool_names = [t.name for t in tools]
    print(f"[info] Loaded {len(tool_names)} tools for '{api}':")
    for name in sorted(tool_names)[:25]:
        print(f"  - {name}")
    if len(tool_names) > 25:
        print("  ...")

    # Build agent and run a short prompt to trigger at least one tool call
    agent = build_agent(api=api)

    session_service = InMemorySessionService()
    user_id = "demo-user"
    session_id = f"dnb-openapi-{api}"
    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

    runner = Runner(agent=agent, app_name=app_name, session_service=session_service)

    prompt = _sample_query_for(api)
    print(f"\n[info] Running prompt for '{api}': {prompt}")

    content = types.Content(role="user", parts=[types.Part(text=prompt)])
    final: Optional[str] = None

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            final = event.content.parts[0].text if event.content and event.content.parts else None
        # Also print tool call events for quick visibility
        if event.type == "function_call":
            print(f"[tool-call] {event.content.parts[0].function_call.name}")
        if event.type == "function_response":
            print(f"[tool-response] {event.content.parts[0].function_response.name}")

    print("\n[final]")
    print(final or "<no final response>")


if __name__ == "__main__":
    asyncio.run(main())
