#Requires -Version 5.1
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

<#
.SYNOPSIS
  Adopts an ADK sample agent via git subtree.

.DESCRIPTION
  Imports or updates an ADK sample agent from google/adk-samples
  using git subtree strategy. Maintains connection to upstream for
  easy updates while allowing local customization.

.PARAMETER SampleName
  Name of the sample agent to adopt (e.g., 'data-science', 'financial-advisor')

.PARAMETER TargetPath
  Target directory relative to repo root (default: backend/adk/agents/{SampleName})

.PARAMETER DryRun
  Show what would be done without executing git commands

.EXAMPLE
  .\adopt-adk-sample.ps1 -SampleName "data-science"

.EXAMPLE
  .\adopt-adk-sample.ps1 -SampleName "financial-advisor" -TargetPath "backend/adk/agents/financial"

.EXAMPLE
  .\adopt-adk-sample.ps1 -SampleName "data-science" -DryRun
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [string]$SampleName,

  [Parameter(Mandatory=$false)]
  [string]$TargetPath = "",

  [Parameter(Mandatory=$false)]
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Constants
$ADK_SAMPLES_REMOTE = "adk-samples"
$ADK_SAMPLES_URL = "https://github.com/google/adk-samples.git"
$UPSTREAM_BRANCH = "main"

# Determine target path
if ([string]::IsNullOrWhiteSpace($TargetPath)) {
  $TargetPath = "backend/adk/agents/$SampleName"
}

# Display header
Write-Host ""
Write-Host "ADK Sample Adoption Tool" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Sample: $SampleName" -ForegroundColor White
Write-Host "Target: $TargetPath" -ForegroundColor White
if ($DryRun) {
  Write-Host "Mode: DRY RUN (no changes will be made)" -ForegroundColor Yellow
}
Write-Host ""

# Step 1: Check git remote
Write-Host "[Step 1/5] Checking git remote..." -ForegroundColor Yellow

$remotes = git remote
if ($remotes -notcontains $ADK_SAMPLES_REMOTE) {
  Write-Host "Adding remote '$ADK_SAMPLES_REMOTE'..." -ForegroundColor White
  
  if (-not $DryRun) {
    git remote add $ADK_SAMPLES_REMOTE $ADK_SAMPLES_URL
    if ($LASTEXITCODE -ne 0) {
      Write-Host "Failed to add remote" -ForegroundColor Red
      exit 1
    }
  } else {
    Write-Host "[DRY RUN] Would execute: git remote add $ADK_SAMPLES_REMOTE $ADK_SAMPLES_URL" -ForegroundColor Gray
  }
  
  Write-Host "Fetching from remote..." -ForegroundColor White
  if (-not $DryRun) {
    git fetch $ADK_SAMPLES_REMOTE
    if ($LASTEXITCODE -ne 0) {
      Write-Host "Failed to fetch from remote" -ForegroundColor Red
      exit 1
    }
  } else {
    Write-Host "[DRY RUN] Would execute: git fetch $ADK_SAMPLES_REMOTE" -ForegroundColor Gray
  }
  
  Write-Host "Remote added successfully" -ForegroundColor Green
} else {
  Write-Host "Remote '$ADK_SAMPLES_REMOTE' already exists" -ForegroundColor Green
  Write-Host "Fetching latest changes..." -ForegroundColor White
  
  if (-not $DryRun) {
    git fetch $ADK_SAMPLES_REMOTE
    if ($LASTEXITCODE -ne 0) {
      Write-Host "Warning: Failed to fetch from remote" -ForegroundColor Yellow
    }
  } else {
    Write-Host "[DRY RUN] Would execute: git fetch $ADK_SAMPLES_REMOTE" -ForegroundColor Gray
  }
}

Write-Host ""

# Step 2: Verify sample exists in upstream
Write-Host "[Step 2/5] Verifying sample exists in upstream..." -ForegroundColor Yellow

$upstreamPath = "python/agents/$SampleName"
$sampleExists = git ls-tree -r "$ADK_SAMPLES_REMOTE/$UPSTREAM_BRANCH" --name-only | Where-Object { $_ -like "$upstreamPath/*" }

if (-not $sampleExists) {
  Write-Host "Sample '$SampleName' not found in upstream repository" -ForegroundColor Red
  Write-Host ""
  Write-Host "Available samples:" -ForegroundColor Yellow
  
  $availableSamples = git ls-tree -r "$ADK_SAMPLES_REMOTE/$UPSTREAM_BRANCH" --name-only | 
    Where-Object { $_ -like "python/agents/*" } |
    ForEach-Object { ($_ -split '/')[2] } |
    Select-Object -Unique |
    Sort-Object
  
  $availableSamples | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }
  
  exit 1
}

Write-Host "Sample exists in upstream" -ForegroundColor Green
Write-Host ""

# Step 3: Check if target path already exists
Write-Host "[Step 3/5] Checking target directory..." -ForegroundColor Yellow

$isUpdate = Test-Path $TargetPath

if ($isUpdate) {
  Write-Host "Target directory already exists: $TargetPath" -ForegroundColor Yellow
  
  $response = Read-Host "Continue and pull updates from upstream? [y/N]"
  if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "Aborted by user" -ForegroundColor Red
    exit 0
  }
  
  Write-Host "Will update existing sample" -ForegroundColor Green
} else {
  Write-Host "Target directory does not exist - will import fresh" -ForegroundColor Green
}

Write-Host ""

# Step 4: Execute git subtree command
if ($isUpdate) {
  Write-Host "[Step 4/5] Pulling updates via git subtree..." -ForegroundColor Yellow
  
  if (-not $DryRun) {
    Write-Host "Executing: git subtree pull --prefix=$TargetPath $ADK_SAMPLES_REMOTE $UPSTREAM_BRANCH --squash" -ForegroundColor Gray
    
    # Create temporary branch that points to the subdirectory
    $tempBranch = "temp-subtree-$SampleName-$(Get-Date -Format 'yyyyMMddHHmmss')"
    git branch -D $tempBranch 2>$null  # Delete if exists
    git subtree split --prefix=$upstreamPath --branch=$tempBranch $ADK_SAMPLES_REMOTE/$UPSTREAM_BRANCH
    
    # Pull from the temporary branch
    git subtree pull --prefix=$TargetPath . $tempBranch --squash
    
    # Clean up temporary branch
    git branch -D $tempBranch
    
    if ($LASTEXITCODE -ne 0) {
      Write-Host ""
      Write-Host "Git subtree pull failed" -ForegroundColor Red
      Write-Host "This may be due to conflicts. Resolve manually and run:" -ForegroundColor Yellow
      Write-Host "  git add ." -ForegroundColor White
      Write-Host "  git commit -m 'merge: Update $SampleName from upstream'" -ForegroundColor White
      exit 1
    }
    
    Write-Host ""
    Write-Host "Sample updated successfully" -ForegroundColor Green
  } else {
    Write-Host "[DRY RUN] Would execute: git subtree pull with temporary branch strategy" -ForegroundColor Gray
  }
} else {
  Write-Host "[Step 4/5] Importing sample via git subtree..." -ForegroundColor Yellow
  
  if (-not $DryRun) {
    Write-Host "Executing: git subtree add --prefix=$TargetPath $ADK_SAMPLES_REMOTE/$UPSTREAM_BRANCH:$upstreamPath --squash" -ForegroundColor Gray
    
    # Create temporary branch that points to the subdirectory
    $tempBranch = "temp-subtree-$SampleName-$(Get-Date -Format 'yyyyMMddHHmmss')"
    git branch -D $tempBranch 2>$null  # Delete if exists
    git subtree split --prefix=$upstreamPath --branch=$tempBranch $ADK_SAMPLES_REMOTE/$UPSTREAM_BRANCH
    
    # Add from the temporary branch
    git subtree add --prefix=$TargetPath . $tempBranch --squash
    
    # Clean up temporary branch
    git branch -D $tempBranch
    
    if ($LASTEXITCODE -ne 0) {
      Write-Host ""
      Write-Host "Git subtree add failed" -ForegroundColor Red
      exit 1
    }
    
    Write-Host ""
    Write-Host "Sample imported successfully" -ForegroundColor Green
  } else {
    Write-Host "[DRY RUN] Would execute: git subtree add with temporary branch strategy" -ForegroundColor Gray
  }
}

Write-Host ""

# Step 5: Post-import instructions
Write-Host "[Step 5/5] Next steps" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Review the imported agent:" -ForegroundColor Cyan
Write-Host "   cd $TargetPath" -ForegroundColor White
Write-Host "   code README.md" -ForegroundColor White
Write-Host ""

Write-Host "2. Copy and configure .env file:" -ForegroundColor Cyan
Write-Host "   cd $TargetPath" -ForegroundColor White
Write-Host "   copy .env.example .env" -ForegroundColor White
Write-Host "   notepad .env" -ForegroundColor White
Write-Host ""

Write-Host "3. Install dependencies:" -ForegroundColor Cyan
Write-Host "   cd backend/adk" -ForegroundColor White
Write-Host "   uv sync" -ForegroundColor White
Write-Host ""

Write-Host "4. Test the agent:" -ForegroundColor Cyan
Write-Host "   adk run $TargetPath" -ForegroundColor White
Write-Host ""

if (-not $isUpdate) {
  Write-Host "5. Commit the changes:" -ForegroundColor Cyan
  Write-Host "   git commit -m 'feat(adk): Import $SampleName from ADK samples'" -ForegroundColor White
  Write-Host "   git push origin dev" -ForegroundColor White
  Write-Host ""
}

Write-Host "Success!" -ForegroundColor Green
Write-Host ""
