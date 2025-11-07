#Requires -Version 5.1
<#
.SYNOPSIS
    Check for upstream changes in the data-science agent from adk-samples.

.DESCRIPTION
    Fetches from adk-samples remote and displays recent commits to the
    data-science agent that are not yet in your local copy.

.EXAMPLE
    .\backend\scripts\adk-check-data-science-upstream.ps1
#>

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

Write-Host '📥 Fetching from adk-samples remote...' -ForegroundColor Cyan
git fetch adk-samples

Write-Host ''
Write-Host '📊 Changes in upstream data-science agent:' -ForegroundColor Cyan
Write-Host ''

# Get commits in upstream that we don't have yet
$changes = git log --oneline --graph HEAD..adk-samples/main -- python/agents/data-science | Select-Object -First 20

if ($changes) {
    $changes
    Write-Host ''
    Write-Host '💡 Run "ADK: Pull data-science Agent Updates" task to apply these changes' -ForegroundColor Yellow
} else {
    Write-Host '✅ No upstream changes found - you are up to date!' -ForegroundColor Green
}
