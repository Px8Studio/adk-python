# DNB API Standardization Report

Date: 2025-10-19
Author: Orkhon (ADK-based) Integration

## Purpose

This report documents several standardization opportunities across DNB’s Public Register and Statistics APIs that directly impact agentic integrations and LLM-based tool-calling. The goal is to:

- Improve developer and tool interoperability by reducing ambiguities.
- Prevent avoidable HTTP 400s that arise from parameter name inconsistencies and format ambiguity.
- Enable reliable code generation and schema-aligned assistants across SDKs, MCP/Toolbox servers, and LLM agents.

## Summary of Findings

1) Parameter name casing inconsistencies (Public Register API)
- Observation: Query parameter names sometimes use different casing than similarly named path parameters.
- Example (from Public Register, publications_search):
  - Path: `/api/publicregister/{languageCode}/Publications/search`
  - Query params include `RegisterCode` (capital R), while other endpoints use `registerCode` (lowercase r) in path params.
- Concrete references:
  - File: `backend/apis/dnb/specs/openapi3_publicdatav1.yaml`
  - Endpoint: `/api/publicregister/{languageCode}/Publications/search` → parameter `RegisterCode`
  - Endpoint: `/api/publicregister/{languageCode}/Publications/{registerCode}` → parameter `registerCode`
- Impact: LLMs often normalize to lowerCamel (e.g., `registerCode`) when emitting function-call arguments. If the receiving service expects `RegisterCode`, the parameter is omitted/misnamed, leading to HTTP 400.

2) Mixed array vs string encoding for list-like parameters
- Observation: Some parameters represent lists (e.g., `relationNumbers`) but the on-wire expectations (comma-separated vs repeated keys) aren’t explicitly documented.
- Example:
  - Endpoint: `/api/publicregister/{languageCode}/{registerCode}/Organizations` has `relationNumbers` declared as an array of string in OpenAPI.
  - Client libraries and generators vary in how they encode arrays in query strings without explicit `style`/`explode` directives.
- Impact: Interoperability issues across tooling; servers may receive unexpected encodings and respond 400.

3) Date/time format guidance is embedded in description strings
- Observation: The accepted date format (e.g., `YYYY-MM-dd`) appears in descriptions but not as a machine-enforced format.
- Example:
  - Historical endpoints include examples like `YYYY-MM-dd (2024-01-30)`.
- Impact: Tooling and LLMs may produce ISO 8601 variants or ambiguous values unless constraints are explicitly modeled (format, pattern) or examples are consistent.

4) Pagination defaults and constraints not consistently modeled
- Observation: `page` and `pageSize` semantics appear in descriptions; limits (e.g., max 25) are mentioned in text, not in schema (minimum/maximum).
- Impact: Agents and SDKs can overstep limits unintentionally; servers respond 400.

5) Security header vs query key duality
- Observation: Two security schemes are defined (`apiKeyHeader` and `apiKeyQuery`). The preferred one should be emphasized, and error modes documented when the wrong one is used.
- Impact: Inconsistent client behavior; easier to standardize on header and deprecate query where possible.

## Why this matters for LLM/agent integrations

LLMs don’t “know” vendor-specific naming quirks unless provided precise, consistent schemas and examples. When parameter names and formats vary:
- Function-call arguments may use normalized casing (lowerCamel) instead of the exact on-wire names (e.g., `RegisterCode`).
- Missing or mis-cased params result in HTTP 400s. This is exactly what we observed during ADK runs against the Public Register tools.
- Even with instructions, enforcing correctness is brittle without consistent schemas and machine-readable constraints. Small variances can lead to failed calls and degraded user experience.

## Recommendations

1) Normalize parameter naming across endpoints
- Adopt a single casing convention for parameter names (recommended: lowerCamel for query/path params).
- Specifically: change `RegisterCode` → `registerCode` in publications_search to align with other endpoints.
- Provide a deprecation path: accept both names for a period, then remove the old form.

2) Specify query array encoding explicitly
- Use OpenAPI style/explode on array params, e.g.:
  - `style: form`, `explode: true` for `?relationNumbers=a&relationNumbers=b`
  - or `explode: false` for `?relationNumbers=a,b`
- Update server to accept both during transition; document the canonical form.

3) Make date formats machine-readable
- Use `format: date` or add `pattern` for `YYYY-MM-dd` where applicable.
- Add `examples` consistently and include a negative example in the description.

4) Model pagination constraints in schema
- Add `minimum: 1` for `page`, and `minimum`/`maximum` for `pageSize` (e.g., `maximum: 25`).
- Document default values via `default:` fields.

5) Clarify security scheme usage
- Recommend and document `apiKeyHeader` as the primary method.
- Ensure error responses include guidance when `subscription-key` query is used incorrectly.

6) Versioning and migration plan
- Introduce a minor API version (e.g., `/v1.1`) with standardized parameter names and constraints.
- Provide a migration guide mapping old → new parameter names and encoding rules.

## Evidence and examples

- Parameter casing inconsistency:
  - publications_search: `RegisterCode` (query)
  - publications/latest: `registerCode` (path)
  - organizations endpoints: `registerCode` (path)

- Array param encoding ambiguity:
  - `relationNumbers` declared as array without explicit `style`/`explode`.

- Date format guidance only in descriptions:
  - Historical endpoints include textual examples but no `format: date` or regex `pattern`.

- Pagination constraints not in schema:
  - `pageSize` max 25 described in text; not modeled as `maximum: 25`.

Files referenced:
- Public Register: `backend/apis/dnb/specs/openapi3_publicdatav1.yaml`
- Statistics: `backend/apis/dnb/specs/openapi3_statisticsdatav2024100101.yaml`
- Echo: `backend/apis/dnb/specs/openapi3-echo-api.yaml`

## Proposed developer experience improvements

- Provide canonical client examples for each endpoint, including:
  - Exact parameter names and casing.
  - Query array encoding format.
  - Date formats with valid/invalid samples.
- Publish a Postman collection and an OpenAPI PR that incorporates the recommendations above.
- Add a conformance test suite to validate server behavior against the standardized spec (array/style, casing aliases, pagination bounds).

## Appendix: Impact on our stack (Orkhon/ADK/Toolbox)

- Our OpenAPI → Toolbox generator preserves parameter names exactly. Inconsistent casing leads to mismatches during LLM tool calls.
- We’ve mitigated by updating agent instructions to stress case-sensitive names and by offering optional pre-validation/remapping.
- A standardized API definition would remove the need for fragile, per-endpoint exceptions and improve success rates for autonomous tool use.

---

We’re happy to contribute a PR against the OpenAPI specs to demonstrate these changes, with backward-compatible guidance and examples.
