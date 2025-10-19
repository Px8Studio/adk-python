# Orkhon Multi-Agent Architecture Diagram

## Agent Tree Overview (October 2025)

```
root_agent (LlmAgent, gemini-2.0-flash)
├─ dnb_coordinator (LlmAgent, Toolbox path)
│  ├─ dnb_echo_agent (ToolboxToolset: dnb_echo_tools)
│  ├─ dnb_statistics_agent (ToolboxToolset: dnb_statistics_tools)
│  └─ dnb_public_register_agent (ToolboxToolset: dnb_public_register_tools)
├─ dnb_openapi_coordinator (LlmAgent, OpenAPIToolset path)
│  ├─ dnb_openapi_echo_agent (OpenAPIToolset ← openapi3-echo-api.yaml)
│  ├─ dnb_openapi_statistics_agent (OpenAPIToolset ← openapi3_statisticsdatav2024100101.yaml)
│  └─ dnb_openapi_public_register_agent (OpenAPIToolset ← openapi3_publicdatav1.yaml)
└─ [future] google_coordinator / data_coordinator / utility_coordinator
```

### Key Notes
- `root_agent` delegates through `sub_agents`. Instructions live in `root_agent/instructions.txt`.
- `dnb_coordinator` defaults to Toolbox-backed specialists but honours `DNB_COORDINATOR_USE_OPENAPI` to swap in OpenAPI variants.
- `dnb_openapi_coordinator` mounts the OpenAPI agents directly for runtime tool generation.
- Each specialized agent is an LlmAgent exposing a single toolset to keep prompts simple.

## Package-Level Coordinator (`api_agents/agent.py`)
- Provides a consolidated entry point that exposes all DNB specialists (Toolbox) plus the unified OpenAPI agent and the placeholder Google search agent.
- Useful for scripts or tests that want a single agent without the higher-level `root_agent` hierarchy.

## Workflow Scaffolds (`workflows/`)

```
data_pipeline (SequentialAgent)
  ├─ data_validator  → output_key="validation_status"
  ├─ data_transformer → output_key="transformed_data"
  └─ data_analyzer   → output_key="insights"

parallel_api_fetcher (ParallelAgent)
  ├─ api1_fetcher → output_key="api1_result"
  ├─ api2_fetcher → output_key="api2_result"
  └─ result_aggregator → output_key="aggregated_result"
```

- Both agents are scaffolds. Coordinators should clone or pass in real specialists before use.
- Deterministic flows (validate→transform→analyze, fan-out/fan-in) reduce LLM token cost when wired into coordinators.

## Tool Execution Paths

| Path | Source | Tool layer | Auth | Typical use |
|------|--------|------------|------|--------------|
| Toolbox | `api_agents/dnb_*` | MCP Toolbox server (`http://localhost:5000`) | API key stored in Toolbox config | Stable day-to-day execution |
| OpenAPI | `api_agents/dnb_openapi/*` | ADK OpenAPIToolset (specs under `backend/apis/dnb/specs`) | `token_to_scheme_credential` adds header | Experiments, schema drift validation |

- Both routes emit OpenTelemetry spans through the Toolbox service and ADK adapters.

## Data Flow Example

1. User query enters `root_agent`.
2. `root_agent` transfers to `dnb_coordinator` (Toolbox path) or `dnb_openapi_coordinator` (OpenAPI path) based on instructions or operator choice.
3. Coordinator delegates to one or more specialists via `transfer_to_agent`.
4. Specialist invokes toolset:
   - Toolbox: REST call → MCP Toolbox → DNB API.
   - OpenAPI: Generated tool → direct HTTP call defined by spec.
5. Specialist writes results to state via `output_key`.
6. Coordinator aggregates and returns to `root_agent`, which formats the final reply.

## Supporting Infrastructure
- **Toolbox server**: Docker Compose service `genai-toolbox-mcp`, config in `backend/toolbox/config/dev/`.
- **OpenAPI specs**: `backend/apis/dnb/specs/` feed runtime tool generation.
- **Jaeger**: Optional tracing at `http://localhost:16686`; spans show `root_agent → coordinator → specialist → tool` chain.

## A2A Status
- `root_agent/agent.json` is present; other agent cards are pending.
- No `a2a_config.yaml` or server bootstrap script yet—add during Phase 3 of the roadmap.

## Next Additions
- Implement Google/data/utility coordinators when toolsets become available.
- Wire workflow scaffolds into coordinators for predictable multi-call flows.
- Extend agent cards and automation to publish coordinators over A2A.

*Last updated: 2025-10-19*
