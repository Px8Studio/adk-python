"""
Google Search Agent - Performs web searches via Google Custom Search API.

[PLACEHOLDER - To be implemented]
"""

from __future__ import annotations

from google.adk.agents import LlmAgent as Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset
from .._common.config import get_model  # type: ignore

# Future implementation
google_search_agent = Agent(
    name="google_search",
    model=get_model("fast"),
    description="Performs web searches and retrieves information from Google",
    instruction="You help users search the web and find information.",
    tools=[
        # ToolboxToolset for Google Custom Search API tools (to be added)
    ],
)