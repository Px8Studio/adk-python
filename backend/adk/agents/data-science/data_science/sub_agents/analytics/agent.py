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

"""Analytics Agent: generate nl2py and use code interpreter to run the code."""
import os
try:
    from _common.config import get_llm_model, get_model  # type: ignore
except Exception:  # pragma: no cover
    def get_llm_model() -> str:
        return os.getenv("ORKHON_LLM_MODEL") or os.getenv("ROOT_AGENT_MODEL") or os.getenv("GOOGLE_GEMINI_MODEL") or "gemini-2.5-flash"
    def get_model(profile: str) -> str:
        return get_llm_model()

from google.adk.agents import Agent
from google.adk.code_executors import VertexAiCodeExecutor
# from google.adk.tools import load_artifacts  # removed, not callable inside CI Python
from google.genai import types

from .prompts import return_instructions_analytics


analytics_agent = Agent(
    model=os.getenv("ANALYTICS_AGENT_MODEL", ""),
    name="analytics_agent",
    instruction=return_instructions_analytics(),
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,
    ),
)
