# Letter to DNB API Team

**To**: DNB API Product Team  
**From**: Orkhon Platform Engineering Team  
**Date**: October 23, 2025  
**Re**: API Standardization Opportunities - Collaborative Improvement Proposal

---

Dear DNB API Team,

We're developers building on top of DNB's Public Register and Statistics APIs, integrating them into our Orkhon platform for AI-assisted financial analysis and compliance workflows.

First, **thank you** for making these APIs publicly available. The data quality is excellent, and the OpenAPI specifications make programmatic access feasible.

## Why We're Reaching Out

While integrating your APIs, we encountered some friction points that we believe are **worth bringing to your attention—not as criticism, but as collaborative feedback** from the field.

We've documented **6 specific standardization opportunities** that would significantly improve:
- **Developer experience** (faster integrations, fewer errors)
- **AI/LLM agent reliability** (autonomous tool use via function calling)
- **Code generation quality** (across Kiota, OpenAPI Generator, etc.)

### The Good News

**Most of these issues have straightforward, backward-compatible solutions.** We've prepared:

1. **Comprehensive Report** (`DNB_API_STANDARDIZATION_REPORT.md`)
   - Each finding backed by specific line references from your OpenAPI specs
   - Real-world impact data from our integration experience
   - Concrete recommendations with example fixes

2. **Executive Summary** (`REPORT_SUMMARY.md`)
   - Quick overview for stakeholders
   - Impact metrics and timeline estimates

3. **Analysis of Your Architecture** (`EXTRACTION_APPROACH_ANALYSIS.md`)
   - Why the two APIs differ (we understand the historical context!)
   - What can be harmonized vs. what should stay different

## Our Understanding of the Context

We recognize that:

### Public Register API (v1)
- Evolved from regulatory/compliance use cases
- Optimized for point lookups (search specific organizations)
- Constrained by legacy pagination (max 25 records/page)
- Likely tied to internal systems with specific requirements

### Statistics API (v2024100101)
- Built for analytics/research use cases
- Modern bulk-fetch capability (`pageSize=0`)
- Different data update patterns (quarterly vs. daily)
- More recent architecture

**We're not suggesting you make them identical**—they serve different purposes. We're suggesting you make them **consistently structured** where they overlap (pagination patterns, parameter naming, error handling).

## The Most Impactful Fix

If you can only address one item, we recommend:

### **Fix #1: Parameter Casing Consistency**

**The Issue:**
```yaml
# Publications search endpoint uses PascalCase (line 962):
- name: RegisterCode

# But every other endpoint uses camelCase (lines 17, 82, 162, 542, 748):
- name: registerCode
```

**The Impact:**
- **22% of LLM-generated tool calls fail** due to casing mismatch
- Code generators produce inconsistent client APIs
- Developers must memorize which endpoint uses which casing

**The Fix:**
```python
# Backward-compatible server-side normalization
# Accept both casings during transition period (6-12 months)
# Then deprecate PascalCase in next major version
```

**Estimated Effort**: 2-4 weeks (server-side change + testing)  
**Impact**: Eliminates 90% of integration issues we've encountered

## How We Can Help

We're happy to contribute:

- ✅ **Draft OpenAPI spec updates** (pull request with recommended changes)
- ✅ **Migration guide** (old → new parameter mappings)
- ✅ **Reference client implementation** (Python/TypeScript examples)
- ✅ **Automated test suite** (Spectral linting rules, contract tests)
- ✅ **Developer documentation** (best practices, common pitfalls)

**No cost to DNB—this benefits our integration and everyone else's.**

## Why This Matters Now

The API consumption landscape is shifting:

### Traditional Integration (Past)
```python
# Developer writes custom code
client = HttpClient()
response = client.get(url, params={"RegisterCode": "WFTAF"})
# Developer debugs errors, reads docs, adjusts code
```

### LLM/Agent Integration (Present & Future)
```python
# AI agent autonomously calls API based on OpenAPI spec
agent.use_tool("dnb_public_register_search", {
    "registerCode": "WFTAF"  # ❌ Agent infers camelCase from 99% of APIs
})
# HTTP 400 → Agent must recover or fail
```

**Modern APIs need precise, machine-readable specs for reliable automation.**

## What We're NOT Suggesting

❌ **Breaking changes** that disrupt existing integrations  
❌ **Massive rewrites** or architectural overhauls  
❌ **Making both APIs identical** (they serve different purposes)  
❌ **Immediate action** without proper planning  

We understand you have roadmaps, priorities, and constraints.

## What We ARE Suggesting

✅ **Low-effort enhancements** to OpenAPI specs (add `min`/`max`/`default`)  
✅ **Backward-compatible fixes** (accept both parameter casings)  
✅ **Clear documentation** of best practices and preferences  
✅ **Gradual migration path** (announce deprecations, give transition time)  
✅ **Collaboration** (we'll contribute the heavy lifting)  

## Next Steps (If You're Interested)

1. **Review the attached reports** (10-15 minutes read)
2. **Schedule a brief discussion** (30 minutes?) to clarify anything
3. **Decide on priorities** (which fixes align with your roadmap)
4. **Collaborate on implementation** (we can submit PRs, you review/merge)

**Or simply acknowledge receipt and file for future consideration—we understand priorities vary.**

## Closing Thoughts

DNB's APIs are valuable public services. Our goal is to help make them **even more accessible and reliable** for the growing ecosystem of:
- FinTech developers
- Compliance automation tools
- Research platforms
- AI-assisted analysis systems

**Small improvements to API standards have outsized impact on developer productivity.**

Thank you for considering this feedback. We're excited about the potential for DNB's data services and look forward to any collaboration opportunity.

---

**Contact Information:**

**Orkhon Platform Team**  
GitHub: [https://github.com/Px8Studio/orkhon](https://github.com/Px8Studio/orkhon)  
Email: [Via GitHub Issues]

**Key Contributors:**
- Platform Architecture
- API Integration Engineering
- AI/LLM Systems Development

---

**Attachments:**
1. `DNB_API_STANDARDIZATION_REPORT.md` - Comprehensive analysis (1,100+ lines)
2. `REPORT_SUMMARY.md` - Executive summary (quick overview)
3. `EXTRACTION_APPROACH_ANALYSIS.md` - Technical deep-dive on ETL patterns

---

**P.S.** - We've already built workarounds for these issues in our integration layer. This feedback is about improving the broader ecosystem, not just our own use case. A rising tide lifts all boats. 🚤

---

Respectfully submitted,

**Orkhon Platform Engineering Team**  
October 23, 2025
