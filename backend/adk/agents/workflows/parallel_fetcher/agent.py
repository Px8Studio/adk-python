"""Parallel API Fetcher scaffold."""

from __future__ import annotations

from google.adk.agents import ParallelAgent, LlmAgent as Agent

# Placeholder fetchers; real sub-agents should be injected by the coordinator when used
api1_fetcher = Agent(
    name="api1_fetcher",
    instruction="Fetch data from API 1 and set state under 'api1_result'",
    output_key="api1_result",
)

api2_fetcher = Agent(
    name="api2_fetcher",
    instruction="Fetch data from API 2 and set state under 'api2_result'",
    output_key="api2_result",
)

result_aggregator = Agent(
    name="result_aggregator",
    instruction=(
        "Aggregate results from {api1_result} and {api2_result}. "
        "Provide a concise summary."
    ),
    output_key="aggregated_result",
)

parallel_api_fetcher = ParallelAgent(
    name="parallel_api_fetcher",
    instruction="Run multiple API fetchers in parallel and aggregate results.",
    sub_agents=[api1_fetcher, api2_fetcher, result_aggregator],
)

__all__ = [
    "parallel_api_fetcher",
]
