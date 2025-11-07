#Requires -Version 5.1
<#
.SYNOPSIS
    Compare local data-science agent with upstream version.

.DESCRIPTION
    Fetches from adk-samples remote and shows file-level differences
    between your local data-science agent and the upstream version.

.EXAMPLE
    .\backend\scripts\adk-compare-data-science-upstream.ps1
#>

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host '📥 Fetching from adk-samples remote...' -ForegroundColor Cyan
git fetch adk-samples

Write-Host ''
Write-Host '📊 File differences between local and upstream:' -ForegroundColor Cyan
Write-Host ''

# Show file statistics
git diff --stat HEAD adk-samples/main -- python/agents/data-science

Write-Host ''
Write-Host '💡 Use "git diff HEAD adk-samples/main -- python/agents/data-science/<file>" for detailed diff' -ForegroundColor Yellow
Write-Host '💡 Or use VS Code: git diff to view changes visually' -ForegroundColor Yellow
