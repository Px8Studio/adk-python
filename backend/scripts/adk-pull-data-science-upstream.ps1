#Requires -Version 5.1
<#
.SYNOPSIS
    Pull upstream updates for the data-science agent from adk-samples.

.DESCRIPTION
    Fetches from adk-samples remote and merges upstream changes into
    your local data-science agent using git subtree pull.

.EXAMPLE
    .\backend\scripts\adk-pull-data-science-upstream.ps1
#>

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host '📥 Fetching from adk-samples remote...' -ForegroundColor Cyan
git fetch adk-samples

Write-Host ''
Write-Host '🔄 Pulling updates for data-science agent...' -ForegroundColor Cyan
Write-Host ''

# Pull updates using git subtree
git subtree pull --prefix=backend/adk/agents/data-science adk-samples/main --squash

Write-Host ''
Write-Host '✅ Update complete! Review changes and test agent.' -ForegroundColor Green
Write-Host ''
Write-Host 'Next steps:' -ForegroundColor Cyan
Write-Host '  1. Review changes: git log -p --since="1 hour ago" backend/adk/agents/data-science'
Write-Host '  2. Test agent: cd backend/adk && uv sync && uv run adk run agents/data-science'
Write-Host '  3. Commit if satisfied: git add . && git commit -m "chore(adk): Update data-science agent from upstream"'
