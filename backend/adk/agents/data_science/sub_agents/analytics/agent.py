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

"""Analytics Agent: NL2Py data analysis using Vertex AI Code Interpreter."""

from __future__ import annotations

import logging
import os

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext
from google.adk.code_executors.vertex_ai_code_executor import VertexAiCodeExecutor
from google.genai import types

from .prompts import return_instructions_analytics

_logger = logging.getLogger(__name__)

# User agent identifier for API calls
USER_AGENT = "orkhon-data-science-agent"


def _create_code_executor():
  """Create a code executor, with graceful fallback if Vertex AI API is disabled.

  Returns:
    VertexAiCodeExecutor if available, None otherwise
  """
  try:
    return VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    )
  except Exception as e:
    _logger.warning(
        "Failed to initialize VertexAiCodeExecutor: %s. "
        "Analytics agent will run without code execution capability. "
        "To enable code execution, ensure Vertex AI API is enabled in your GCP project.",
        str(e)
    )
    return None


def setup_before_agent_call(callback_context: CallbackContext) -> None:
  """Setup callback executed before agent processes a request."""
  _logger.debug("Analytics agent setup_before_agent_call")


def get_analytics_agent() -> LlmAgent:
  """Create and configure the analytics agent.

  Returns:
    Configured LlmAgent instance for data analysis
  """
  code_executor = _create_code_executor()

  agent = LlmAgent(
      model=os.getenv("ANALYTICS_AGENT_MODEL", "gemini-2.0-flash-exp"),
      name="analytics_agent",
      instruction=return_instructions_analytics(),
      code_executor=code_executor,
      before_agent_callback=setup_before_agent_call,
      generate_content_config=types.GenerateContentConfig(temperature=0.01),
  )

  _logger.info("Analytics agent initialized with code executor: %s", 
               "enabled" if code_executor else "disabled")

  return agent


# For backwards compatibility, create a default instance
analytics_agent = get_analytics_agent()
