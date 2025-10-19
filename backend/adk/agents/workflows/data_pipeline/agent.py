"""Data Pipeline (Sequential) scaffold."""

from __future__ import annotations

from google.adk.agents import SequentialAgent, LlmAgent as Agent

validator = Agent(
    name="data_validator",
    instruction="Validate the provided input and set 'validation_status' to OK or ERROR.",
    output_key="validation_status",
)

transformer = Agent(
    name="data_transformer",
    instruction=(
        "If {validation_status} is OK, transform the input and set 'transformed_data'. "
        "Otherwise provide a reason."
    ),
    output_key="transformed_data",
)

analyzer = Agent(
    name="data_analyzer",
    instruction=(
        "Analyze {transformed_data} and produce insights; set 'insights' in state."
    ),
    output_key="insights",
)

data_pipeline = SequentialAgent(
    name="data_pipeline",
    instruction="Run validation, transformation, and analysis in order.",
    sub_agents=[validator, transformer, analyzer],
)

__all__ = [
    "data_pipeline",
]
