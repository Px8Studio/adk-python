param(
  [string]$RepoPath = ".",
  [string]$DefaultBranch = "main",
  [switch]$Isolate,     # If set: remove third-party remotes instead of restricting fetch
  [switch]$VerboseMode
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Info($msg){ if ($VerboseMode) { Write-Host $msg -ForegroundColor DarkGray } }

function Restrict-Remote([string]$remote, [string]$branch) {
  if (-not (git remote | Select-String -Pattern "^$remote$" -Quiet)) { return }
  Info "  Restricting $remote to $branch only"
  git config --unset-all "remote.$remote.fetch" 2>$null
  git config --add "remote.$remote.fetch" "+refs/heads/$branch:refs/remotes/$remote/$branch"
  git config "remote.$remote.tagOpt" "--no-tags"
  git config "remote.$remote.prune" "true"
}

function Prune-RemoteBranches([string]$remote, [string]$keep) {
  if (-not (git remote | Select-String -Pattern "^$remote$" -Quiet)) { return }
  Info "  Pruning $remote"
  git fetch --prune "$remote"
  # Delete all remote-tracking branches except the kept one
  git for-each-ref "refs/remotes/$remote/" --format="%(refname:short)" |
    Where-Object { $_ -ne "$remote/$keep" } |
    ForEach-Object { git branch -dr $_ 2>$null }
}

function Remove-Remote([string]$remote) {
  if (-not (git remote | Select-String -Pattern "^$remote$" -Quiet)) { return }
  Write-Host "  Removing remote '$remote'..." -ForegroundColor Yellow
  git remote remove "$remote"
}

if (-not (Test-Path (Join-Path $RepoPath ".git"))) {
  Write-Error "Not a git repo: $RepoPath"
  exit 1
}

Push-Location $RepoPath
try {
  Write-Host "Repo: $(Resolve-Path .)" -ForegroundColor Cyan
  Write-Host "Current remotes:" -ForegroundColor Cyan
  git remote -v

  if ($Isolate) {
    # Max isolation: remove third-party remotes commonly used in this workspace
    foreach ($r in @("upstream","adk-samples")) {
      Remove-Remote $r
    }
    # Optional: restrict origin to main to avoid all branches from your fork
    if (git remote | Select-String "^origin$" -Quiet) {
      Restrict-Remote -remote "origin" -branch $DefaultBranch
      Prune-RemoteBranches -remote "origin" -keep $DefaultBranch
    }
    git fetch --prune --all
  } else {
    # Restrict common remotes to main only
    foreach ($r in @("origin","upstream","adk-samples")) {
      if (git remote | Select-String "^$r$" -Quiet) {
        Restrict-Remote -remote $r -branch $DefaultBranch
        Prune-RemoteBranches -remote $r -keep $DefaultBranch
      }
    }
  }

  Write-Host "`nAfter:" -ForegroundColor Cyan
  git remote -v
  Write-Host "`nFetch refspecs:" -ForegroundColor Cyan
  foreach ($r in (git remote)) {
    $specs = git config --get-all "remote.$r.fetch"
    Write-Host "  $r => $specs"
  }

  Write-Host "`nTip (PowerShell):" -ForegroundColor DarkGray
  Write-Host "  Count remote branches: git branch -r | Sort-Object | Measure-Object -Line" -ForegroundColor DarkGray
} finally {
  Pop-Location
}

# Usage examples:
#   pwsh backend/scripts/git-tighten-fetch.ps1                     # restrict to main for origin/upstream/adk-samples
#   pwsh backend/scripts/git-tighten-fetch.ps1 -Isolate            # remove upstream/adk-samples, keep origin main only
#   pwsh backend/scripts/git-tighten-fetch.ps1 -RepoPath C:\Users\rjjaf\_Projects\adk-samples