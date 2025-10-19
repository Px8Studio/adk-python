# Orkhon Agent Implementation Examples

> **Implementation templates and code examples for the new multi-agent architecture**

## 📁 Directory Structure

```
backend/adk/agents/
├── orkhon_root/                    # NEW: Root coordinator
│   ├── __init__.py
│   ├── agent.py
│   ├── agent.json                  # A2A agent card
│   └── instructions.txt
├── api_coordinators/               # NEW: Category coordinators
│   ├── __init__.py
│   └── dnb_coordinator/
│       ├── __init__.py
│       ├── agent.py
│       ├── agent.json
│       └── instructions.txt
├── api_agents/                     # REFACTORED: Specialized agents
│   ├── __init__.py
│   ├── dnb_echo/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── dnb_statistics/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   └── boundary_toolset.py
│   ├── dnb_public_register/
│   │   ├── __init__.py
│   │   └── agent.py
│   └── google_search/              # FUTURE
│       ├── __init__.py
│       └── agent.py
└── workflows/                      # NEW: Workflow agents
    ├── __init__.py
    ├── data_pipeline/
    │   ├── __init__.py
    │   └── agent.py
    └── parallel_fetcher/
        ├── __init__.py
        └── agent.py
```

---

## 1️⃣ Root Coordinator Implementation

### `backend/adk/agents/orkhon_root/agent.py`

```python
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

"""
Orkhon Root Coordinator Agent

The top-level intelligent router for the Orkhon AI Platform.
Routes requests to specialized category coordinators.

Hierarchy:
  orkhon_root (this)
  ├─ dnb_coordinator       (DNB API operations)
  ├─ google_coordinator    (Google API operations - future)
  └─ data_coordinator      (Data processing - future)
"""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import LlmAgent as Agent

# Import category coordinators
# ADK adds the agents directory to sys.path, so these absolute imports work
from api_coordinators.dnb_coordinator.agent import dnb_coordinator_agent  # type: ignore

# Model configuration
MODEL = os.getenv("ORKHON_ROOT_MODEL", "gemini-2.0-flash")

# Load instructions from file for better maintainability
_INSTRUCTIONS_FILE = Path(__file__).parent / "instructions.txt"
if _INSTRUCTIONS_FILE.exists():
  INSTRUCTION = _INSTRUCTIONS_FILE.read_text(encoding="utf-8")
else:
  INSTRUCTION = """You are the Orkhon platform coordinator.

Your role:
1. Understand user requests across multiple domains
2. Route to appropriate category coordinators:
   - DNB API operations → dnb_coordinator_agent
   - Google searches → google_coordinator_agent (coming soon)
   - Data analysis → data_coordinator_agent (coming soon)
3. Synthesize responses from multiple coordinators when needed
4. Maintain conversational context across interactions

Guidelines:
- Be clear about which coordinator you're delegating to and why
- Provide concise summaries of results
- Handle multi-part requests intelligently
- Ask clarifying questions when user intent is ambiguous
- Preserve context for follow-up questions
"""

# Root agent definition
root_agent = Agent(
    name="orkhon_root",
    model=MODEL,
    description=(
        "Main coordinator for the Orkhon AI platform. Routes requests to "
        "specialized domain coordinators for API integrations, data processing, "
        "and utility operations. Handles multi-domain workflows and maintains "
        "conversational context."
    ),
    instruction=INSTRUCTION,
    # Sub-agents: LLM will use transfer_to_agent() to delegate
    sub_agents=[
        dnb_coordinator_agent,
        # Future coordinators will be added here:
        # google_coordinator_agent,
        # data_coordinator_agent,
    ],
    # Output key for tracking in state
    output_key="orkhon_root_response",
)

# Backwards compatibility alias
agent = root_agent
```

### `backend/adk/agents/orkhon_root/__init__.py`

```python
from __future__ import annotations

from .agent import root_agent

__all__ = ["root_agent"]
```

### `backend/adk/agents/orkhon_root/instructions.txt`

```text
You are the Orkhon platform coordinator, the main entry point for all user requests.

ROLE:
You intelligently route requests to specialized category coordinators based on user intent.

AVAILABLE COORDINATORS:
1. dnb_coordinator_agent
   - Handles all DNB (De Nederlandsche Bank) API operations
   - Use for: Dutch financial data, statistics, public register queries
   - Examples: "Get exchange rates", "Find pension fund statistics", "Search DNB licenses"

2. google_coordinator_agent (COMING SOON)
   - Handles Google API operations
   - Use for: Web searches, maps, calendar operations
   - Examples: "Search for X", "Find location Y"

3. data_coordinator_agent (COMING SOON)
   - Handles data processing workflows
   - Use for: Data validation, transformation, analysis
   - Examples: "Validate this dataset", "Analyze trends in data"

WORKFLOW:
1. Analyze user request
2. Identify which coordinator(s) are needed
3. Transfer to appropriate coordinator using transfer_to_agent()
4. If multiple coordinators needed, coordinate sequential execution
5. Synthesize final response from coordinator results

MULTI-DOMAIN REQUESTS:
- If request spans multiple domains, handle sequentially
- Maintain context between coordinator invocations
- Provide unified response that combines results

CONTEXT MANAGEMENT:
- Preserve conversation history
- Handle follow-up questions without re-routing unnecessarily
- Clarify ambiguous requests before routing

RESPONSE STYLE:
- Be clear about which coordinator you're using and why
- Provide concise summaries
- Cite data sources when relevant
- Guide users when capabilities are limited
```

### `backend/adk/agents/orkhon_root/agent.json` (A2A Agent Card)

```json
{
  "name": "orkhon_root",
  "version": "2.0.0",
  "description": "Main coordinator for Orkhon AI platform. Routes to specialized domain coordinators.",
  "capabilities": {
    "streaming": true,
    "artifacts": true,
    "tools": false,
    "sub_agents": true,
    "session_state": true
  },
  "sub_agents": [
    {
      "name": "dnb_coordinator_agent",
      "description": "DNB API operations coordinator"
    }
  ],
  "metadata": {
    "domain": "multi-domain-coordination",
    "vendor": "Orkhon",
    "contact": "team@orkhon.dev",
    "model": "gemini-2.0-flash",
    "pattern": "coordinator-dispatcher"
  },
  "endpoints": {
    "invoke": "/a2a/orkhon_root/invoke",
    "agent_card": "/a2a/orkhon_root/.well-known/agent-card"
  }
}
```

---

## 2️⃣ DNB Coordinator Implementation

### `backend/adk/agents/api_coordinators/dnb_coordinator/agent.py`

```python
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

"""
DNB API Coordinator Agent

Category coordinator for DNB (De Nederlandsche Bank) API operations.
Routes to specialized agents for Echo, Statistics, and Public Register APIs.

Hierarchy:
  orkhon_root
  └─ dnb_coordinator (this)
     ├─ dnb_echo_agent
     ├─ dnb_statistics_agent
     └─ dnb_public_register_agent
"""

from __future__ import annotations

import os
from pathlib import Path

from google.adk.agents import LlmAgent as Agent

# Import specialized DNB agents
from api_agents.dnb_echo.agent import dnb_echo_agent  # type: ignore
from api_agents.dnb_statistics.agent import dnb_statistics_agent  # type: ignore
from api_agents.dnb_public_register.agent import dnb_public_register_agent  # type: ignore

# Model configuration
MODEL = os.getenv("DNB_COORDINATOR_MODEL", "gemini-2.0-flash")

# Load instructions
_INSTRUCTIONS_FILE = Path(__file__).parent / "instructions.txt"
if _INSTRUCTIONS_FILE.exists():
  INSTRUCTION = _INSTRUCTIONS_FILE.read_text(encoding="utf-8")
else:
  INSTRUCTION = """You coordinate DNB API operations across three specialized domains:

1. **Echo API** (dnb_echo_agent):
   - Connectivity tests, health checks, API availability
   - Use for: "test DNB connection", "is DNB API up?"

2. **Statistics API** (dnb_statistics_agent):
   - Economic datasets, exchange rates, financial statistics
   - Use for: "get exchange rates", "pension fund data", "balance of payments"

3. **Public Register API** (dnb_public_register_agent):
   - License searches, registration data, regulatory info
   - Use for: "find licenses", "search institutions", "regulatory data"

Route to the appropriate specialist based on user request.
If multiple specialists needed, coordinate execution.
Provide clear, structured summaries."""

dnb_coordinator_agent = Agent(
    name="dnb_coordinator",
    model=MODEL,
    description=(
        "Coordinator for DNB (De Nederlandsche Bank) API operations. "
        "Routes to Echo (tests), Statistics (datasets), or Public Register "
        "(licenses/registrations) based on request type."
    ),
    instruction=INSTRUCTION,
    sub_agents=[
        dnb_echo_agent,
        dnb_statistics_agent,
        dnb_public_register_agent,
    ],
    output_key="dnb_coordinator_response",
)

# Backwards compatibility
agent = dnb_coordinator_agent
```

### `backend/adk/agents/api_coordinators/dnb_coordinator/__init__.py`

```python
from __future__ import annotations

from .agent import dnb_coordinator_agent

__all__ = ["dnb_coordinator_agent"]
```

### `backend/adk/agents/api_coordinators/dnb_coordinator/instructions.txt`

```text
You are the DNB API Coordinator, responsible for routing DNB-related requests to specialized agents.

SPECIALIZED AGENTS:

1. dnb_echo_agent
   Purpose: Connectivity and health checks
   Use cases:
   - "Test DNB API connection"
   - "Is the DNB API available?"
   - "Run a health check on DNB services"
   - "Get hello world from DNB"
   Tools: dnb-echo-helloworld, dnb-echo-health

2. dnb_statistics_agent  
   Purpose: Economic and financial statistics data
   Use cases:
   - "Get exchange rates for EUR/USD"
   - "Find pension fund statistics"
   - "Query balance of payments data"
   - "List available statistical datasets"
   - "Get metadata for DNB statistics"
   Tools: 79 statistics API tools
   
3. dnb_public_register_agent
   Purpose: License and registration searches
   Use cases:
   - "Search for financial institution licenses"
   - "Find registered entities in public register"
   - "Get details about a specific institution"
   - "List recent publications"
   Tools: publications_search, entities_search, entity_details

ROUTING LOGIC:

Simple requests:
- Identify the relevant specialist
- Transfer using: transfer_to_agent(agent_name="dnb_echo_agent")
- Let specialist handle the details

Multi-part requests:
- If request needs multiple specialists, handle sequentially
- Example: "Test connection and then get statistics"
  1. Transfer to dnb_echo_agent
  2. Wait for result in state
  3. Transfer to dnb_statistics_agent
  4. Combine results in response

Ambiguous requests:
- Ask clarifying questions
- Example: "Get DNB data" → "What type of DNB data? Statistics, licenses, or just testing connectivity?"

RESPONSE FORMAT:
- State which specialist handled the request
- Provide clear summary of results
- Include source attribution (which API was used)
- Format data for readability

ERROR HANDLING:
- If API call fails, explain the error clearly
- Suggest alternatives when appropriate
- Don't retry automatically (let user decide)
```

---

## 3️⃣ Specialized API Agent Example (Echo)

### `backend/adk/agents/api_agents/dnb_echo/agent.py`

```python
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

"""
DNB Echo Agent

Specialized agent for DNB Echo API operations.
Handles connectivity tests and health checks.

Hierarchy:
  orkhon_root → dnb_coordinator → dnb_echo_agent (this)
"""

from __future__ import annotations

import os

from google.adk.agents import LlmAgent as Agent
from google.adk.tools.toolbox_toolset import ToolboxToolset

# Configuration
_TOOLBOX_URL = os.getenv("TOOLBOX_SERVER_URL", "http://localhost:5000")
_TOOLSET_NAME = os.getenv("DNB_ECHO_TOOLSET_NAME", "dnb_echo_tools")
MODEL = os.getenv("DNB_ECHO_MODEL", "gemini-2.0-flash")

dnb_echo_agent = Agent(
    name="dnb_echo_agent",
    model=MODEL,
    description=(
        "Specialized agent for DNB Echo API. Performs connectivity tests, "
        "health checks, and API availability verification."
    ),
    instruction="""You are a specialist in DNB Echo API operations.

CAPABILITIES:
- Test API connectivity (helloworld endpoint)
- Check API health status
- Verify API availability

TOOLS AVAILABLE:
- dnb-echo-helloworld: Get hello world message from DNB
- dnb-echo-health: Check health status of DNB API
- dnb-echo-test: Test basic connectivity

GUIDELINES:
- Use ONLY tools whose names start with 'dnb-echo-'
- For other DNB operations, ask user to route to appropriate agent
- Provide clear status messages about connectivity
- Format results in a user-friendly way
- If API is down, provide helpful troubleshooting steps

RESPONSE FORMAT:
- Status: [OK/FAIL]
- Message: <result from API>
- Timestamp: <when test was run>
- Additional info: <any relevant details>
""",
    tools=[
        ToolboxToolset(
            server_url=_TOOLBOX_URL,
            toolset_name=_TOOLSET_NAME,
        ),
    ],
    output_key="dnb_echo_result",
)

# Backwards compatibility
agent = dnb_echo_agent
```

---

## 4️⃣ Workflow Agent Example (Sequential Pipeline)

### `backend/adk/agents/workflows/data_pipeline/agent.py`

```python
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

"""
Data Pipeline Workflow Agent

A SequentialAgent that implements a multi-step data processing pipeline:
  Validate → Transform → Analyze → Store

This is a workflow agent (not LLM-based) that executes sub-agents sequentially.
Each sub-agent is an LlmAgent that performs a specific step.
"""

from __future__ import annotations

from google.adk.agents import SequentialAgent, LlmAgent as Agent

# Step 1: Validation
data_validator = Agent(
    name="data_validator",
    model="gemini-2.0-flash",
    description="Validates input data against schema and business rules",
    instruction="""Validate the input data provided in the session state.

Check:
- Required fields are present
- Data types are correct
- Values are within acceptable ranges
- No malformed or suspicious data

Set state['validation_status'] to one of:
- 'valid': Data passed all checks
- 'invalid': Data failed validation (explain why)
- 'warning': Data has issues but can proceed (explain warnings)

Also set state['validation_details'] with specific findings.
""",
    output_key="validation_status",
)

# Step 2: Transformation
data_transformer = Agent(
    name="data_transformer",
    model="gemini-2.0-flash",
    description="Transforms data based on validation status",
    instruction="""Transform the data if validation passed.

Read state['validation_status']:
- If 'valid': Proceed with transformation
- If 'invalid': Skip transformation, preserve error info
- If 'warning': Transform with caution, log warnings

Transformation steps:
1. Normalize formats
2. Apply business rules
3. Enrich with additional data if needed
4. Standardize structure

Save result to state['transformed_data'].
If transformation fails, set state['transformation_error'].
""",
    output_key="transformed_data",
)

# Step 3: Analysis
data_analyzer = Agent(
    name="data_analyzer",
    model="gemini-2.0-flash",
    description="Analyzes transformed data and generates insights",
    instruction="""Analyze the transformed data.

Read state['transformed_data'] and generate:
- Summary statistics
- Key insights
- Anomalies or interesting patterns
- Recommendations

Save comprehensive analysis to state['insights'].
Include confidence levels for insights.
""",
    output_key="insights",
)

# Step 4: Storage (placeholder)
data_storer = Agent(
    name="data_storer",
    model="gemini-2.0-flash",
    description="Stores processed data and insights",
    instruction="""Store the processed data and insights.

Read from state:
- 'transformed_data': The processed data
- 'insights': The analysis results
- 'validation_details': Validation info for audit trail

Simulate storage operation (future: integrate with actual storage).
Set state['storage_status'] to 'success' or 'failed'.
Include storage location/reference.
""",
    output_key="storage_status",
)

# Complete pipeline: SequentialAgent
data_pipeline = SequentialAgent(
    name="data_pipeline",
    description=(
        "Sequential data processing pipeline: "
        "Validate → Transform → Analyze → Store"
    ),
    sub_agents=[
        data_validator,
        data_transformer,
        data_analyzer,
        data_storer,
    ],
)

# Usage in a parent agent:
# coordinator = Agent(
#     name="data_coordinator",
#     sub_agents=[data_pipeline, ...],
# )
# When invoked, data_pipeline will execute all 4 steps sequentially.
```

---

## 5️⃣ Workflow Agent Example (Parallel Fetcher)

### `backend/adk/agents/workflows/parallel_fetcher/agent.py`

```python
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

"""
Parallel API Fetcher Workflow

A ParallelAgent + SequentialAgent combination for concurrent API fetching
followed by result aggregation.

Pattern: Parallel Fan-Out → Sequential Gather

Use case: When you need to fetch data from multiple APIs simultaneously
and then combine the results.
"""

from __future__ import annotations

from google.adk.agents import ParallelAgent, SequentialAgent, LlmAgent as Agent

# Parallel fetch agents (these run concurrently)
api1_fetcher = Agent(
    name="api1_fetcher",
    model="gemini-2.0-flash",
    description="Fetches data from API source 1",
    instruction="""Fetch data from API source 1 based on request parameters.
    
Save result to state['api1_result'].
Include metadata: timestamp, status, record_count.
""",
    output_key="api1_result",
)

api2_fetcher = Agent(
    name="api2_fetcher",
    model="gemini-2.0-flash",
    description="Fetches data from API source 2",
    instruction="""Fetch data from API source 2 based on request parameters.
    
Save result to state['api2_result'].
Include metadata: timestamp, status, record_count.
""",
    output_key="api2_result",
)

api3_fetcher = Agent(
    name="api3_fetcher",
    model="gemini-2.0-flash",
    description="Fetches data from API source 3",
    instruction="""Fetch data from API source 3 based on request parameters.
    
Save result to state['api3_result'].
Include metadata: timestamp, status, record_count.
""",
    output_key="api3_result",
)

# ParallelAgent executes all fetchers concurrently
parallel_fetch_step = ParallelAgent(
    name="parallel_fetch",
    description="Fetches from multiple APIs concurrently",
    sub_agents=[
        api1_fetcher,
        api2_fetcher,
        api3_fetcher,
    ],
)

# Aggregator runs after parallel fetch completes
result_aggregator = Agent(
    name="result_aggregator",
    model="gemini-2.0-flash",
    description="Aggregates results from parallel API fetches",
    instruction="""Aggregate results from parallel API calls.

Read from state:
- api1_result: Data from source 1
- api2_result: Data from source 2
- api3_result: Data from source 3

Tasks:
1. Combine all results into unified structure
2. Identify common patterns across sources
3. Resolve conflicts if data disagrees
4. Generate summary statistics
5. Highlight unique findings from each source

Save comprehensive result to state['aggregated_result'].
Include confidence scores and source attribution.
""",
    output_key="aggregated_result",
)

# Complete workflow: Parallel fetch, then sequential aggregation
parallel_fetcher_workflow = SequentialAgent(
    name="parallel_fetcher_workflow",
    description="Fetches from multiple APIs in parallel, then aggregates",
    sub_agents=[
        parallel_fetch_step,  # Runs parallel fetchers
        result_aggregator,    # Runs after parallel completes
    ],
)

# Example usage in DNB coordinator for concurrent queries:
#
# dnb_parallel_fetcher = SequentialAgent(
#     name="dnb_multi_source_fetcher",
#     sub_agents=[
#         ParallelAgent(
#             name="dnb_parallel_apis",
#             sub_agents=[
#                 dnb_statistics_agent,
#                 dnb_public_register_agent,
#             ],
#         ),
#         result_aggregator,
#     ],
# )
```

---

## 6️⃣ A2A Server Configuration

### `backend/adk/a2a_config.yaml`

```yaml
# A2A Server Configuration for Orkhon Platform
# Enables agent-to-agent communication over network

server:
  host: "0.0.0.0"
  port: 8001
  cors_enabled: true
  cors_origins:
    - "http://localhost:4200"
    - "http://localhost:8000"

# Agents exposed via A2A
agents:
  - name: "orkhon_root"
    module: "orkhon_root.agent"
    agent_var: "root_agent"
    enabled: true
    expose_externally: true
    description: "Main Orkhon coordinator"
    
  - name: "dnb_coordinator"
    module: "api_coordinators.dnb_coordinator.agent"
    agent_var: "dnb_coordinator_agent"
    enabled: true
    expose_externally: true
    description: "DNB API coordinator"

# Telemetry & Observability
telemetry:
  enabled: true
  service_name: "orkhon-a2a-server"
  jaeger_endpoint: "http://localhost:4318"
  trace_all_requests: true

# Security (future)
security:
  require_auth: false  # Set to true in production
  api_key_header: "X-Orkhon-API-Key"
  allowed_ips: []  # Empty = allow all

# Logging
logging:
  level: "INFO"
  format: "json"
  include_request_body: true
  include_response_body: false  # Can be large
```

### `backend/adk/start_a2a_server.py`

```python
#!/usr/bin/env python3
"""
Start A2A Server for Orkhon Platform

Exposes agents via Agent-to-Agent protocol for remote invocation.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from a2a.server import A2AServer
from google.adk.agents.loader import load_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
  """Start the A2A server with registered agents."""
  
  config_path = Path(__file__).parent / "a2a_config.yaml"
  
  logger.info("Starting Orkhon A2A Server...")
  logger.info(f"Config: {config_path}")
  
  # Create server
  server = A2AServer(config_path=str(config_path))
  
  # Register agents
  logger.info("Registering agents...")
  
  try:
    # Load and register root agent
    root_agent = load_agent("orkhon_root.agent", "root_agent")
    server.register_agent("orkhon_root", root_agent)
    logger.info("✓ Registered: orkhon_root")
    
    # Load and register DNB coordinator
    dnb_coordinator = load_agent(
        "api_coordinators.dnb_coordinator.agent",
        "dnb_coordinator_agent"
    )
    server.register_agent("dnb_coordinator", dnb_coordinator)
    logger.info("✓ Registered: dnb_coordinator")
    
  except Exception as e:
    logger.error(f"Failed to register agents: {e}")
    raise
  
  # Start server
  logger.info("Starting server on http://0.0.0.0:8001")
  logger.info("Agent cards available at:")
  logger.info("  - http://localhost:8001/a2a/orkhon_root/.well-known/agent-card")
  logger.info("  - http://localhost:8001/a2a/dnb_coordinator/.well-known/agent-card")
  
  await server.start()


if __name__ == "__main__":
  asyncio.run(main())
```

---

## 7️⃣ Environment Configuration

### `.env.example` (add to existing)

```bash
# Orkhon Agent Configuration

# Model Selection
ORKHON_ROOT_MODEL=gemini-2.0-flash
DNB_COORDINATOR_MODEL=gemini-2.0-flash
DNB_ECHO_MODEL=gemini-2.0-flash
DNB_STATISTICS_MODEL=gemini-2.0-flash
DNB_PUBLIC_REGISTER_MODEL=gemini-2.0-flash

# Toolbox Configuration
TOOLBOX_SERVER_URL=http://localhost:5000
DNB_ECHO_TOOLSET_NAME=dnb_echo_tools
DNB_STATISTICS_TOOLSET_NAME=dnb_statistics_tools
DNB_PUBLIC_REGISTER_TOOLSET_NAME=dnb_public_register_tools

# A2A Server Configuration
A2A_SERVER_ENABLED=false
A2A_SERVER_HOST=0.0.0.0
A2A_SERVER_PORT=8001

# Observability
OTEL_SERVICE_NAME=orkhon-agents
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

---

## 8️⃣ Migration Script

### `backend/adk/migrate_agents.py`

```python
#!/usr/bin/env python3
"""
Migration script to move from old agent structure to new architecture.

Usage:
  python migrate_agents.py --dry-run  # Show what would be done
  python migrate_agents.py            # Perform migration
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def migrate_agents(agents_dir: Path, dry_run: bool = False):
  """Migrate agents to new structure."""
  
  print("🔄 Orkhon Agent Migration")
  print("=" * 60)
  
  if dry_run:
    print("🔍 DRY RUN MODE - No changes will be made")
    print()
  
  # Step 1: Create new directories
  new_dirs = [
      agents_dir / "orkhon_root",
      agents_dir / "api_coordinators" / "dnb_coordinator",
      agents_dir / "api_agents" / "dnb_echo",
      agents_dir / "api_agents" / "dnb_statistics",
      agents_dir / "api_agents" / "dnb_public_register",
      agents_dir / "workflows" / "data_pipeline",
      agents_dir / "workflows" / "parallel_fetcher",
  ]
  
  print("📁 Creating new directories:")
  for new_dir in new_dirs:
    if not dry_run:
      new_dir.mkdir(parents=True, exist_ok=True)
      (new_dir / "__init__.py").touch()
    print(f"  ✓ {new_dir.relative_to(agents_dir)}")
  print()
  
  # Step 2: Copy existing agents to new locations
  migrations = [
      ("dnb_api_echo", "api_agents/dnb_echo"),
      ("dnb_api_statistics", "api_agents/dnb_statistics"),
      ("dnb_api_public_register", "api_agents/dnb_public_register"),
  ]
  
  print("📦 Copying existing agents:")
  for old_name, new_path in migrations:
    old_dir = agents_dir / old_name
    new_dir = agents_dir / new_path
    
    if old_dir.exists():
      if not dry_run:
        shutil.copytree(old_dir, new_dir, dirs_exist_ok=True)
      print(f"  ✓ {old_name} → {new_path}")
    else:
      print(f"  ⚠️  {old_name} not found (skipping)")
  print()
  
  # Step 3: Create placeholder files
  print("📝 Creating new agent files:")
  print("  ℹ️  Use implementation examples from AGENT_IMPLEMENTATION_EXAMPLES.md")
  print()
  
  # Step 4: Summary
  print("=" * 60)
  print("✅ Migration complete!")
  print()
  print("Next steps:")
  print("1. Review generated structure")
  print("2. Implement new agents using examples from documentation")
  print("3. Update imports in existing code")
  print("4. Test each agent individually")
  print("5. Test complete hierarchy")
  print("6. Remove old dnb_agent directory when confident")


def main():
  parser = argparse.ArgumentParser(description="Migrate Orkhon agents")
  parser.add_argument(
      "--dry-run",
      action="store_true",
      help="Show what would be done without making changes"
  )
  parser.add_argument(
      "--agents-dir",
      type=Path,
      default=Path(__file__).parent / "agents",
      help="Path to agents directory"
  )
  
  args = parser.parse_args()
  
  if not args.agents_dir.exists():
    print(f"❌ Error: Agents directory not found: {args.agents_dir}")
    sys.exit(1)
  
  migrate_agents(args.agents_dir, args.dry_run)


if __name__ == "__main__":
  main()
```

---

## 9️⃣ Testing Strategy

### `backend/adk/tests/test_agent_hierarchy.py`

```python
"""
Tests for new agent hierarchy.

Run with: pytest backend/adk/tests/test_agent_hierarchy.py
"""

from __future__ import annotations

import pytest
from google.adk.agents import LlmAgent
from google.adk.runner import Runner


@pytest.fixture
def root_agent():
  """Load root agent for testing."""
  from orkhon_root.agent import root_agent
  return root_agent


@pytest.fixture
def dnb_coordinator():
  """Load DNB coordinator for testing."""
  from api_coordinators.dnb_coordinator.agent import dnb_coordinator_agent
  return dnb_coordinator_agent


def test_root_agent_structure(root_agent):
  """Test root agent has correct structure."""
  assert root_agent.name == "orkhon_root"
  assert isinstance(root_agent, LlmAgent)
  assert len(root_agent.sub_agents) >= 1  # Should have dnb_coordinator


def test_dnb_coordinator_structure(dnb_coordinator):
  """Test DNB coordinator has correct structure."""
  assert dnb_coordinator.name == "dnb_coordinator"
  assert isinstance(dnb_coordinator, LlmAgent)
  assert len(dnb_coordinator.sub_agents) == 3  # Echo, Stats, PR


def test_agent_hierarchy(root_agent):
  """Test complete agent hierarchy."""
  # Root should have dnb_coordinator
  dnb_coord = root_agent.find_agent("dnb_coordinator")
  assert dnb_coord is not None
  
  # DNB coordinator should have 3 sub-agents
  echo = dnb_coord.find_agent("dnb_echo_agent")
  stats = dnb_coord.find_agent("dnb_statistics_agent")
  pr = dnb_coord.find_agent("dnb_public_register_agent")
  
  assert echo is not None
  assert stats is not None
  assert pr is not None


@pytest.mark.asyncio
async def test_root_agent_routing(root_agent):
  """Test root agent can route to DNB coordinator."""
  runner = Runner(agent=root_agent)
  
  # Test simple routing
  result = await runner.run("Test DNB API connection")
  
  # Should invoke dnb_coordinator → dnb_echo_agent
  assert result is not None
  # Add more specific assertions based on expected behavior


@pytest.mark.asyncio
async def test_dnb_echo_agent(dnb_coordinator):
  """Test DNB echo agent directly."""
  runner = Runner(agent=dnb_coordinator)
  
  result = await runner.run("Run hello world test")
  
  # Should invoke dnb_echo_agent and call helloworld tool
  assert result is not None
  # Check for expected response structure
```

---

## 🔟 Quick Start After Migration

### 1. Test Individual Agents

```bash
# Test root agent
adk run orkhon_root -q "Hello, what can you do?"

# Test DNB coordinator
adk run api_coordinators.dnb_coordinator -q "Test DNB connection"

# Test specific agent
adk run api_agents.dnb_echo -q "Run hello world"
```

### 2. Start ADK Web with New Structure

```bash
cd backend/adk
adk web --reload_agents agents/
```

### 3. Start A2A Server (Optional)

```bash
cd backend/adk
python start_a2a_server.py
```

### 4. Test from UI

Navigate to http://localhost:8000 and select "orkhon_root"

Try queries:
- "Test DNB API connection"
- "Get DNB statistics for exchange rates"
- "Search DNB public register"
- "Run hello world from echo API"

---

## 📚 Additional Resources

- **ADK Documentation**: `/adk-docs/docs/agents/`
- **Sample Agents**: `/adk-samples/python/agents/`
- **Architecture Analysis**: `AGENT_ARCHITECTURE_ANALYSIS.md`
- **Architecture Diagram**: `AGENT_ARCHITECTURE_DIAGRAM.md`

---

*Last Updated: 2025-01-19*
*Version: 1.0*
