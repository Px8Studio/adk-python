# ADK Samples: Quick Reference Card

## 🚀 Adopt a Sample (One Command)

```powershell
.\backend\scripts\adopt-adk-sample.ps1 -SampleName "data-science"
```

---

## 📋 5-Step Integration

```powershell
# 1. Import
.\backend\scripts\adopt-adk-sample.ps1 -SampleName "data-science"

# 2. Configure
cd backend\adk\agents\data-science
copy .env.example .env
notepad .env  # Set GCP_PROJECT_ID, BQ_DATASET_ID, etc.

# 3. Install
cd ..\..
uv sync

# 4. Test
adk run agents/data-science

# 5. Integrate
notepad agents\root_agent\agent.py  # Add to sub_agents
```

---

## 🔄 Monthly Sync (One Command)

```powershell
.\backend\scripts\sync-adk-samples.ps1
```

---

## 📁 File Naming Convention

```
✅ orkhon_dnb_config.json        # Orkhon-specific configs
✅ orkhon_tools.py                # Orkhon-specific tools
✅ orkhon_sub_agents/             # Orkhon-specific sub-agents
❌ Modify agent.py directly       # Breaks upstream sync
```

---

## 🎯 Recommended Samples

| Priority | Sample | Time Saved | Effort |
|----------|--------|-----------|--------|
| 🔥 High | data-science | 4-6 weeks | 2-3 weeks |
| 🔥 High | financial-advisor | 3-4 weeks | 2 weeks |
| 🔥 High | customer-service | 2-3 weeks | 1 week |
| ⭐ Medium | RAG | 2-3 weeks | 1-2 weeks |
| ⭐ Medium | llm-auditor | 1-2 weeks | 1 week |

---

## 🛠️ Common Commands

```powershell
# List available samples in adk-samples
git ls-tree -r adk-samples/main --name-only python/agents/

# Check what's been adopted
ls backend\adk\agents\

# Test an agent
adk run agents/{name}

# Web UI (test multiple agents)
adk web agents

# Pull updates for one agent
git subtree pull --prefix=backend/adk/agents/{name} adk-samples main:python/agents/{name} --squash
```

---

## 🐛 Troubleshooting

```powershell
# Remote not found
git remote add adk-samples https://github.com/google/adk-samples.git
git fetch adk-samples

# Dependency conflicts
cd backend\adk
uv sync --resolution=highest

# Agent not working
adk run agents/{name} --verbose
cat agents\{name}\.env
```

---

## 📚 Full Documentation

- **Integration Guide:** `ADK_SAMPLES_INTEGRATION.md`
- **Adoption Strategy:** `ADOPTION_STRATEGY.md`
- **5-Min Quick Start:** `QUICK_START_ADK_SAMPLES.md`

---

## 🎯 Key Principle

> **Adopt → Adapt → Sync**
> 
> 1. Adopt official samples via git subtree
> 2. Adapt with `orkhon_*` customizations
> 3. Sync monthly with upstream improvements

---

## ⚡ Power User Tips

```powershell
# Adopt + Configure + Test (all at once)
.\backend\scripts\adopt-adk-sample.ps1 -SampleName "financial-advisor"
cd backend\adk\agents\financial-advisor
copy .env.example .env
code .env  # Quick edit in VS Code
cd ..\..
uv sync
adk web agents  # Launch web UI to test

# Check for upstream changes before syncing
cd C:\Users\rjjaf\_Projects\adk-samples
git pull origin main
git log --oneline --since="1 month ago" python/agents/data-science

# Dry run sync (see what would change)
.\backend\scripts\sync-adk-samples.ps1 -DryRun
```

---

**Need help?** Check the full guides in `backend/adk/` or the official [ADK Samples](https://github.com/google/adk-samples).
