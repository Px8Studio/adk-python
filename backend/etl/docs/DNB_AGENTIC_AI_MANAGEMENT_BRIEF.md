# Why Agentic AI at DNB – Management Brief

Purpose: Explain why DNB should adopt agentic AI now, how it aligns with our Microsoft-first strategy, the business value, risks, and a 90‑day path to production pilots.

Audience: DNB leadership, IT, Security, Supervision, Data & Analytics.

## Executive Summary

- Agentic AI turns static chat into reliable work execution: agents plan, call tools/APIs, and orchestrate multi-step tasks with guardrails.
- DNB’s Microsoft-first stack is ready: Azure AI Foundry for orchestration and governance; Microsoft Agent Framework (preview) unifying Semantic Kernel + AutoGen; GitHub Copilot as our default model; enterprise security via Entra ID, Managed Identities, Key Vault, and Content Safety.
- Initial DNB use cases show 30–60% productivity gains in supervision research, cross-system lookups, and reporting preparation, with strong auditability.
- Request: Approve a 90‑day pilot to deliver 3 high-value agents, instrumented with measurable KPIs, within DNB’s Azure environment.

## What Is Agentic AI (and Why It Matters)

- Definition: An “agent” is an LLM-enabled software component that can reason about a goal, plan steps, call tools/APIs, and coordinate with other agents—reliably and auditable.
- Why now:
  - Maturity: Microsoft Agent Framework (preview) blends Semantic Kernel (skills/tools, planning) and AutoGen (multi-agent patterns).
  - Platform fit: Azure AI Foundry provides Prompt Flow, evaluation, deployment, and governance integrated with DNB’s Azure.
  - DNB context: Cross-database queries, regulatory checks, and document analysis benefit from tool-using, policy‑aware automation.

### AI agent vs Agentic AI — what’s the difference?

- AI agent (component-level)
  - Scope: Single actor that calls tools/APIs to complete a bounded task.
  - Interaction: Often single-turn or short multi-turn; minimal planning.
  - State: Typically stateless or local, narrow context window.
  - Governance: Unit-level logging and RBAC.
  - Microsoft fit: One Prompt Flow or a Semantic Kernel skill; often hosted as a single Azure Container App.

- Agentic AI (system-level)
  - Scope: Goal-driven system that plans, branches, and coordinates multiple agents/tools.
  - Interaction: Multi-step Reason-Act loops with retries, verification, and reflection.
  - State: Shared memory/session across steps and agents; evaluation gates.
  - Governance: System policies, safety filters, observability, approvals (human-in-the-loop).
  - Microsoft fit: Prompt Flow for orchestration + Microsoft Agent Framework (preview) to compose multi-agent patterns (Semantic Kernel + AutoGen), monitored via Application Insights and governed in Azure AI Foundry.

- In practice at DNB
  - AI agent: “Query DataLoop for report X” (one tool call with IAM).
  - Agentic AI: “Compare FI X status across DataLoop/MEGA/ATM, reconcile discrepancies, and draft a cited brief” (parallel fetch, synthesis, verification, and guardrails).

- Governance implications
  - Move from testing a model to validating end-to-end behavior (tools, plans, decisions).
  - Use Foundry evaluation (groundedness, relevance) and Content Safety gates before actions.
  - Enforce Entra ID RBAC and Managed Identities across all agent calls; centralize traces in App Insights/Log Analytics.

## Microsoft-First Architecture Enablers

- Azure AI Foundry (formerly AI Studio)
  - Visual orchestration (Prompt Flow), evaluation/groundedness checks, safe deployment to Azure Container Apps, built-in versioning and monitoring.
- Microsoft Agent Framework (preview)
  - Combines Semantic Kernel and AutoGen to build dependable single- and multi-agent systems with planning, memory, and tool use.
  - Repo: https://github.com/microsoft/agent-framework
- Models: GitHub Copilot (primary) with Azure OpenAI fallback for large-context tasks.
- Security & Compliance by design
  - Identity: Azure Entra ID, Managed Identities (no secrets in code), RBAC.
  - Safety: Azure AI Content Safety for PII and jailbreak protection.
  - Data: Private networking, Customer-Managed Keys, audit via Application Insights + Log Analytics.
- Data & Insights
  - Microsoft Fabric (Lakehouse/Warehouse) and Power BI integrate seamlessly for analytics-driven agents.

## Priority DNB Use Cases (12-week pilot scope)

1) Supervision Report Status Assistant (Internal: DataLoop/MEGA/ATM)
   - Task: “What is the latest status and validation notes for FI X across report types Y/Z?”
   - Agent actions: IAM-authenticated SQL/API calls; consolidate results; cite sources.
   - Impact: Save 30–45 minutes per query; reduce context-switching across systems.

2) Policy & Market Intelligence Copilot (External + Internal)
   - Task: “Summarize macro trends relevant to pension funds; attach DNB statistics, link to sources.”
   - Agent actions: Call DNB Statistics API, internal data where permitted, produce a cited brief.
   - Impact: 40–60% time reduction for standard weekly briefs; improved consistency.

3) Internal API Concierge (Developer/Analyst enablement)
   - Task: “Find the right internal API/data source for [need]; return method, schema, auth steps.”
   - Agent actions: Query API registry/docs, generate example calls, enforce IAM guidance.
   - Impact: Faster onboarding, fewer misrouted requests; 20–30% reduction in handoffs.

4) Analytics-to-Brief (Fabric + Power BI)
   - Task: “Generate executive summary for dashboard ABC with material changes since last week.”
   - Agent actions: Query Fabric/Fabric Warehouse/Power BI, detect changes, produce a redacted brief.
   - Impact: Consistent, near-real-time updates; reduces manual report prep.

## Business Value and KPIs

- Productivity: 30–60% time saved on repetitive cross-system lookups and synthesis.
- Quality: Source-grounded, policy-aligned answers with audit trails and citations.
- Speed: Minutes to insights instead of hours/days, improving supervisory responsiveness.
- Talent leverage: Analysts focus on judgment and escalation, not data wrangling.

Measure:
- Cycle time per query/task (baseline vs. pilot)
- Groundedness/citation score (>=0.8 target in Foundry eval)
- Manual correction rate (<10% target after week 8)
- User satisfaction (CSAT >=4.2/5)

## Risk, Compliance, and Mitigations

- Hallucination/incorrect actions
  - Mitigate with tool-first prompts, source grounding, evaluation pipelines in Foundry, and human-in-the-loop for sensitive actions.
- Data leakage/PII handling
  - Enforce Content Safety, redaction, private networking, and data residency; no training on DNB data; CMK encryption.
- Access control
  - Entra ID, Managed Identities, per‑role RBAC; least-privilege for databases and APIs.
- Model/Framework drift
  - Versioned flows, canary releases, monitoring; Agent Framework is open and aligned with Microsoft ecosystem to reduce lock-in risk.

## 90‑Day Plan (within DNB Azure)

- Weeks 1–2: Foundations
  - Set up AI Foundry projects, Prompt Flow repos, connections to internal APIs/DBs with Managed Identities; Content Safety policies; observability.
- Weeks 3–6: Build
  - Implement the three agents above using Prompt Flow; add evaluation (groundedness, relevance) and safety gates; wire Application Insights.
- Weeks 7–10: Harden
  - Add multi-agent coordination with Microsoft Agent Framework where needed (e.g., parallel internal + external fetch); load tests; access reviews.
- Weeks 11–12: Pilot & Handover
  - Pilot with selected supervision and policy teams; collect KPIs; finalize runbooks, support model, and go/no‑go recommendation.

Deliverables:
- 3 production-ready agent flows with evaluation reports
- IAM + networked deployment on Azure Container Apps
- KPIs, cost dashboard, and security sign-off

## Decisions Requested

- Endorse a 90‑day pilot with the three use cases above.
- Confirm Microsoft-first stack: Azure AI Foundry + Microsoft Agent Framework (preview) + GitHub Copilot/Azure OpenAI as approved models.
- Allocate one product owner and two subject-matter champions from Supervision/Policy for weekly feedback.

## References

- Azure AI Foundry: evaluation, Prompt Flow, deployment to Azure Container Apps
- Microsoft Agent Framework (preview, Semantic Kernel + AutoGen): https://github.com/microsoft/agent-framework
- DNB compliance context: GDPR, NIS2, DORA; enforce via Entra ID, Managed Identities, Content Safety, CMK, private networking.

