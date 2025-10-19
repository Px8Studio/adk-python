# Orkhon Multi-Agent Architecture Analysis & Roadmap

## Executive Summary
- The multi-agent tree now has a clear hierarchy with `root_agent` delegating to DNB-specific coordinators and specialized agents.
- Both MCP Toolbox-backed tools and runtime OpenAPI toolchains are wired in, giving parity testing across execution paths.
- Workflow scaffolds for sequential and parallel flows exist but remain unused by coordinators.
- Additional coordinators, Google search tooling, A2A exposure, and automated validation still need attention.

## Current Architecture Snapshot

### Agent hierarchy
- `root_agent/agent.py`: LlmAgent that routes to DNB coordinators. Configuration comes from `ROOT_AGENT_MODEL` and the adjacent `instructions.txt` file.
- `api_coordinators/dnb_coordinator/agent.py`: LlmAgent that delegates to toolbox-backed specialists (`dnb_echo`, `dnb_statistics`, `dnb_public_register`). Supports optional OpenAPI variants via the `DNB_COORDINATOR_USE_OPENAPI` toggle.
- `api_coordinators/dnb_openapi_coordinator/agent.py`: LlmAgent that routes requests to runtime OpenAPIToolset agents for echo, statistics, and public-register APIs.
- `api_agents/dnb_echo`, `api_agents/dnb_statistics`, `api_agents/dnb_public_register`: LlmAgents wired to the MCP Toolbox server. Each provides domain-specific guidance and uses a single `ToolboxToolset`.
- `api_agents/dnb_openapi/agent.py`: Builds OpenAPIToolset toolsets from local spec files and exports both per-API and unified agents for experimentation.
- `api_agents/agent.py`: Package-level coordinator exposing all API specialists (toolbox plus unified OpenAPI) as a single entry point.
- `api_agents/google_search/agent.py`: Placeholder agent that reserves the structure for future Google tooling.
- `workflows/data_pipeline/agent.py` and `workflows/parallel_fetcher/agent.py`: Deterministic scaffolds for sequential and parallel orchestration that share state through `output_key`.

### Supporting infrastructure
- MCP Toolbox server (default `http://localhost:5000`) remains the primary tool execution path for DNB APIs.
- OpenAPI specs under `backend/apis/dnb/specs/` feed the runtime OpenAPIToolset builder.
- Instructions for the root agent and DNB coordinators live beside the agent modules, simplifying updates without code edits.

## Strengths
- Directory restructuring and naming now align with ADK guidance (relative package imports, `_agent` suffixes, and forward annotations).
- Root and coordinator agents separate instructions into files, making it easier to iterate on prompt tuning.
- Coordinators defensively clone their sub-agents, preventing shared toolset state when agents appear in multiple trees.
- Dual-path (Toolbox and OpenAPI) execution allows side-by-side regression testing without branching logic.
- Workflow scaffolds provide ready-made building blocks for deterministic pipelines once wired in.

## Active Gaps and Risks
1. **Workflow integration**: Sequential and parallel scaffolds are not yet invoked by coordinators, so complex multi-call flows still rely on LLM reasoning.
2. **Non-DNB domains**: Google search, data, and utility coordinators remain unimplemented; `google_search_agent` has no tools.
3. **A2A readiness**: Only `root_agent/agent.json` exists. There is no `a2a_config.yaml`, server bootstrap script, or automation for remote exposure.
4. **Testing and observability**: Smoke tests are manual, Jaeger dashboards are ad hoc, and there is no automated coverage for routing paths or OpenAPI toggles.
5. **Documentation drift**: Secondary docs (quick reference, READMEs) still reference the retired `dnb_agent` structure and should be updated.

## Recommended Next Steps

### Short term (1-2 weeks)
- Wire `workflows/data_pipeline` and `workflows/parallel_fetcher` into DNB flows where predictable fan-in/out is required.
- Implement a Google or data coordinator once the underlying tools are ready; guard the new coordinator behind a feature flag in `root_agent` until stable.
- Flesh out `google_search_agent` with a Toolbox or OpenAPI implementation plus smoke tests.
- Refresh Quick Reference and README content to reflect the current layout.

### Medium term (3-4 weeks)
- Define `a2a_config.yaml`, extend agent cards beyond the root agent, and add a helper script or VS Code task to launch the A2A server.
- Add regression smoke tests (pytest plus ADK harness) that cover the main routing paths and the OpenAPI fallback logic.
- Produce Jaeger dashboards or documentation showing expected traces for common flows.

### Long term
- Introduce advanced agents such as LoopAgent for pagination and custom agents for rate limiting or caching.
- Explore memory service integration and guardrails after deterministic workflows are established.

## Implementation Highlights

### Root Coordinator (`root_agent/agent.py`)
- Uses `ROOT_AGENT_MODEL` and `instructions.txt` for configuration.
- Delegates to `dnb_coordinator_agent` and `dnb_openapi_coordinator_agent` through `sub_agents`.
- Designed for future extensions by appending new coordinators to the list.

### DNB Coordinator (`api_coordinators/dnb_coordinator/agent.py`)
- Delegates to toolbox specialists by default.
- Supports the `DNB_COORDINATOR_USE_OPENAPI` environment toggle to swap in OpenAPI-driven agents without rewriting instructions.
- Clones sub-agents to ensure toolsets do not leak shared state when reused elsewhere.

### DNB OpenAPI Coordinator (`api_coordinators/dnb_openapi_coordinator/agent.py`)
- Routes to the OpenAPIToolset-based agents for echo, statistics, and public register APIs.
- Enables side-by-side testing of ADK OpenAPIToolset vs MCP Toolbox flows.

### Specialized DNB Agents (`api_agents/dnb_*`)
- Toolbox-backed agents expose domain guidance and enforce tool prefix usage.
- OpenAPI agents build toolsets on the fly from repository specs and automatically attach API keys via `token_to_scheme_credential`.
- Public Register logic emphasises discovery of valid register codes before invoking tools.

### Workflow Scaffolds (`workflows/`)
- `data_pipeline`: SequentialAgent executing validation, transformation, and analysis with explicit state hand-off.
- `parallel_fetcher`: ParallelAgent skeleton illustrating fan-out/fan-in patterns ready to be parameterised by coordinators.

### Package Coordinator (`api_agents/agent.py`)
- Consolidated entry point exposing all API specialists, including the unified OpenAPI agent and placeholder Google search agent.
- Useful when a single coordinator is embedded in tests or utilities without the full root agent hierarchy.

## Roadmap Status

| Phase | Focus | Status |
|-------|-------|--------|
| Phase 1 – Foundation | Directory restructuring, root coordinator, DNB routing | ✅ Complete |
| Phase 2 – Enhancement | Workflow integration, Google tooling, documentation refresh | 🚧 In progress |
| Phase 3 – Network | A2A configuration, remote exposure, observability | ⏳ Not started |
| Phase 4 – Expansion | Additional domains, advanced agents, guardrails | ⏳ Not started |

## References
- ADK documentation: `adk-docs/docs/agents/` and `adk-docs/docs/a2a/`
- MCP Toolbox configs: `backend/toolbox/config/dev/`
- OpenAPI specs: `backend/apis/dnb/specs/`
- Implementation examples: `backend/adk/agents/`

*Last updated: 2025-10-19*

