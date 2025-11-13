# Solven – DNB’s Agentic AI Assistant

A two-part brief for non-technical and technical readers.

- Part 1 – Meet Solven (plain-language)
- Part 2 – Technical Appendix (deep-dive, architecture, governance)

## Part 1 – Meet Solven

### Why Solven Exists
Solven is our digital colleague that answers supervision questions by talking to the same governed data sources we use. Think of it as a concierge who knows the DNB house rules and can fetch the right dossier in seconds.

- Live URL: https://solven-ai.web.app
- Goal: Faster, cited answers; less time chasing data; more time for judgment.

### How Solven Helps Us
- Colleagues will ask Solven in plain language. Example: “What’s the latest reported solvency ratio for FI X, and how does it compare quarter-over-quarter?”
- Solven looks into:
  - DNB public datasets and registers
  - Internal sources such as Synapse/Fabric lakehouse and Azure parquet archives
  - Approved APIs exposed with managed identity
- The team receives a cited answer with links to sources and a short reasoning trail.

What stays the same
- Experts remain in control. Solven proposes; reviewers approve.
- Sensitive actions follow our established approval flows.
- Data access respects existing RBAC and least‑privilege rules.

### The Team Behind Solven: Three Specialist Sub‑Agents
- Validation Specialist
  - Plain-English: Our spell‑checker for insurance and pension data quality.
  - Focus: DataLoop/MEGA/ATM validations, common quality rules, missing/late filings.
- Taxonomy Guide
  - Plain-English: Tracks taxonomy evolutions and explains how a data point changed over time.
  - Focus: Insurance/pension data point models, historical versions, mapping suggestions during change.
- Data Navigator
  - Plain-English: Knows where each dataset lives—Synapse, Fabric, parquet—and fetches the freshest numbers.
  - Focus: Source selection, freshness checks, and row‑level filters based on assigned access.

Analogy
- Imagine an orchestra: Solven is the conductor. It cues the right section (Validation, Taxonomy, Data Navigation), keeps tempo (policies and approvals), and produces a reliable performance (cited answers).

### FAQ
- What data will Solven access?
  - Only what assigned roles allow. Entra ID and managed identities enforce least privilege.
- How will we validate answers?
  - Check citations; ask Solven to show the validation checks it applied.
- What about sensitive information?
  - Safety filters, redaction, and governance gates are applied before tool/database actions.
- How do we report issues?
  - Open a ticket in the team channel or contact the product owner/security liaison listed below.

### Engagement and Support
- Access will be provided during pilot via the standard app catalog entry (Solven – DNB).
- Requirements: Entra ID account, RBAC aligned to governed sources.
- Support: Product Owner, Solution Architect, Security/Privacy contact.
- See Appendix C for the deployment and rollout plan in Azure AI Foundry.

---

## Part 2 – Technical Appendix

### Appendix A – Vision Overview
<!-- Previous full document content begins here, now nested under Appendix A.
     Keep the text unchanged except for heading levels as needed. -->

# Why Agentic AI at DNB – Management Brief

Purpose: Recommend adoption of agentic AI aligned with Microsoft-first strategy; outline value, risks, and fit for DNB, with an initial focus on Insurance and Pension funds.

Audience: DNB leadership, IT, Security, Supervision, Data & Analytics.

## Executive Summary

- Agentic AI reduces cycle time and handoffs for supervisory and data tasks with full auditability.
- An initial high-value use case is a Database Agent that lets non‑technical users query governed data in natural language; this can expand into a multi‑agent system as needs mature.
- Works in familiar channels (Teams/Copilot) with enterprise identity, safety, and governance.
- Expected outcomes: faster answers, higher-quality, cited outputs, and better analyst leverage.

## What Is Agentic AI and Why It Matters

- Definition: An agent is a governed software component using large language
  model (LLM) reasoning to plan, invoke tools/APIs, and coordinate tasks.
- Maturity: Microsoft Agent Framework integrates planning (Semantic Kernel) and multi‑agent patterns (AutoGen).
- Fit: Supervisory workflows (cross-database reconciliation, regulatory change impact, document analysis) require tool use plus policy controls.
- Platform: Azure AI Foundry supplies orchestration, evaluation, deployment, identity integration.

### Component-Level vs System-Level

- AI agent (single actor): Bounded task, minimal planning, local state.
- Agentic AI (system): Goal-driven orchestration, branching, retries, verification, shared session state, centralized policies.
- Example difference:
  - Single agent: “Query DataLoop for report X.”
  - System: “Compare FI X status across DataLoop/MEGA/ATM, reconcile differences, draft cited brief.”

### Governance Shift

- Moves from model-centric testing to full path validation (intent → plan →
  tool executions → output).
- Foundry evaluation (groundedness, relevance) plus Content Safety gating
  precede sensitive actions.
- Identity: Azure Entra ID + Managed Identities across all calls; unified
  telemetry in Application Insights (App Insights) and Azure Log Analytics.

## Microsoft-First Architecture Enablers

- Secure-by-default identity and access (single sign-on, role-based access).
- Safety and governance controls (content safety, logging, approvals).
- Integration with productivity tools (Teams/Copilot) for fast adoption.
- Reuse existing, governed data sources and dashboards (no new platforms required at pilot).

## Why Azure AI Foundry and not Copilot Studio?

- TL;DR: Use Copilot Studio for lightweight, M365-first experiences and citizen-development. Use Azure AI Foundry for governed, multi-agent, tool-heavy backends that require private networking, managed identity, evaluation gates, and CI/CD.

Key differences
- Scope and target:
  - Copilot Studio: Rapid M365-centric copilots, plugins, actions, and connectors inside the Microsoft 365 runtime.
  - AI Foundry: Engineering platform for agentic backends (Prompt Flow/Semantic Kernel), any channel (incl. Teams), any model/provider, custom tools/APIs.
- Identity, networking, and data perimeter:
  - Copilot Studio: Strong for user-delegated access to M365 and Power Platform connectors.
  - AI Foundry: End-to-end Entra ID with Managed Identities, Key Vault, private networking/VNet, private endpoints across LLM, APIs, and databases.
- Orchestration and multi-agent:
  - Copilot Studio: Prompts, plugins, and actions; limited branching/planning for complex tool use.
  - AI Foundry: First-class orchestration (Prompt Flow, SK), retries/branching, multi-agent patterns, evaluation gates before sensitive actions.
- Tools and internal APIs:
  - Copilot Studio: Connector-first; custom connectors via Power Platform/Dataverse.
  - AI Foundry: Direct SDK/OpenAPI/MCP tools, database access with MI, standardized tool schemas, reuse across agents/services.
- Evaluation, safety, and observability:
  - Copilot Studio: Responsible AI features for M365 experiences.
  - AI Foundry: Offline/online evaluations (groundedness/relevance), policy gates, lineage and tracing (App Insights/Log Analytics), A/B, canary, rollbacks.
- DevOps and portability:
  - Copilot Studio: ALM via Power Platform solutions.
  - AI Foundry: Projects/Hubs, infra-as-code (Bicep/Terraform), versioned flows, multi-environment CI/CD, model/provider portability.
- Cost and scaling:
  - Copilot Studio: Fast time-to-value for M365 scenarios; simpler cost model.
  - AI Foundry: More control for data/compute-heavy backends, explicit cost attribution, scale-out patterns.

When to use which
- Choose Copilot Studio when:
  - The experience is primarily in M365 (Teams/Outlook/SharePoint) with user-delegated access and simple actions.
  - Citizen developers maintain the solution and connector breadth is sufficient.
- Choose AI Foundry when:
  - Workflows invoke internal APIs/databases under Managed Identity with private networking and audit needs.
  - You need multi-agent orchestration, evaluation gates, rollouts, and platform-level observability/traceability.
  - Model/provider portability or non-M365 channels are in scope.

Coexistence pattern (recommended)
- Frontend: Copilot/Teams (Copilot Studio for UX where helpful).
- Backend: Agentic services in AI Foundry (Prompt Flow/SK) with tools, evaluations, and governance.
- Integration: Expose backend APIs to Copilot via secure plugins/actions; keep Teams UX while centralizing orchestration, identity, and audit in Foundry.

## Agent Catalog (Initial Focus: Insurance & Pension)

- Root Orchestrator: Entry, routing, policy enforcement.
- Coordinators: Internal Services; External Regulatory; Data & Analytics.
- Database Agent (New): Conversational access to governed datasets for non‑technical users; turns natural language into safe, approved queries and returns cited answers.
- Specialists: DataLoop, MEGA, ATM; Taxonomy (EIOPA RAG); Statistics; Public Registers; Analytics‑to‑Brief; Document Ingestion; API Concierge; Entity Resolution; Case Triage; Compliance Guard.
- Validation Specialist: Explains validation logic; assists natural‑language authoring and review of new rules with change control (positioned for later phase).
- Guardrails: Identity, safety filters, evaluation gates, centralized tracing.

## Representative Use Cases

1) Supervision Report Status Assistant – Consolidate status + validation notes with sources.  
2) Taxonomy Agent – Detect taxonomy deltas, propose mapping changes.  
3) Policy & Market Intelligence – Macro trends + cited data.  
4) Internal API Concierge – Locate authoritative endpoints and auth method.  
5) Analytics‑to‑Brief – Summarize material dashboard shifts.  
6) Entity Resolution – Canonical ID with confidence + lineage.  
7) Case Triage – Classify, enrich, and route with audit metadata.  
8) Database Q&A (New) – Ask questions in natural language and get cited answers from governed datasets without writing SQL.  
9) Validation Authoring & Coverage (Later) – NL→Validation authoring, proposal and review with change control.

All responses are source‑grounded; human‑in‑the‑loop (HITL) for sensitive outputs.

## Business Value and Key Performance Indicators (KPIs)

- Productivity: 30–60% cycle time reduction on targeted tasks.
- Quality: Cited, policy‑aligned outputs.
- Adoption: Weekly active users and repeat usage in Teams/Copilot.
- Satisfaction: CSAT ≥4.2/5.

KPIs:
- Time‑to‑answer vs baseline (by use case).
- Citation/grounding rate ≥0.8 (sampled reviews).
- Manual correction rate <10% after week 8.
- Analyst hours shifted from collection to judgment.

## Risks & Mitigations

- Incorrect actions: Tool‑first prompting, verification steps, HITL for sensitive flows.
- Data leakage / PII: Safety gating, redaction, private networking, no training on DNB data.
- Access control gaps: Role‑based access, least privilege, approvals.
- Drift: Versioned flows, canary rollout, telemetry and feedback loops.

## Readiness Checklist (Pre-Build)

- Clear outcomes and decision rights (advisory vs action; HITL points).
- Authoritative data sources, freshness, and citation expectations.
- Identity scopes, residency, and retention.
- Safety classification, PII handling, audit scope and review cadence.
- Channels and change management (Teams/Copilot, ACA), cost envelope.
- Reusable patterns and governance (approvals, logging, rollout gates).

## References

- Azure AI Foundry (orchestration, evaluation, deployment).
- Microsoft Copilot (end‑user channel).
- Governance: GDPR, NIS2, DORA via identity, safety, encryption, and audit.

## Open Questions for DNB Architecture and Operations

- Organization & Collaboration
  - Central ownership: Which central team leads Agentic AI (sponsor,
    product/owner, platform)? Where does it sit organizationally?
  - Collaboration model: How do we work with supervision domains and IT
    (cadence, working agreements, Teams channel, decision forum)?
  - Roles and staffing (pilot → scale): Which roles are needed and at what
    allocation? (Product Owner, Solution Architect, Agent Engineer(s),
    Data Engineer, Tool/API owner(s), Security, Compliance/Privacy,
    Platform/DevOps, Evaluator/QA, Change & Adoption lead,
    Legal/Procurement liaison).
  - Capacity & timeline (indicative): Discovery 2–3 weeks; pilot build 6–8
    weeks; hardening/deployment 2 weeks. Typical availability per role:
    PO 0.3–0.5 FTE; Eng 2–3 FTE; Data Eng 0.5–1 FTE; Security/Compliance
    0.2 FTE each; Evaluator 0.3 FTE.
  - Artifacts: RACI, roadmap/backlog, Definition of Done/acceptance criteria,
    decision log, risk/mitigation register.
  - Ways of working: PR‑based change control, weekly demos, design reviews,
    incident/DR exercises.

- Identity & Access
  - How will agents authenticate to Azure SQL/PostgreSQL (Managed Identity vs user-delegated tokens)? Do we need per-user attribution in downstream query audit trails?
  - What RBAC roles are required per agent and per tool? How will least privilege be enforced and reviewed?
  - How will cross-tenant or guest access be handled, if needed, for inter-agency collaboration?

- Data Residency, Retention, and Privacy
  - Confirm EU region(s), customer-managed keys (CMK), and encryption posture for all services (Cosmos DB, Log Analytics, AI services).
  - What retention and deletion policies apply to chats, event logs, artifacts, and intermediate data? How will PII redaction be applied to logs?

- Networking & Connectivity
  - Which services require private endpoints/VNet integration (ACA, databases, Key Vault, OpenAI endpoints)? Any egress restrictions or proxy requirements?
  - DNS, firewall rules, and IP allowlists for internal APIs and databases.

- Secrets, Keys, and Credentials
  - Can we operate fully with Managed Identities, or are any secrets required? How will rotation and access reviews be enforced via Key Vault?

- Safety & Compliance
  - What Content Safety thresholds (PII, jailbreak, hate/abuse) should gate tool execution? Where are human-in-the-loop approvals required?
  - How do we record safety decisions without storing sensitive payloads?

- Observability & Audit
  - What App Insights/Log Analytics schema, sampling, and correlation IDs will we adopt for end-to-end tracing (user → agent → tool → DB/API)?
  - Which KQL queries and dashboards are needed for security investigations and compliance reporting?

- Models & Orchestration
  - Baseline model choice (Azure OpenAI GPT-4/Copilot) and fallbacks. What evaluation metrics (groundedness, relevance) define acceptable quality?
  - Criteria for selecting Prompt Flow vs Semantic Kernel for specific agents. How will versions and rollouts be controlled?

- Tools & Internal APIs
  - Inventory of authoritative APIs with OpenAPI specs. Are rate limits, pagination, and error contracts consistent?
  - How will tool schemas (inputs/outputs) be standardized and reused across agents?

- Databases & Data Warehouse
  - Catalog of governed datasets (DataLoop, MEGA, ATM, Synapse/Fabric). What row-level security and masking policies apply?
  - Do we need query cost controls, caching, or synthesized datasets for evaluations/smoke tests?

- Teams/Copilot Integration
  - Which channels (Teams bot, message extensions, Copilot plugins) are in scope? How will user identity and authorization be enforced per request?

- Agent-to-Agent (A2A) Interactions
  - Do we need A2A now or later? What is the agent card format, registry location, and auth model for cross-department calls?
  - How will we audit and rate-limit cross-org calls?

- Cost & Operations
  - Cost attribution tags, budgets, and alerts. Expected concurrency, autoscaling thresholds, and cold start mitigation for ACA.
  - Quota management for model and data services.

- Change Management & Governance
  - PR-based change control for prompts, tools, and flows; required reviewers; canary and rollback strategies.
  - Incident response runbooks, DR strategy (RTO/RPO), and backup/restore coverage.

- Legal & Procurement
  - Data Processing Agreements and EU data boundary requirements for model providers.
  - Licensing constraints for connectors, SDKs, and any third-party components.

### Appendix B – Multi‑Agent Orchestration Architecture
- Orchestration pattern
  - Root agent (Solven) plans and delegates to specialists via tool-first prompting and retries.
  - Multi-agent coordination follows Semantic Kernel/Prompt Flow patterns with evaluation gates.
  - Identity: End-to-end Entra ID; managed identities for databases/APIs; Key Vault for secrets.
- Sub-agent responsibilities and contracts
  - Validation Specialist
    - Inputs: dataset identifier, period, entity scope, validation profile.
    - Contract: Validation DSL (rule_id, predicate, severity, remediation_hint).
    - Outputs: issues[], coverage metrics, provenance.
  - Taxonomy Guide
    - Inputs: datapoint id/version, filing period, domain (insurance/pension).
    - Contract: Taxonomy metadata (concept, lineage, deprecation, mapping candidates).
    - Outputs: version deltas, migration hints, confidence, citations.
  - Data Navigator
    - Inputs: query intent, freshness requirements, user role.
    - Contract: Storage endpoints (Synapse, Fabric lakehouse, parquet URIs), schema hints, RLS filters.
    - Outputs: resolved source, query plan, row-count estimate, cost hints.
- Orchestration triggers
  - Trigger Validation when the answer affects regulated KPIs or when risk score > threshold.
  - Trigger Taxonomy on datapoints tied to evolving concepts or historical comparisons.
  - Trigger Data Navigator when multiple candidate sources exist or freshness is uncertain.
- Evaluation and safety
  - Groundedness/relevance checks in Prompt Flow before sensitive actions.
  - Content Safety filters on user prompts and tool outputs.
- Observability
  - Tracing via App Insights and Log Analytics with correlation IDs (user → agent → tool → DB).

References
- Azure AI Foundry (Prompt Flow, evaluation), Semantic Kernel orchestration, and multi-agent patterns aligned with Microsoft’s evolving agent frameworks.

### Appendix C – Data Source Connectivity Matrix
| Agent            | DNB Public APIs | Synapse (SQL/Spark) | Fabric Lakehouse | Azure Parquet Containers | Auth Method            | Scope         |
|------------------|-----------------|---------------------|------------------|--------------------------|------------------------|---------------|
| Solven (Root)    | Read            | Read                | Read             | Read                     | Entra ID (user), MI    | Read-only     |
| Validation Spec. | Optional Read   | Read                | Read             | Read                     | Managed Identity (MI)  | Read-only     |
| Taxonomy Guide   | Read            | Optional Read       | Optional Read    | Optional Read            | MI + Key Vault if any  | Read-only     |
| Data Navigator   | Read            | Read                | Read             | Read                     | MI + Private Endpoints | Read-only     |

Notes
- No write operations in pilot phase.
- Private networking and PE on LLM endpoints and data stores where required.
- RBAC at source level; row-level security enforced by source.

### Appendix D – Conversation Journey (Diagram)
- Diagram placeholder: images/conversation_journey.png
  - Swimlane: User → Solven → Specialist Agent(s) → Data Source(s) → Solven → User
  - Checkpoints: Safety gate, plan preview (optional), validation, citations.

### Appendix E – Agent Mesh Topology (Diagram)
- Diagram placeholder: images/agent_mesh_topology.png
  - Layers: Channels (Teams/Copilot) → Orchestration (Prompt Flow/SK) → Agents/Tools → Data Sources
  - Boundaries: Entra ID, Managed Identities, Key Vault, Private Endpoints.

### Appendix F – Bridging and Related Docs
- See Appendix B for orchestration and security details referenced in Part 1.
- Dutch-language use cases: backend/etl/docs/ECDAP_AGENTIC_AI_USE_CASE_NL.md
- Future additions: deployment runbooks, CI/CD (bicep/terraform), canary strategy.

<!-- End of Appendix. -->

