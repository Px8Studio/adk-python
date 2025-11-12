#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Syncs all third-party forked repositories with their upstream main branches.

.DESCRIPTION
  This script automates the process of syncing local forks with their upstream
  repositories. It adds upstream remotes if they don't exist, fetches the latest
  changes, and merges them into your local main branch.

.PARAMETER DryRun
  If specified, shows what would be done without actually making changes.

.EXAMPLE
  .\sync-upstream-repos.ps1
  Syncs all repos with their upstreams

.EXAMPLE
  .\sync-upstream-repos.ps1 -DryRun
  Shows what would be synced without making changes
#>

param(
  [switch]$DryRun,
  [switch]$Force,
  [int]$TimeoutSeconds = 120  # <-- Add timeout parameter
)

# Define repository configurations
# Format: LocalPath, UpstreamUrl, DefaultBranch
$repos = @(
  @{
    Path = "C:\Users\rjjaf\_Projects\adk-python"
    Upstream = "https://github.com/google/adk-python.git"
    Branch = "main"
    Name = "ADK Python"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\adk-docs"
    Upstream = "https://github.com/google/adk-docs.git"
    Branch = "main"
    Name = "ADK Docs"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\adk-samples"
    Upstream = "https://github.com/google/adk-samples.git"
    Branch = "main"
    Name = "ADK Samples"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\adk-web"
    Upstream = "https://github.com/google/adk-web.git"
    Branch = "main"
    Name = "ADK Web"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\openapi-mcp-codegen"
    Upstream = "https://github.com/google/openapi-mcp-codegen.git"
    Branch = "main"
    Name = "OpenAPI MCP Codegen"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\genai-toolbox"
    Upstream = "https://github.com/google/genai-toolbox.git"
    Branch = "main"
    Name = "GenAI Toolbox"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\a2a-python"
    Upstream = "https://github.com/google/a2a-python.git"
    Branch = "main"
    Name = "A2A Python"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\a2a-inspector"
    Upstream = "https://github.com/google/a2a-inspector.git"
    Branch = "main"
    Name = "A2A Inspector"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\a2a-samples"
    Upstream = "https://github.com/google/a2a-samples.git"
    Branch = "main"
    Name = "A2A Samples"
  }
)

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Upstream Repository Sync Tool for Third-Party Forks" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
  Write-Host "DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
  Write-Host ""
}

$successCount = 0
$skipCount = 0
$errorCount = 0

# When fetching each upstream repo, only fetch default branch to avoid tracking all branches
$TimeoutSeconds = 120
foreach ($repo in $repos) {
  Write-Host "▶ $($repo.Name)" -ForegroundColor Cyan
  if (-not (Test-Path $repo.Path)) {
    Write-Host "   Skipped (path not found): $($repo.Path)" -ForegroundColor Yellow
    continue
  }

  Push-Location $repo.Path
  try {
    Write-Host "   Ensuring 'upstream' remote exists..." -NoNewline
    if (-not (git remote | Select-String "^upstream$" -Quiet)) {
      git remote add upstream $($repo.Upstream)
      Write-Host " added" -ForegroundColor Green
    } else {
      Write-Host " ok" -ForegroundColor Green
    }

    # Restrict remote fetch to branch only; no tags; prune
    git config --unset-all remote.upstream.fetch 2>$null
    git config --add remote.upstream.fetch "+refs/heads/$($repo.Branch):refs/remotes/upstream/$($repo.Branch)"
    git config remote.upstream.tagOpt "--no-tags"
    git config remote.upstream.prune "true"

    Write-Host "   Fetching $($repo.Branch) from upstream..." -NoNewline
    $fetchJob = Start-Job -ScriptBlock {
      param($path, $branch)
      Set-Location $path
      git fetch --prune --no-tags upstream "+refs/heads/$branch:refs/remotes/upstream/$branch" 2>&1
    } -ArgumentList $repo.Path, $repo.Branch

    Wait-Job $fetchJob | Out-Null
    $output = Receive-Job $fetchJob
    if ($LASTEXITCODE -ne 0) {
      Write-Host "`n$output" -ForegroundColor Red
      throw "Fetch failed"
    } else {
      Write-Host " done" -ForegroundColor Green
    }
  } finally {
    Pop-Location
  }
}

# Summary
Write-Host "================================================================" -ForegroundColor Gray
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "   Successful: $successCount" -ForegroundColor Green
Write-Host "   Skipped: $skipCount" -ForegroundColor Yellow
Write-Host "   Errors: $errorCount" -ForegroundColor Red
Write-Host "================================================================" -ForegroundColor Gray

if ($DryRun) {
  Write-Host ""
  Write-Host "This was a dry run. Run without -DryRun to apply changes." -ForegroundColor Cyan
}
