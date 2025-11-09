# ADK Sample Agents – Production-Oriented Recommendation Shortlist

This document curates a shortlist of Python ADK sample agents to form a robust, future‑proof foundation for Orkhon’s multi‑agent AI platform. It emphasizes patterns that will scale when we later add non‑ADK agents (LangChain / LangGraph) while maintaining guardrails, observability, and extensibility.

---
## 1. Selection Criteria
Agents were evaluated against the following pragmatic production readiness signals:

| Criterion | Why It Matters | Signals Used |
|-----------|----------------|--------------|
| Architectural Pattern | Reusable orchestration primitives | Clear multi-agent layering, sub-agent specialization, App/Runner usage |
| Tooling Diversity | Demonstrates integration envelope | Built-in tools, MCP, external APIs, database, retrieval |
| Evaluation & Tests | Confidence + baselines for regression | Presence of `tests/` and `eval/` directories with scripts |
| Deployment Examples | Accelerates Cloud Run / Agent Engine path | README shows Vertex AI / Cloud Run steps |
| Modularity / Config | Ease of selective capability import | Environment variables, pluggable sub-agents, dataset config |
| Safety / Governance | Early trust & compliance posture | Guardrail plugins, auditing, fact-checking |
| Adaptability to Orkhon Domain | Finance / analytics / compliance fit | Natural language → data, verification, reporting |

---
## 2. Recommended Core Foundation (Adopt First)
| Agent | Role in Orkhon | Rationale | Key Patterns to Reuse |
|-------|----------------|-----------|-----------------------|
| Data Science (multi-agent) | Analytical reasoning / NL2SQL / ML exploration | Mature multi-agent orchestration; cross-dataset config; code+SQL blending | Dataset config JSON, sub-agent segmentation (DB / BQML / DS) |
| Machine Learning Engineering (MLE-STAR) | Automated model experimentation & refinement | Iterative targeted code block refinement + search → high performance loop | Inner / outer refinement loops, task workspace separation |
| LLM Auditor | Factual verification & compliance layer | Lightweight multi-agent audit pipeline; claim extraction + rewrite | Critic/Reviser pattern; attach as post-processing stage |
| RAG (Documentation Retrieval Agent) | Internal knowledge grounding | Clean single-agent retrieval pattern leveraging Vertex RAG; citation discipline | Retrieval gating, tool invocation expectation evaluation |
| Software Bug Assistant | Internal ops + incident triage | Blends DB (tickets) + MCP + search + external sources; good ops template | MCP toolbox integration; mixed internal/external knowledge routing |
| Safety Plugins (Gemini Judge + Model Armor) | Global safety / session poisoning prevention | Demonstrates plugin hooks across model, tool, user message boundaries | Runner-level plugin injection; callback surfaces for future policy |
| Gemini Fullstack | Research workflow + HITL planning UX | End-to-end user approval loop then autonomous execution + citations | Plan→Approval→Iterative research→Critique→Compose workflow graph |

---
## 3. Secondary / Conditional Additions (Adopt Later)
| Agent | Reason to Defer | Future Trigger |
|-------|-----------------|---------------|
| Customer Service (Retail) | Mocked tools; vertical-specific state model | When building multimodal customer‑facing flows (voice/video) |
| Data Engineering | Narrow Dataform focus; similar patterns already in Data Science | When orchestrating transformation authoring at scale |
| Incident Management | Requires ServiceNow + Integration Connectors setup overhead | When dynamic identity propagation becomes a requirement |
| Order Processing | Workflow deterministic + HITL specific to order domain | After establishing general Application Integration connector strategy |
| Real-Time Conversational | Live audio/video adds infra complexity early | When enabling Gemini Live bi-directional streaming to users |
| Marketing / Travel / Vertical demos | Domain-specific content only | Product vertical pivot or demo scenario needs |
| Image Scoring | Imagen / policy scoring specialized | Visual moderation expansion |

---
## 4. Integration Sequencing (Phased)
1. Baseline Core Orkhon Agents: Data Science + LLM Auditor + RAG (establish data + verification + retrieval triad).
2. Introduce Safety Plugins globally via Runner (enforce hooks before broad usage growth).
3. Add Software Bug Assistant for internal reliability + toolchain debugging (observability synergy with Jaeger).
4. Onboard MLE-STAR for advanced model building tasks (ensure resource isolation & quota guards).
5. Integrate Gemini Fullstack planning components into research/reporting workflows (wrap with Orkhon auth + session layer).
6. Expand toward vertical / real-time agents if strategic need emerges.

---
## 5. Mapping to Orkhon Logical Personas
| Orkhon Layer | Recommended Agent(s) | Notes |
|--------------|----------------------|-------|
| Ingestion / External Data | Software Bug Assistant (tickets), Data Science (BigQuery/AlloyDB), RAG (docs) | Leverage existing DNB ingestion flows; treat these as post-ingest reasoning |
| Analytical Reasoning | Data Science, MLE-STAR | Separate compute; consider future Cloud Run service split |
| Governance / Safety | LLM Auditor, Safety Plugins | Attach as pipeline steps; auditor optionally invoked per message or batch |
| Retrieval / Knowledge | RAG | Provide internal corpus overlay (DNB directives, compliance manuals) |
| Research & Synthesis | Gemini Fullstack | Used for multi-step strategic summaries and reports |
| Ops & Observability | Software Bug Assistant | Internal tool triage; integrate with existing tracing + metrics |

---
## 6. Minimal Adaptation Checklist per Agent
| Agent | Immediate Adapt | Medium-Term Hardening |
|-------|-----------------|-----------------------|
| Data Science | Strip sample dataset loading; mount Orkhon dataset config; integrate BigQuery quotas | Add cost guardrails, structured audit events, output schema contracts |
| MLE-STAR | Constrain search scope; sandbox code execution; add timeouts | Add result caching; provenance logging for imported code blocks |
| LLM Auditor | Convert to sidecar plugin invoked after generation | Add policy taxonomy mapping (fact vs policy vs safety) |
| RAG | Point to internal corpus; unify citation format | Add freshness scoring; fallback path if retrieval low confidence |
| Software Bug Assistant | Replace sample tickets DB with Orkhon incident schema; configure MCP secure auth | Enable vector similarity over incident logs; auto root cause summarizer |
| Safety Plugins | Parameterize blocked message templates; integrate alerting | Policy versioning; metrics export (blocked_count, false_positive_rate) |
| Gemini Fullstack | Decouple React UI; reuse planning agents under Orkhon API | Formal plan revision diffing; plan storage for analytics |

---
## 7. Cross-Cutting Productionization Tasks
- Auth & Isolation: Namespacing sessions by `user_id:session_uuid`; restrict tool invocation surfaces.
- Observability: Add trace spans per sub-agent; log prompt+tool call metadata (redact secrets). 
- Quota / Cost: Central rate limiting (LLM calls per minute; retrieval queries; DB queries).
- Evaluation Harness: Standardize success metrics (tool trajectory score, response faithfulness, latency p95) across agents.
- Model / Tool Version Registry: Record model IDs and toolset commits for reproducibility.

---
## 8. Bridging to LangChain / LangGraph (Future)
To integrate non‑ADK agents later without refactoring core flows:
1. Adapter Layer: Implement a thin wrapper that exposes a LangGraph “node” as an ADK tool (input schema → node invocation → output parts).
2. Event Normalization: Map LangGraph state transitions to ADK Session events for unified telemetry.
3. Capability Registry: Extend agent inventory to include origin (`adk` | `langgraph` | `langchain`) enabling dynamic routing selection.
4. Safety Reuse: Invoke LLM Auditor & Safety Plugins regardless of backend by enforcing adapter to funnel outputs into standardized content structure.

---
## 9. Agents Explicitly Not Recommended Early
| Agent | Reason |
|-------|-------|
| Payment / Domain-Specific (antom-payment, medical-pre-authorization, auto-insurance-agent) | Heavy domain prerequisites + regulatory surface; increases early complexity |
| Marketing / Travel | Non-core to current financial/regulatory analytics focus |
| Short Movie Agents | Media pipeline overhead not aligned with near-term goals |
| Personalized Shopping | E‑commerce personalization not immediate priority |

---
## 10. Risk & Mitigation Snapshot
| Risk | Mitigation |
|------|------------|
| Capability Overload Early | Phased adoption; freeze after Phase 2 for stabilization |
| Security Drift (tools) | Centralized tool permission matrix + plugin enforcement |
| Cost Escalation (search / embeddings) | Pre-flight budgeting layer + caching for high-frequency queries |
| Evaluation Fragmentation | Unified evaluator harness with per-agent config JSON |
| Session Poisoning | Deploy safety plugins before public exposure |

---
## 11. Next Concrete Actions
1. Create `docs/agents_inventory.md` (list current Orkhon + planned imported agents, roles, maturity). 
2. Start extraction of Data Science agent core (root agent + dataset config) into Orkhon sandbox. 
3. Wrap LLM Auditor as post-processing step inside Orkhon Runner pipeline. 
4. Draft safety plugin integration hooks (user_message, tool_input, tool_output, model_output). 
5. Implement evaluation harness skeleton referencing auditor + retrieval agent.

---
## 12. Summary
The shortlisted agents (Data Science, MLE-STAR, LLM Auditor, RAG, Software Bug Assistant, Safety Plugins, Gemini Fullstack) collectively cover: analytics, iterative ML improvement, factual verification, retrieval grounding, operational support, safety, and structured research workflows. This set forms a versatile nucleus adaptable to Orkhon’s financial/compliance posture and future expansion toward LangGraph/LangChain ecosystems.

---
*Document generated as part of initial multi-agent foundation planning.*
