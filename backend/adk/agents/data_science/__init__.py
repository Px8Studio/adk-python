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

"""Orkhon Data Science Coordinator Agent.

A domain-level coordinator for data science operations within the Orkhon
multi-agent system. This agent integrates BigQuery database access and
Python analytics capabilities via specialized sub-agents.

Integration Pattern:
  This agent is designed as a sub-agent of the Orkhon root_agent. The
  run_data_science_agent.py script is provided for development/testing only.
"""

from __future__ import annotations

from .agent import root_agent as data_science_coordinator

__all__ = ["data_science_coordinator"]
