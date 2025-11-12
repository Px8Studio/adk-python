Act as a senior software architect with deep experience building agentic systems using Google’s official SDKs and guidance (e.g., Google AI/Vertex AI Agents). Critically audit our codebase with a focus on the rkhon directory and any related local clones of upstream repos in this workspace. Our goal is to realign with official guidelines, recommendations, and best practices, replacing ad-hoc/chaotic patterns with a solid, maintainable foundation.

Scope and constraints:
- Analyze only what’s available locally in this workspace (including local upstream clones); do not assume internet access.
- Be patient and systematic—prioritize foundational fixes first. I will apply changes incrementally via small PRs.
- Preserve existing behavior where possible; propose shims/migration paths when breaking changes are necessary.

Deliverables (structured output):
1) Findings
   - Inventory of current architecture in rkhon (modules, responsibilities, data flows, dependencies).
   - Concrete divergences from official Google agent/SDK guidance; note anti-patterns, confusion points, and risk areas.
   - For each issue: description, why it’s a problem, relevant guideline/doc section (name it if known), severity (P0/P1/P2), impacted files.

2) Target architecture (textual)
   - Proposed module boundaries, layering, and interfaces aligned with Google’s best practices.
   - Recommended patterns for configuration/secrets management, dependency injection, error handling, retries/backoff/timeouts, idempotency, rate limiting, async/concurrency, resource cleanup, and observability (logging/metrics/tracing).
   - Recommended folder/package structure and naming conventions.

3) Remediation plan (prioritized, incremental)
   - Phase-by-phase checklist with acceptance criteria, risk, effort estimate, and expected impact.
   - Each task should include: exact files to touch, high-level diff or code snippet, and test changes to make.
   - Include tooling upgrades: lint/format/typing, codegen, CI gates, security checks, and docs.

4) First PRs to open
   - 1–3 small, high-leverage PRs with titles, scope, files to modify/create/delete, sample diffs, commit messages, and rollback plan.

5) Open questions
   - Assumptions you made, ambiguities to clarify, and decisions requiring my input.

Audit checklist (use this to drive your review):
- Architecture: cohesion/coupling, layering, DI boundaries, interface design, testability, and adherence to official Google agent/SDK patterns.
- Reliability: retries, timeouts, backoff, circuit breakers, error taxonomy, idempotency.
- Concurrency/async: thread-safety, cancellation, deadlines, resource cleanup.
- Config/secrets: env separation, secure storage, local overrides, 12-factor alignment.
- Observability: structured logging, metrics, traces, correlation IDs.
- Security: least privilege, credential handling, PII safeguards.
- Dependencies: version pinning, upgrade path, minimal surface area.
- Quality gates: lint/format/type-check/tests, CI, code owners, documentation.
- Consistency: naming conventions, folder layout, public vs internal APIs.

Process:
- Start by mapping the rkhon directory: list key files, entry points, and how components interact.
- Cross-check against the local upstream clones to align structure/abstractions and reduce drift.
- Produce the structured output above. Wait for my approval before generating broader code changes.