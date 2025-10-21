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

foreach ($repo in $repos) {
  Write-Host "----------------------------------------------------------------" -ForegroundColor Gray
  Write-Host "Processing: $($repo.Name)" -ForegroundColor Cyan
  Write-Host "   Path: $($repo.Path)" -ForegroundColor DarkGray
  
  # Check if directory exists
  if (-not (Test-Path $repo.Path)) {
    Write-Host "   ERROR: Directory does not exist - SKIPPING" -ForegroundColor Red
    $skipCount++
    Write-Host ""
    continue
  }

  Push-Location $repo.Path
  
  try {
    # Check if it's a git repository
    $isGitRepo = Test-Path ".git"
    if (-not $isGitRepo) {
      Write-Host "   ERROR: Not a git repository - SKIPPING" -ForegroundColor Red
      $skipCount++
      Pop-Location
      Write-Host ""
      continue
    }

    # Get current branch
    $currentBranch = git rev-parse --abbrev-ref HEAD 2>$null
    Write-Host "   Current branch: $currentBranch" -ForegroundColor DarkGray

    # Check for uncommitted changes
    $status = git status --porcelain 2>$null
    if ($status) {
      Write-Host "   WARNING: Uncommitted changes detected - SKIPPING" -ForegroundColor Yellow
      Write-Host "   Please commit or stash your changes first" -ForegroundColor Yellow
      $skipCount++
      Pop-Location
      Write-Host ""
      continue
    }

    # Check if upstream remote exists
    $upstreamExists = git remote | Select-String -Pattern "^upstream$" -Quiet
    
    if (-not $upstreamExists) {
      if ($DryRun) {
        Write-Host "   [DRY RUN] Would add upstream remote: $($repo.Upstream)" -ForegroundColor Yellow
      } else {
        Write-Host "   Adding upstream remote..." -ForegroundColor Blue
        git remote add upstream $repo.Upstream
        if ($LASTEXITCODE -ne 0) {
          throw "Failed to add upstream remote"
        }
      }
    } else {
      Write-Host "   OK: Upstream remote already exists" -ForegroundColor Green
    }

    # Modify the fetch section
    Write-Host "   Fetching from upstream (timeout: ${TimeoutSeconds}s)..." -NoNewline

    $fetchJob = Start-Job -ScriptBlock {
      param($path)
      Set-Location $path
      git fetch upstream 2>&1
    } -ArgumentList $repo.Path

    $completed = Wait-Job $fetchJob -Timeout $TimeoutSeconds

    if ($completed) {
      $output = Receive-Job $fetchJob
      if ($fetchJob.State -eq 'Completed') {
        Write-Host " Done" -ForegroundColor Green
      } else {
        Write-Host " Failed" -ForegroundColor Red
        Write-Host "   Error: $output"
      }
    } else {
      Stop-Job $fetchJob
      Write-Host " TIMEOUT" -ForegroundColor Yellow
      Write-Host "   Fetch took longer than ${TimeoutSeconds} seconds"
      Write-Host "   You may need to fetch manually for this repository"
    }

    Remove-Job $fetchJob -Force

    # Switch to target branch if not already on it
    if ($currentBranch -ne $repo.Branch) {
      if ($DryRun) {
        Write-Host "   [DRY RUN] Would checkout branch: $($repo.Branch)" -ForegroundColor Yellow
      } else {
        Write-Host "   Checking out $($repo.Branch)..." -ForegroundColor Blue
        git checkout $repo.Branch 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
          throw "Failed to checkout $($repo.Branch)"
        }
      }
    }

    # Check if merge is needed
    $behindCount = git rev-list --count HEAD..upstream/$($repo.Branch) 2>$null
    if ($behindCount -and $behindCount -gt 0) {
      if ($DryRun) {
        Write-Host "   [DRY RUN] Would merge $behindCount commit(s) from upstream/$($repo.Branch)" -ForegroundColor Yellow
      } else {
        Write-Host "   Merging $behindCount commit(s) from upstream/$($repo.Branch)..." -ForegroundColor Blue
        git merge upstream/$($repo.Branch) --no-edit 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
          throw "Failed to merge from upstream"
        }
        Write-Host "   SUCCESS: Synced with upstream" -ForegroundColor Green
      }
    } else {
      Write-Host "   OK: Already up to date with upstream" -ForegroundColor Green
    }

    # Return to original branch if we switched
    if ($currentBranch -ne $repo.Branch -and -not $DryRun) {
      Write-Host "   Returning to branch: $currentBranch" -ForegroundColor Blue
      git checkout $currentBranch 2>&1 | Out-Null
    }

    $successCount++
    
  } catch {
    Write-Host "   ERROR: $_" -ForegroundColor Red
    $errorCount++
  } finally {
    Pop-Location
    Write-Host ""
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
