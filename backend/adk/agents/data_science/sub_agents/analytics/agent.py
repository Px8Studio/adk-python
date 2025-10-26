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
from google.adk.tools.load_artifacts_tool import load_artifacts_tool  # Import the actual tool instance
from google.adk.tools import ToolContext
from google.adk.code_executors.vertex_ai_code_executor import VertexAiCodeExecutor
from google.genai import types

from .prompts import return_instructions_analytics

_logger = logging.getLogger(__name__)

# User agent identifier for API calls
USER_AGENT = "orkhon-data-science-agent"


def _create_code_executor():
  """Create and configure the Vertex AI Code Executor.

  Returns:
    Configured VertexAiCodeExecutor instance, or None if disabled
  """
  # Check if code execution is disabled via environment variable
  if os.getenv("DISABLE_CODE_EXECUTION", "").lower() == "true":
    _logger.info("Code execution is disabled via DISABLE_CODE_EXECUTION env var")
    return None

  try:
    # Create executor with project and region from environment
    executor = VertexAiCodeExecutor(
        project_id=os.getenv("GCP_PROJECT_ID"),
        region=os.getenv("GCP_REGION", "us-central1"),
    )
    _logger.info("Vertex AI Code Executor initialized successfully")
    return executor
  except Exception as e:
    _logger.error(f"Failed to initialize code executor: {e}")
    return None


def setup_before_agent_call(callback_context: CallbackContext) -> None:
  """Setup callback executed before agent processes a request."""
  tool_context = ToolContext(user_agent=USER_AGENT)
  callback_context.tool_context = tool_context


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
      tools=[load_artifacts_tool],  # ✅ Now passing the tool instance
      before_agent_callback=setup_before_agent_call,
      generate_content_config=types.GenerateContentConfig(temperature=0.01),
  )

  _logger.info("Analytics agent initialized with code executor: %s", 
               "enabled" if code_executor else "disabled")

  return agent


# For backwards compatibility, create a default instance
analytics_agent = get_analytics_agent()
