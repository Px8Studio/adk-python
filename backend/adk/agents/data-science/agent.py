"""
ADK agent entrypoint for the data-science app.

This module defines `root_agent` per ADK discovery convention so the
ADK Web server can load and run this app.
"""

from google.adk import Agent

# Minimal agent; extend with tools or plugins as needed.
root_agent = Agent(
    name="data-science",
    model="gemini-2.5-flash",
    instruction=(
        "You are a helpful data science assistant. Be concise and provide "
        "clear, actionable answers."
    ),
)
