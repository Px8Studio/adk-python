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
    from ...._common.config import get_llm_model, get_model  # type: ignore
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


class DataScienceAnalyticsAgent(Agent):
    """Subclass to ensure the runner detects the data_science origin."""


# Remove region normalization and env warnings; rely on executor defaults
if not os.getenv("CODE_INTERPRETER_EXTENSION_NAME"):
  # Not fatal; executor can still provision or use defaults in many setups.
  import logging
  logging.getLogger(__name__).warning(
      "CODE_INTERPRETER_EXTENSION_NAME not set; relying on default executor behavior."
  )

def _normalize_extension_name_by_region(ext: str | None) -> str | None:
  """Keep provided extension even if its region differs; just warn."""
  if not ext:
    return None
  try:
    import logging
    loc = os.getenv("GOOGLE_CLOUD_LOCATION", "").strip()
    if "/locations/" in ext:
      ext_loc = ext.split("/locations/")[1].split("/")[0]
      if loc and ext_loc and ext_loc != loc:
        logging.getLogger(__name__).warning(
            "CODE_INTERPRETER_EXTENSION_NAME location '%s' != "
            "GOOGLE_CLOUD_LOCATION '%s'. Using the provided extension "
            "cross-region.",
            ext_loc,
            loc,
        )
    return ext
  except Exception:
    return ext

_extension_name = _normalize_extension_name_by_region(
  os.getenv("CODE_INTERPRETER_EXTENSION_NAME")
)

analytics_agent = DataScienceAnalyticsAgent(
  model=os.getenv("ANALYTICS_AGENT_MODEL") or get_model("smart"),
  name="analytics_agent",
  instruction=return_instructions_analytics(),
  # tools=[load_artifacts],  # removed; Vertex executor will collect output_files
  code_executor=VertexAiCodeExecutor(),
  generate_content_config=types.GenerateContentConfig(
    temperature=0.1,
  ),
)
