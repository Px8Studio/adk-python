#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Syncs forked repositories: upstream → origin/main → local main

.DESCRIPTION
  For each third-party fork:
  1. Fetches latest from upstream
  2. Pushes upstream changes to your fork's remote main (origin/main)
  3. Pulls those changes to your local main branch

.PARAMETER DryRun
  Shows what would be done without making changes

.PARAMETER ResetDiverged
  For repos with diverging branches, resets local main to match upstream (DESTRUCTIVE)

.EXAMPLE
  .\sync-upstream-repos.ps1
  Syncs all forks: upstream → origin/main → local main

.EXAMPLE
  .\sync-upstream-repos.ps1 -ResetDiverged
  Resets any diverged local branches to match upstream (discards local commits)
#>

param(
  [switch]$DryRun,
  [switch]$ResetDiverged
)

$ErrorActionPreference = "Stop"

function Write-Step {
  param(
    [Parameter(Mandatory = $true)][string]$Message,
    [ValidateSet("Info", "Success", "Warn", "Error", "Skip")]
    [string]$Level = "Info"
  )

  $prefix, $color = switch ($Level) {
    "Success" { "[OK]", "Green" }
    "Warn"    { "[!!]", "Yellow" }
    "Error"   { "[XX]", "Red" }
    "Skip"    { "[--]", "Yellow" }
    default   { "[>>]", "Gray" }
  }

  Write-Host ("      {0} {1}" -f $prefix, $Message) -ForegroundColor $color
}

function Invoke-GitCommand {
  param(
    [Parameter(Mandatory = $true)][string[]]$Arguments,
    [switch]$IgnoreExitCode
  )

  $process = Start-Process -FilePath "git" `
    -ArgumentList $Arguments `
    -NoNewWindow `
    -Wait `
    -PassThru `
    -RedirectStandardOutput "git_stdout.tmp" `
    -RedirectStandardError "git_stderr.tmp"

  $stdout = if (Test-Path "git_stdout.tmp") { 
    Get-Content "git_stdout.tmp" -Raw 
    Remove-Item "git_stdout.tmp" -Force
  } else { "" }

  $stderr = if (Test-Path "git_stderr.tmp") { 
    Get-Content "git_stderr.tmp" -Raw 
    Remove-Item "git_stderr.tmp" -Force
  } else { "" }

  $exitCode = $process.ExitCode

  $success = ($exitCode -eq 0) -or $IgnoreExitCode

  return [PSCustomObject]@{
    ExitCode = $exitCode
    Output = if ($stdout) { $stdout -split "`n" } else { @() }
    Error = if ($stderr) { $stderr -split "`n" } else { @() }
    Success = $success
  }
}

function Get-RemoteCommit {
  param(
    [Parameter(Mandatory = $true)][string]$Remote,
    [Parameter(Mandatory = $true)][string]$Branch
  )

  $result = Invoke-GitCommand @("ls-remote", $Remote, "refs/heads/$Branch") -IgnoreExitCode
  
  if ($result.ExitCode -ne 0) {
    $errorText = (($result.Error + $result.Output) | Where-Object { $_ } ) -join "`n"
    if ($errorText -match "Repository not found" -or 
        $errorText -match "fatal: repository" -or 
        $errorText -match "access denied" -or 
        $errorText -match "Permission denied") {
      return [PSCustomObject]@{
        Success = $false
        Commit = $null
        ErrorOutput = $result.Error
        Reason = "unreachable"
      }
    }
    
    return [PSCustomObject]@{
      Success = $false
      Commit = $null
      ErrorOutput = $result.Error
      Reason = "error"
    }
  }

  $commit = $null
  $targetRef = "refs/heads/$Branch"
  
  foreach ($line in $result.Output) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    
    $parts = $line -split "`t"
    if ($parts.Length -lt 2) {
      $parts = $line -split "\s+"
    }

    if ($parts.Length -ge 2 -and $parts[1] -eq $targetRef) {
      $commit = $parts[0]
      break
    }
  }

  if (-not $commit) {
    return [PSCustomObject]@{
      Success = $false
      Commit = $null
      ErrorOutput = @("Branch '$Branch' not found on remote $Remote.")
      Reason = "notfound"
    }
  }

  return [PSCustomObject]@{
    Success = $true
    Commit = $commit
    ErrorOutput = @()
    Reason = "ok"
  }
}

function Get-ShortHash {
  param([string]$Hash)

  if ([string]::IsNullOrWhiteSpace($Hash)) {
    return "--------"
  }

  if ($Hash.Length -ge 7) {
    return $Hash.Substring(0, 7)
  }

  return $Hash
}

function Sync-Repository {
  param(
    [Parameter(Mandatory = $true)][hashtable]$Repo,
    [switch]$DryRun,
    [switch]$ResetDiverged
  )

  Push-Location $Repo.Path
  try {
    $changesDetected = $false

    # Step 1: Configure remotes
    Write-Host ("   [1/4] Configure remotes") -ForegroundColor Cyan
    if ($DryRun) {
      Write-Step "Dry run: skipping remote configuration" "Info"
    } else {
      # Get current remotes
      $remoteList = Invoke-GitCommand @("remote")
      if (-not $remoteList.Success) {
        Write-Step "Failed to list git remotes" "Error"
        $remoteList.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
        return "Error"
      }

      $hasUpstream = $remoteList.Output -contains "upstream"

      # Configure upstream
      if (-not $hasUpstream) {
        $addUpstream = Invoke-GitCommand @("remote", "add", "upstream", $Repo.Upstream)
        if (-not $addUpstream.Success) {
          Write-Step "Failed to add upstream remote" "Error"
          $addUpstream.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
          return "Error"
        }
      } else {
        $setUpstream = Invoke-GitCommand @("remote", "set-url", "upstream", $Repo.Upstream)
        if (-not $setUpstream.Success) {
          Write-Step "Failed to update upstream remote URL" "Error"
          $setUpstream.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
          return "Error"
        }
      }

      # Configure origin
      $originUrlResult = Invoke-GitCommand @("remote", "get-url", "origin") -IgnoreExitCode
      if ($originUrlResult.Success) {
        $currentOriginUrl = ($originUrlResult.Output | Where-Object { $_ } | Select-Object -First 1)
        if ($currentOriginUrl -ne $Repo.Origin) {
          $setOrigin = Invoke-GitCommand @("remote", "set-url", "origin", $Repo.Origin)
          if (-not $setOrigin.Success) {
            Write-Step "Failed to set origin remote URL" "Error"
            $setOrigin.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
            return "Error"
          }
        }
      } else {
        $addOrigin = Invoke-GitCommand @("remote", "add", "origin", $Repo.Origin)
        if (-not $addOrigin.Success) {
          Write-Step "Failed to add origin remote" "Error"
          $addOrigin.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
          return "Error"
        }
      }

      # Configure fetch refspec
      $unsetFetch = Invoke-GitCommand @("config", "--unset-all", "remote.upstream.fetch") -IgnoreExitCode
      # Exit code 5 means key not found, which is acceptable
      if (-not $unsetFetch.Success -and $unsetFetch.ExitCode -ne 5) {
        Write-Step "Failed to reset upstream fetch spec" "Error"
        $unsetFetch.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
        return "Error"
      }

      $addFetch = Invoke-GitCommand @("config", "--add", "remote.upstream.fetch", "+refs/heads/$($Repo.Branch):refs/remotes/upstream/$($Repo.Branch)")
      if (-not $addFetch.Success) {
        Write-Step "Failed to set upstream fetch spec" "Error"
        $addFetch.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
        return "Error"
      }

      $tagOpt = Invoke-GitCommand @("config", "remote.upstream.tagOpt", "--no-tags")
      if (-not $tagOpt.Success) {
        Write-Step "Failed to set upstream tag option" "Error"
        $tagOpt.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
        return "Error"
      }

      $prune = Invoke-GitCommand @("config", "remote.upstream.prune", "true")
      if (-not $prune.Success) {
        Write-Step "Failed to enable upstream pruning" "Error"
        $prune.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
        return "Error"
      }

      Write-Step "Remotes configured" "Success"
    }

    # Step 2: Fetch upstream
    Write-Host ("   [2/4] Fetch upstream/{0}" -f $Repo.Branch) -ForegroundColor Cyan
    if ($DryRun) {
      Write-Step "Dry run: skipping upstream fetch" "Info"
    } else {
      $fetchResult = Invoke-GitCommand @("fetch", "--prune", "--no-tags", "upstream", $Repo.Branch) -IgnoreExitCode
      
      if ($fetchResult.ExitCode -ne 0) {
        $errorText = (($fetchResult.Error + $fetchResult.Output) | Where-Object { $_ }) -join "`n"
        if ($errorText -match "Repository not found" -or 
            $errorText -match "fatal: repository" -or 
            $errorText -match "access denied" -or 
            $errorText -match "Permission denied") {
          Write-Step "Upstream repository not accessible; skipping" "Skip"
          return "Skipped"
        }

        Write-Step "Failed to fetch upstream branch" "Error"
        $fetchResult.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
        return "Error"
      }

      # Check if fetch brought new commits
      $fetchOutput = (($fetchResult.Error + $fetchResult.Output) | Where-Object { $_ }) -join "`n"
      if ($fetchOutput -match "\.\." -or $fetchOutput -match "->" -or $fetchOutput -match "new branch") {
        Write-Step "Fetched new commits from upstream" "Success"
        $changesDetected = $true
      } else {
        Write-Step "Already up-to-date with upstream" "Info"
      }
    }

    # Check commit hashes
    $upstreamCommit = Get-RemoteCommit -Remote $Repo.Upstream -Branch $Repo.Branch
    if (-not $upstreamCommit.Success) {
      if ($upstreamCommit.Reason -eq "notfound") {
        Write-Step ("Branch '{0}' not found on upstream; skipping" -f $Repo.Branch) "Skip"
        return "Skipped"
      }

      Write-Step "Unable to read upstream branch" "Error"
      $upstreamCommit.ErrorOutput | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
      return "Error"
    }

    $upstreamHash = $upstreamCommit.Commit
    $originCommit = Get-RemoteCommit -Remote $Repo.Origin -Branch $Repo.Branch

    if (-not $originCommit.Success -and $originCommit.Reason -eq "unreachable") {
      Write-Step "Unable to reach origin remote" "Error"
      $originCommit.ErrorOutput | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
      return "Error"
    }

    $originHash = if ($originCommit.Success) { $originCommit.Commit } else { $null }

    # Step 3: Push to origin if needed
    $needsPush = (-not $originCommit.Success) -or ($originCommit.Commit -ne $upstreamHash)
    
    Write-Host ("   [3/4] Push to origin/{0}" -f $Repo.Branch) -ForegroundColor Cyan
    if (-not $needsPush) {
      Write-Step "Origin already up-to-date" "Info"
    } elseif ($DryRun) {
      Write-Step "Dry run: would push $(Get-ShortHash $upstreamHash) to origin" "Info"
      $changesDetected = $true
    } else {
      $pushResult = Invoke-GitCommand @("push", "origin", "upstream/$($Repo.Branch):refs/heads/$($Repo.Branch)", "--force-with-lease")
      if (-not $pushResult.Success) {
        Write-Step "Git push failed" "Error"
        $pushResult.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
        return "Error"
      }

      Write-Step "Pushed $(Get-ShortHash $upstreamHash) to origin" "Success"
      $changesDetected = $true
    }

    # Step 4: Update local branch
    Write-Host ("   [4/4] Update local {0}" -f $Repo.Branch) -ForegroundColor Cyan
    if ($DryRun) {
      Write-Step "Dry run: skipping local update" "Info"
    } else {
      $currentBranch = (Invoke-GitCommand @("rev-parse", "--abbrev-ref", "HEAD")).Output | Where-Object { $_ } | Select-Object -First 1
      
      if ($currentBranch -eq $Repo.Branch) {
        $pullResult = Invoke-GitCommand @("pull", "--ff-only", "origin", $Repo.Branch) -IgnoreExitCode
        
        if ($pullResult.ExitCode -ne 0) {
          $errorOutput = (($pullResult.Error + $pullResult.Output) | Where-Object { $_ }) -join "`n"
          
          # Check if it's a divergence issue
          if ($errorOutput -match "fatal: Not possible to fast-forward" -or $errorOutput -match "Diverging branches") {
            if ($ResetDiverged) {
              Write-Step "Diverged branch detected - resetting to upstream" "Warn"
              $resetResult = Invoke-GitCommand @("reset", "--hard", "upstream/$($Repo.Branch)")
              if (-not $resetResult.Success) {
                Write-Step "Failed to reset branch" "Error"
                $resetResult.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
                return "Error"
              }
              Write-Step "Local branch reset to upstream" "Success"
              $changesDetected = $true
            } else {
              Write-Step "Local branch has diverged from upstream" "Error"
              Write-Step "Run with -ResetDiverged to reset local branch (DESTRUCTIVE)" "Warn"
              return "Error"
            }
          } else {
            Write-Step "Git pull failed" "Error"
            $pullResult.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
            return "Error"
          }
        } else {
          $pullOutput = (($pullResult.Output + $pullResult.Error) | Where-Object { $_ }) -join "`n"
          if ($pullOutput -match "Already up to date" -or $pullOutput -match "Already up-to-date") {
            Write-Step "Local branch already up-to-date" "Info"
          } else {
            Write-Step "Local branch updated" "Success"
            $changesDetected = $true
          }
        }
      } else {
        $fetchLocalResult = Invoke-GitCommand @("fetch", "origin", "$($Repo.Branch):$($Repo.Branch)")
        if (-not $fetchLocalResult.Success) { 
          Write-Step "Local branch update failed" "Error"
          $fetchLocalResult.Error | Where-Object { $_ } | ForEach-Object { Write-Step $_ "Error" }
          return "Error"
        }
        Write-Step "Local branch updated" "Success"
        $changesDetected = $true
      }
    }

    # Return status
    if ($changesDetected) {
      return "Updated"
    } else {
      return "UpToDate"
    }

  } catch {
    Write-Step "Unexpected error: $_" "Error"
    return "Error"
  } finally {
    Pop-Location
  }
}

# Main execution
$repos = @(
  @{
    Path = "C:\Users\rjjaf\_Projects\adk-python"
    Upstream = "https://github.com/google/adk-python.git"
    Origin = "https://github.com/Px8Studio/adk-python.git"
    Branch = "main"
    Name = "ADK Python"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\adk-docs"
    Upstream = "https://github.com/google/adk-docs.git"
    Origin = "https://github.com/Px8Studio/adk-docs.git"
    Branch = "main"
    Name = "ADK Docs"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\adk-samples"
    Upstream = "https://github.com/google/adk-samples.git"
    Origin = "https://github.com/Px8Studio/adk-samples.git"
    Branch = "main"
    Name = "ADK Samples"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\adk-web"
    Upstream = "https://github.com/google/adk-web.git"
    Origin = "https://github.com/Px8Studio/adk-web.git"
    Branch = "main"
    Name = "ADK Web"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\genai-toolbox"
    Upstream = "https://github.com/googleapis/genai-toolbox.git"
    Origin = "https://github.com/Px8Studio/genai-toolbox.git"
    Branch = "main"
    Name = "GenAI Toolbox"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\a2a-python"
    Upstream = "https://github.com/google/a2a-python.git"
    Origin = "https://github.com/Px8Studio/a2a-python.git"
    Branch = "main"
    Name = "A2A Python"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\a2a-inspector"
    Upstream = "https://github.com/a2aproject/a2a-inspector.git"
    Origin = "https://github.com/Px8Studio/a2a-inspector.git"
    Branch = "main"
    Name = "A2A Inspector"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\a2a-samples"
    Upstream = "https://github.com/a2aproject/a2a-samples.git"
    Origin = "https://github.com/Px8Studio/a2a-samples.git"
    Branch = "main"
    Name = "A2A Samples"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\agent-framework"
    Upstream = "https://github.com/microsoft/semantic-kernel.git"
    Origin = "https://github.com/Px8Studio/agent-framework.git"
    Branch = "main"
    Name = "Agent Framework"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\foundry-samples"
    Upstream = "https://github.com/Azure-Samples/azureai-samples.git"
    Origin = "https://github.com/Px8Studio/foundry-samples.git"
    Branch = "main"
    Name = "Foundry Samples"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\mcp-foundry"
    Upstream = "https://github.com/azure-ai-foundry/mcp-foundry.git"
    Origin = "https://github.com/Px8Studio/mcp-foundry.git"
    Branch = "main"
    Name = "MCP Foundry"
  },
  @{
    Path = "C:\Users\rjjaf\_Projects\datavisualization_langgraph"
    Upstream = "https://github.com/DhruvAtreja/datavisualization_langgraph.git"
    Origin = "https://github.com/Px8Studio/datavisualization_langgraph.git"
    Branch = "main"
    Name = "Data Visualization LangGraph"
  }
)

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Fork Sync: upstream -> origin/main -> local main" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
  Write-Host "[DRY RUN] No changes will be made`n" -ForegroundColor Yellow
}

if ($ResetDiverged) {
  Write-Host "[RESET MODE] Diverged branches will be reset to upstream`n" -ForegroundColor Yellow
}

$updatedCount = 0
$upToDateCount = 0
$skipCount = 0
$errorCount = 0

foreach ($repo in $repos) {
  Write-Host "> $($repo.Name)" -ForegroundColor Cyan
  
  if (-not (Test-Path $repo.Path)) {
    Write-Step "Path not found: $($repo.Path)" "Skip"
    $skipCount++
    Write-Host ""
    continue
  }

  $syncResult = Sync-Repository -Repo $repo -DryRun:$DryRun -ResetDiverged:$ResetDiverged
  
  switch ($syncResult) {
    "Updated" { 
      $updatedCount++
      Write-Host "   Result: Updated" -ForegroundColor Green
    }
    "UpToDate" { 
      $upToDateCount++
      Write-Host "   Result: Already up-to-date" -ForegroundColor Gray
    }
    "Skipped" { 
      $skipCount++
      Write-Host "   Result: Skipped" -ForegroundColor Yellow
    }
    "Error" { 
      $errorCount++
      Write-Host "   Result: Error" -ForegroundColor Red
    }
  }
  
  Write-Host ""
}

Write-Host "================================================================" -ForegroundColor Gray
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "   Updated: $updatedCount" -ForegroundColor Green
Write-Host "   Up-to-date: $upToDateCount" -ForegroundColor Gray
Write-Host "   Skipped: $skipCount" -ForegroundColor Yellow
Write-Host "   Errors: $errorCount" -ForegroundColor Red
Write-Host "================================================================" -ForegroundColor Gray

if ($errorCount -gt 0) { 
  Write-Host "`nTo reset diverged repos, run:" -ForegroundColor Yellow
  Write-Host "  .\sync-upstream-repos.ps1 -ResetDiverged" -ForegroundColor Yellow
  exit 1 
} else { 
  exit 0 
}
