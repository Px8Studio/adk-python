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

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.load_artifacts_tool import load_artifacts_tool
from google.adk.tools.tool_context import ToolContext
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
    # Check if we have a cached extension ID to reuse
    cached_extension = os.getenv("CODE_INTERPRETER_EXTENSION_NAME")
    
    # Create executor with optional resource_name for caching
    executor = VertexAiCodeExecutor(
        resource_name=cached_extension,
    )
    
    # Log the extension ID for reuse in future sessions
    if hasattr(executor, '_code_interpreter_extension') and executor._code_interpreter_extension:
      extension_id = executor._code_interpreter_extension.resource_name
      if cached_extension:
        _logger.info(
            "Vertex AI Code Executor initialized (using cached extension: %s)",
            extension_id
        )
      else:
        _logger.info(
            "Vertex AI Code Executor initialized (new extension created). "
            "To reuse this extension, add to your .env file:\n"
            "CODE_INTERPRETER_EXTENSION_NAME=%s",
            extension_id
        )
    else:
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
      tools=[load_artifacts_tool],
      before_agent_callback=setup_before_agent_call,
      generate_content_config=types.GenerateContentConfig(temperature=0.01),
  )

  _logger.info("Analytics agent initialized with code executor: %s", 
               "enabled" if code_executor else "disabled")

  return agent


# For backwards compatibility, create a default instance
analytics_agent = get_analytics_agent()
