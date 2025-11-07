# 🚀 ADK Samples: 5-Minute Quick Start

> **Goal:** Adopt the `data-science` agent from official ADK samples and integrate it with Orkhon in under 5 minutes.

---

## Why Adopt Official Samples?

✅ **Save 4-6 weeks** of development time per sample  
✅ **Production-tested** code from Google  
✅ **Automatic updates** via git subtree sync  
✅ **20+ ready-to-use agents** across domains  

**Official samples:** https://github.com/google/adk-samples

---

## Adopt Your First Sample (data-science)

### 1. Run Adoption Script
```powershell
cd C:\Users\rjjaf\_Projects\orkhon
.\backend\scripts\adopt-adk-sample.ps1 -SampleName "data-science"
```

**What this does:**
- Imports the entire `data-science` agent via git subtree
- Creates a commit with clear attribution
- Sets up for easy monthly upstream sync

### 2. Configure Environment
```powershell
cd backend\adk\agents\data-science
copy .env.example .env
notepad .env
```

**Set these values:**
```bash
GCP_PROJECT_ID=orkhon-dev
GCP_LOCATION=europe-west1
BQ_DATASET_ID=dnb_statistics
```

### 3. Create DNB Config
```powershell
# Create orkhon_config.json
@"
{
  "datasets": [
    {
      "type": "bigquery",
      "dataset_id": "dnb_statistics",
      "description": "DNB Statistics: insurance, pensions, market data"
    },
    {
      "type": "bigquery",
      "dataset_id": "dnb_public_register",
      "description": "DNB Public Register: entities, publications"
    }
  ]
}
"@ | Out-File -FilePath orkhon_config.json -Encoding utf8
```

**Update .env:**
```bash
DATASET_CONFIG_FILE=./orkhon_config.json
```

### 4. Install Dependencies
```powershell
cd ..\..\  # Back to backend/adk
uv sync
```

### 5. Test It!
```powershell
adk run agents/data-science
```

**Try this query:**
```
Query the dnb_statistics dataset for the top 10 insurance companies by total assets
```

### 6. Integrate with Root Agent
```powershell
notepad agents\root_agent\agent.py
```

**Add these lines:**
```python
# At top
from ..data_science.agent import get_root_agent as get_data_science_agent

# Create instance
data_science_agent = get_data_science_agent()

# In root_agent definition, add to sub_agents:
sub_agents=[
    dnb_coordinator,
    data_science_agent,  # ← Add this
]
```

### 7. Test Integrated System
```powershell
adk run agents/root_agent
```

**Try this cross-domain query:**
```
Get all entities from DNB Public Register, query their financial metrics from Statistics, 
and create a bar chart showing top 10 by assets
```

### 8. Commit Changes
```powershell
git add .
git commit -m "feat(adk): Integrate data-science agent from ADK samples

- Import via git subtree for easy upstream sync
- Configure for dnb_statistics and dnb_public_register
- Integrate with root_agent for unified access"

git push origin dev
```

---

## 🎯 What You Just Accomplished

✅ Adopted production-grade data-science agent (4-6 weeks saved)  
✅ Configured for DNB BigQuery datasets  
✅ Integrated with Orkhon's agent hierarchy  
✅ Can now: NL2SQL, BQML, analytics, visualizations  
✅ Syncs with upstream improvements automatically  

---

## 🔄 Monthly Maintenance

**First Monday of each month:**
```powershell
cd C:\Users\rjjaf\_Projects\orkhon
.\backend\scripts\sync-adk-samples.ps1
```

---

## 📚 Full Documentation

- **Comprehensive Guide:** `backend/adk/ADK_SAMPLES_INTEGRATION.md`
- **Quick Reference:** `backend/adk/ADK_SAMPLES_QUICK_REFERENCE.md`
- **Summary:** `backend/adk/ADK_SAMPLES_INTEGRATION_SUMMARY.md`

---

## 🆘 Troubleshooting

### "Sample not found"
```powershell
# Verify remote
git remote -v | Select-String "adk-samples"

# Add if missing
git remote add adk-samples https://github.com/google/adk-samples.git
git fetch adk-samples
```

### "Dependencies conflict"
```powershell
cd backend\adk
uv sync --resolution=highest  # Try latest versions
```

### "Agent not working"
```powershell
# Check environment
cat agents\data-science\.env

# Test toolbox connection
adk run agents/data-science --verbose
```

---

## 🎉 Success!

You've successfully integrated your first ADK sample using git subtree! 

**Next samples to consider:**
- financial-advisor (portfolio analysis, risk assessment)
- customer-service (multi-turn conversations)
- RAG (document Q&A with vector search)

**Have fun building! 🚀**
