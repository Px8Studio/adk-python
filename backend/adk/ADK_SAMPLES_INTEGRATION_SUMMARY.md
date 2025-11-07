# ADK Samples Integration: Executive Summary

## Decision: Git Subtree ✅

**Recommended approach to integrate official ADK samples into Orkhon.**

---

## Why Git Subtree?

```
                Git Subtree         Git Submodule      Manual Copy
                (✅ RECOMMENDED)     (❌ Avoid)         (❌ Avoid)
                
Deployment      Self-contained      Extra steps        Self-contained
Sync            git subtree pull    Complex commands   Manual re-copy
Customization   ✅ Full control     ⚠️ Limited         ✅ Full control
Team onboard    ✅ Simple           ❌ Confusing       ✅ Simple
History         ✅ Tracked          ⚠️ Hidden          ❌ Lost
```

**Winner: Git Subtree** - Best balance of all factors.

---

## Integration Flow

```
┌──────────────────────────────────────────────────────────────┐
│                   Official ADK Samples                        │
│           https://github.com/google/adk-samples              │
│                                                               │
│  ├── data-science/          (Multi-agent: BQ, BQML, NL2SQL)  │
│  ├── financial-advisor/     (Portfolio analysis, risk)       │
│  ├── customer-service/      (Multi-turn conversations)       │
│  ├── RAG/                   (Document Q&A, vector search)    │
│  └── ... 20+ more samples                                    │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ git subtree add
                              │ (one-time import)
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Orkhon Project                             │
│              backend/adk/agents/                              │
│                                                               │
│  ├── root_agent/            (L1: System orchestrator)        │
│  ├── api_coordinators/      (L2: DNB coordinator)            │
│  ├── api_agents/            (L3: DNB API specialists)        │
│  │                                                            │
│  ├── data_science/          ← Imported via git subtree       │
│  │   ├── agent.py           (Upstream code)                  │
│  │   ├── data_science/      (Upstream sub-agents)            │
│  │   ├── .env               (Local config - gitignored)      │
│  │   └── orkhon_dnb_config.json  (Local customization)      │
│  │                                                            │
│  └── financial_advisor/     ← Can adopt more as needed       │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ git subtree pull
                              │ (monthly sync)
                              ▼
                    [Upstream improvements flow in]
```

---

## Adoption Workflow

```
Step 1: ADOPT                    Step 2: ADAPT                    Step 3: SYNC
─────────────────               ──────────────────               ─────────────

git subtree add          ──→    Configure .env           ──→     git subtree pull
                                Create orkhon_*.json              (monthly)
Import entire sample            Add custom tools
                                Integrate with root_agent        [Upstream updates]
[One-time: 5 min]               [Project-specific: 2-3 weeks]   [Ongoing: 10 min/month]
```

---

## File Organization Pattern

```
agents/data_science/
│
├── 📄 agent.py                      [UPSTREAM - Don't modify]
├── 📄 README.md                     [UPSTREAM - Don't modify]
├── 📄 pyproject.toml                [UPSTREAM - Don't modify]
├── 📄 .env.example                  [UPSTREAM - Don't modify]
│
├── 📁 data_science/                 [UPSTREAM - Don't modify]
│   ├── agents/                      (BigQuery, BQML, Analytics sub-agents)
│   └── utils/                       (Shared utilities)
│
├── 📁 tests/                        [UPSTREAM - Don't modify]
├── 📁 eval/                         [UPSTREAM - Don't modify]
├── 📁 deployment/                   [UPSTREAM - Don't modify]
│
├── 📄 .env                          [LOCAL - Your config, gitignored]
├── 📄 orkhon_dnb_config.json        [LOCAL - Dataset config]
├── 📄 orkhon_tools.py               [LOCAL - Custom tools (optional)]
└── 📁 orkhon_sub_agents/            [LOCAL - Custom sub-agents (optional)]
```

**Rule:** Prefix all Orkhon customizations with `orkhon_*`

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        root_agent (L1)                          │
│                   System-level orchestration                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
┌─────────▼──────────┐ ┌────▼──────────┐ ┌────▼──────────────┐
│  dnb_coordinator   │ │ data_science   │ │ financial_advisor │
│       (L2)         │ │    (L2)        │ │      (L2)         │
│  Orkhon custom     │ │ ADK sample     │ │  ADK sample       │
└─────────┬──────────┘ └────┬───────────┘ └────┬──────────────┘
          │                 │                   │
    ┌─────┼─────┐    ┌──────┼──────┐    ┌──────┼──────┐
    │     │     │    │      │      │    │      │      │
┌───▼─┐ ┌─▼──┐ │  ┌─▼──┐ ┌─▼───┐ │  ┌─▼───┐ ┌─▼──┐ │
│Echo │ │Stat│ │  │BQ  │ │BQML │ │  │Port-│ │Risk│ │
│Agent│ │ics │ │  │    │ │     │ │  │folio│ │    │ │
│(L3) │ │(L3)│ │  │(L3)│ │(L3) │ │  │(L3) │ │(L3)│ │
└─────┘ └────┘ │  └────┘ └─────┘ │  └─────┘ └────┘ │
          └────▼────┐       └─────▼────┐       └────▼────┐
         ┌──────────┐      ┌───────────┐      ┌──────────┐
         │Public Reg│      │Analytics  │      │Compliance│
         │(L3)      │      │(L3)       │      │(L3)      │
         └──────────┘      └───────────┘      └──────────┘

Legend:
- L1: Root orchestrator
- L2: Domain coordinators (mix of Orkhon custom + adopted samples)
- L3: Specialist leaf agents
```

---

## Value Proposition

### Time Savings Per Sample

| Sample | Build from Scratch | Adopt + Customize | Time Saved |
|--------|--------------------|-------------------|------------|
| data-science | 6-8 weeks | 2-3 weeks | **4-6 weeks** |
| financial-advisor | 4-6 weeks | 2 weeks | **3-4 weeks** |
| customer-service | 3-4 weeks | 1 week | **2-3 weeks** |
| RAG | 3-4 weeks | 1-2 weeks | **2-3 weeks** |

**Total potential savings: 11-16 weeks** (for 4 samples)

---

## Maintenance Cost

```
Monthly Sync Workflow (10 minutes/month):
1. Run: .\backend\scripts\sync-adk-samples.ps1
2. Review changes: git diff
3. Resolve conflicts (if any)
4. Test: adk run agents/data_science
5. Commit: git commit -m "sync: Update ADK samples from upstream"
```

**ROI:** 10 min/month maintenance for 4-16 weeks saved per sample.

---

## Recommended Adoption Order

```
Priority 1 (Adopt Now):
✅ data-science         ──→  Immediate value for DNB data analysis
                             (NL2SQL, BQML, visualization)

Priority 2 (Adopt Soon):
⭐ financial-advisor    ──→  Domain expertise for financial analysis
⭐ customer-service     ──→  Conversation patterns, escalation logic

Priority 3 (Evaluate Later):
○ RAG                   ──→  When document Q&A becomes priority
○ llm-auditor           ──→  When evaluation/red-teaming needed
```

---

## Risk Mitigation

### Risk: Upstream Breaking Changes

**Mitigation:**
- Use git subtree `--squash` (flattens history, easier to review)
- Always test after sync before integrating
- Keep Orkhon customizations in separate `orkhon_*` files
- Can rollback via git if needed

### Risk: Merge Conflicts

**Mitigation:**
- Minimize modifications to upstream files
- Prefer configuration over code changes
- Document which files were modified and why
- When conflicts occur, prefer upstream for core logic

### Risk: Dependency Conflicts

**Mitigation:**
- Use unified `pyproject.toml` at `backend/adk/` root
- Let `uv` resolve version constraints
- Test after dependency updates
- Can pin versions if needed

---

## Success Metrics

After adopting a sample, measure:

1. **Adoption Time:** Import → Configure → Test → Integrate
   - Target: 1-3 weeks (vs 4-8 weeks to build)

2. **Sync Time:** Monthly upstream sync
   - Target: <30 minutes

3. **Customization Success:** Orkhon features work without breaking upstream
   - Measure: All tests pass after sync

4. **Production Readiness:** Agent deployed and serving users
   - Measure: Uptime, query success rate

---

## Decision Summary

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Integration Method** | Git Subtree | Best balance: sync + deploy + customize |
| **Customization** | Separate `orkhon_*` files | Preserves upstream sync path |
| **Dependencies** | Unified `pyproject.toml` | Simplifies management |
| **Sync Frequency** | Monthly (first Monday) | Balances freshness vs stability |
| **First Sample** | data-science | Highest ROI for Orkhon use case |

---

## Next Steps

1. **Review full guides:**
   - `ADK_SAMPLES_INTEGRATION.md` (comprehensive)
   - `ADK_SAMPLES_QUICK_REFERENCE.md` (cheat sheet)
   - `QUICK_START_ADK_SAMPLES.md` (5-min quickstart)

2. **Adopt first sample:**
   ```powershell
   .\backend\scripts\adopt-adk-sample.ps1 -SampleName "data-science"
   ```

3. **Configure for Orkhon:**
   - Set up `.env` with GCP project, BigQuery datasets
   - Create `orkhon_dnb_config.json` for DNB datasets
   - Test with DNB-specific queries

4. **Integrate with root_agent:**
   - Import data-science agent in `root_agent/agent.py`
   - Test cross-domain queries
   - Deploy to production

5. **Schedule monthly sync:**
   - First Monday of each month
   - Run `sync-adk-samples.ps1`
   - Test and commit

---

**Questions? Issues?** See full guides or file a GitHub issue.

**Ready to start?** Run: `.\backend\scripts\adopt-adk-sample.ps1 -SampleName "data-science"`
