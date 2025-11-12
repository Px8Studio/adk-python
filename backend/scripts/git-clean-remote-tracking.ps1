<#
.SYNOPSIS
  Restrict a remote to a single branch and clean existing remote-tracking branches.

.EXAMPLE
  pwsh backend/scripts/git-clean-remote-tracking.ps1 -RepoPath . -RemoteName adk-samples -BranchName main
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory=$false)][string]$RepoPath = ".",
  [Parameter(Mandatory=$true)][string]$RemoteName,
  [Parameter(Mandatory=$false)][string]$BranchName = "main",
  [Parameter(Mandatory=$false)][switch]$VerboseMode
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Info($m){ if ($VerboseMode) { Write-Host $m -ForegroundColor DarkGray } }

if (-not (Test-Path (Join-Path $RepoPath ".git"))) {
  Write-Error "Not a git repo: $RepoPath"
  exit 1
}

Push-Location $RepoPath
try {
  if (-not (git remote | Select-String -Pattern "^$RemoteName$" -Quiet)) {
    Write-Error "Remote '$RemoteName' not found"
    exit 2
  }

  Write-Host "Restricting '$RemoteName' to branch '$BranchName'..." -ForegroundColor Cyan
  git config --unset-all "remote.$RemoteName.fetch" 2>$null
  git config --add "remote.$RemoteName.fetch" "+refs/heads/$BranchName:refs/remotes/$RemoteName/$BranchName"
  git config "remote.$RemoteName.tagOpt" "--no-tags"
  git config "remote.$RemoteName.prune" "true"

  Info "Fetching with prune..."
  git fetch --prune "$RemoteName"

  Info "Deleting extra remote-tracking branches under '$RemoteName/'..."
  git for-each-ref "refs/remotes/$RemoteName/" --format="%(refname:short)" |
    Where-Object { $_ -ne "$RemoteName/$BranchName" } |
    ForEach-Object { git branch -dr $_ 2>$null }

  Write-Host "Done. Remaining branches under $RemoteName:" -ForegroundColor Green
  git branch -r | Select-String "^\s*$RemoteName/"
} finally {
  Pop-Location
}

# Optional tips:
# Count remote branches: git branch -r | Sort-Object | Measure-Object -Line