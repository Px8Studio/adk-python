# ADK Samples Integration: Complete Guide Index

**Quick navigation to all ADK samples integration documentation.**

---

## 🚀 Getting Started

1. **Start here:** [QUICK_START_ADK_SAMPLES.md](QUICK_START_ADK_SAMPLES.md)
   - 5-minute quick start guide
   - Step-by-step adoption of `data-science` agent
   - Copy-paste commands to get running fast

2. **Quick reference:** [ADK_SAMPLES_QUICK_REFERENCE.md](ADK_SAMPLES_QUICK_REFERENCE.md)
   - Cheat sheet for common commands
   - File naming conventions
   - Troubleshooting guide

---

## 📚 In-Depth Guides

3. **Complete integration guide:** [ADK_SAMPLES_INTEGRATION.md](ADK_SAMPLES_INTEGRATION.md)
   - Comprehensive step-by-step instructions
   - Customization patterns
   - Multiple sample adoption strategies
   - Testing and deployment

4. **Strategic overview:** [ADOPTION_STRATEGY.md](ADOPTION_STRATEGY.md)
   - Why git subtree over alternatives
   - Decision matrix: Adopt vs Build
   - Directory structure conventions
   - Dependency management approach

5. **Executive summary:** [ADK_SAMPLES_INTEGRATION_SUMMARY.md](ADK_SAMPLES_INTEGRATION_SUMMARY.md)
   - Visual flow diagrams
   - Value proposition and ROI
   - Risk mitigation strategies
   - Success metrics

---

## 🛠️ Scripts

Located in `backend/scripts/`:

- **`adopt-adk-sample.ps1`** - Import a sample via git subtree
- **`sync-adk-samples.ps1`** - Pull upstream updates for all adopted samples

---

## 📖 Document Purpose Summary

| Document | Purpose | Audience | Read Time |
|----------|---------|----------|-----------|
| [QUICK_START_ADK_SAMPLES.md](QUICK_START_ADK_SAMPLES.md) | Get running ASAP | Developers | 5 min |
| [ADK_SAMPLES_QUICK_REFERENCE.md](ADK_SAMPLES_QUICK_REFERENCE.md) | Command cheat sheet | Daily users | 2 min |
| [ADK_SAMPLES_INTEGRATION.md](ADK_SAMPLES_INTEGRATION.md) | Complete how-to guide | Implementers | 20 min |
| [ADOPTION_STRATEGY.md](ADOPTION_STRATEGY.md) | Strategic decisions & rationale | Tech leads | 30 min |
| [ADK_SAMPLES_INTEGRATION_SUMMARY.md](ADK_SAMPLES_INTEGRATION_SUMMARY.md) | Executive overview | Management | 10 min |

---

## 🎯 Choose Your Path

### Path A: "Just get it working!" 
→ [QUICK_START_ADK_SAMPLES.md](QUICK_START_ADK_SAMPLES.md)

### Path B: "Show me the commands"
→ [ADK_SAMPLES_QUICK_REFERENCE.md](ADK_SAMPLES_QUICK_REFERENCE.md)

### Path C: "I need complete instructions"
→ [ADK_SAMPLES_INTEGRATION.md](ADK_SAMPLES_INTEGRATION.md)

### Path D: "Why did we choose this approach?"
→ [ADOPTION_STRATEGY.md](ADOPTION_STRATEGY.md)

### Path E: "Give me the executive summary"
→ [ADK_SAMPLES_INTEGRATION_SUMMARY.md](ADK_SAMPLES_INTEGRATION_SUMMARY.md)

---

## 🔑 Key Concepts

### Git Subtree Strategy

```bash
# One-time setup
git remote add adk-samples https://github.com/google/adk-samples.git
git fetch adk-samples

# Import a sample
git subtree add --prefix=backend/adk/agents/{SAMPLE} \
    adk-samples main:python/agents/{SAMPLE} --squash

# Pull updates (monthly)
git subtree pull --prefix=backend/adk/agents/{SAMPLE} \
    adk-samples main:python/agents/{SAMPLE} --squash
```

### Customization Pattern

```
✅ Customize via:
   - .env files (local config)
   - orkhon_*.json (dataset configs)
   - orkhon_*.py (custom tools/sub-agents)

❌ Don't modify:
   - agent.py (breaks upstream sync)
   - Core sub-agent files (breaks upstream sync)
   - Upstream utils/ directory (breaks upstream sync)
```

### Integration Pattern

```python
# In root_agent/agent.py
from ..data_science.agent import get_root_agent as get_data_science_agent

data_science_agent = get_data_science_agent()

root_agent = Agent(
    name="root_agent",
    sub_agents=[
        dnb_coordinator,
        data_science_agent,  # ← Adopted sample integrated
    ]
)
```

---

## 📋 Adoption Checklist

Use this checklist when adopting any sample:

- [ ] Read [QUICK_START_ADK_SAMPLES.md](QUICK_START_ADK_SAMPLES.md)
- [ ] Run `adopt-adk-sample.ps1 -SampleName "{name}"`
- [ ] Configure `.env` with Orkhon-specific values
- [ ] Create `orkhon_*.json` configs (if needed)
- [ ] Install dependencies: `uv sync`
- [ ] Test in isolation: `adk run agents/{name}`
- [ ] Integrate with root_agent
- [ ] Test integration: `adk run agents/root_agent`
- [ ] Create integration tests in `tests/integration/`
- [ ] Update this README with new sample details
- [ ] Commit and push changes
- [ ] Schedule monthly sync (first Monday)

---

## 🔄 Monthly Maintenance

**First Monday of each month:**

```powershell
# 1. Check for upstream updates
cd C:\Users\rjjaf\_Projects\adk-samples
git pull origin main
git log --oneline --since="1 month ago" python/agents/

# 2. Sync all adopted samples in Orkhon
cd C:\Users\rjjaf\_Projects\orkhon
.\backend\scripts\sync-adk-samples.ps1

# 3. Test after sync
cd backend\adk
adk run agents/data_science  # Test each adopted agent
adk run agents/root_agent     # Test integration

# 4. Commit changes
git add .
git commit -m "sync: Update ADK samples from upstream (YYYY-MM-DD)"
git push origin dev
```

---

## 🌟 Recommended Samples

### Already Adopted
- ✅ **data-science** - Multi-agent system for BQ, NL2SQL, BQML, analytics

### High Priority (Adopt Next)
- ⭐ **financial-advisor** - Portfolio analysis, risk assessment, compliance
- ⭐ **customer-service** - Multi-turn conversations, escalation patterns

### Medium Priority (Evaluate Soon)
- ○ **RAG** - Document Q&A with vector search
- ○ **llm-auditor** - Agent evaluation, monitoring, red-teaming

### Lower Priority (Future)
- ○ **marketing-agency** - Content generation, SEO optimization
- ○ **blog-writer** - Automated content creation
- ○ **travel-concierge** - Complex multi-turn planning

---

## 🆘 Troubleshooting

See [ADK_SAMPLES_QUICK_REFERENCE.md](ADK_SAMPLES_QUICK_REFERENCE.md#troubleshooting) for common issues and solutions.

**Common issues:**
- "Sample not found" → Check remote and fetch
- "Conflicts during sync" → Prefer upstream for core logic
- "Dependencies conflict" → Try `uv sync --resolution=highest`
- "Agent not working" → Check `.env`, test in isolation first

---

## 🔗 External Resources

- **Official ADK Samples:** https://github.com/google/adk-samples
- **ADK Documentation:** https://google.github.io/adk-docs
- **Data Science Sample:** https://github.com/google/adk-samples/tree/main/python/agents/data-science
- **Git Subtree Guide:** https://www.atlassian.com/git/tutorials/git-subtree

---

## 🎉 Success Stories

### Data Science Agent Integration
**Status:** ✅ Complete  
**Time saved:** 4-6 weeks  
**Value:** Enabled NL2SQL queries against DNB BigQuery datasets, BQML model training, and data visualization - all via natural language.

**Example queries now supported:**
- "Query dnb_statistics for top 10 insurance companies by assets"
- "Create a trend analysis of pension fund performance over the last 5 years"
- "Train a forecasting model for insurance claim prediction"

---

## 📞 Support

**Questions or issues?**
1. Check the documentation index above
2. Review troubleshooting in [Quick Reference](ADK_SAMPLES_QUICK_REFERENCE.md)
3. File a GitHub issue with details
4. Ask in team chat with `@adk-support`

---

**Last updated:** 2025-11-07  
**Maintained by:** Orkhon Development Team  
**Related:** See `CONTRIBUTING.md` for contribution guidelines
