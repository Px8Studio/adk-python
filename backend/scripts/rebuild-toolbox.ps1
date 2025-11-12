# 🔄 Rebuild Google GenAI Toolbox from Local Source
# This script automates the process of building a custom Toolbox image

param(
  [string]$ToolboxPath = "C:\Users\rjjaf\_Projects\genai-toolbox",
  [string]$ImageTag = "genai-toolbox:dev",
  [switch]$SkipGitSync
)

$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\Users\rjjaf\_Projects\orkhon"

function Show-Step {
  param([string]$Message)
  Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Show-Ok {
  param([string]$Message)
  Write-Host "  [OK]  $Message" -ForegroundColor Green
}

function Show-Err {
  param([string]$Message)
  Write-Host "  [ERR] $Message" -ForegroundColor Red
}

function Show-Info {
  param([string]$Message)
  Write-Host "  [INFO] $Message" -ForegroundColor Yellow
}

# Header
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Rebuild Google GenAI Toolbox from Source              " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Sync with upstream (optional)
if (-not $SkipGitSync) {
  Show-Step "Step 1/4: Syncing genai-toolbox with upstream..."
  try {
    Set-Location $ToolboxPath
    & git pull origin main
    if ($LASTEXITCODE -ne 0) { throw "Git pull failed" }
    Show-Ok "Synced with upstream"
  } catch {
    Show-Err "Failed to sync: $($_.Exception.Message)"
    Show-Info "Continuing with current version... (use -SkipGitSync to skip this step)"
  }
} else {
  Show-Step "Step 1/4: Skipping git sync (-SkipGitSync flag)"
}

# Step 2: Build Docker image
Show-Step "Step 2/4: Building Docker image..."
try {
  $OrkhonToolboxPath = Join-Path $ProjectRoot "backend" "genai-toolbox"
  Set-Location $OrkhonToolboxPath
  
  # ✅ Build using docker-compose to respect the build context
  & docker-compose -f docker-compose.dev.yml build genai-toolbox
  if ($LASTEXITCODE -ne 0) { throw "Docker build failed" }
  Show-Ok "Built image: $ImageTag"
} catch {
  Show-Err "Build failed: $($_.Exception.Message)"
  exit 1
}

# Step 3: Verify docker-compose configuration
Show-Step "Step 3/4: Verifying docker-compose configuration..."
$ComposeFile = Join-Path $ProjectRoot "backend\genai-toolbox\docker-compose.dev.yml"
$ComposeContent = Get-Content $ComposeFile -Raw

if ($ComposeContent -match "build:" -and $ComposeContent -match "image:\s+genai-toolbox:dev") {
  Show-Ok "docker-compose.dev.yml configured for custom build"
} else {
  Show-Info "Ensure docker-compose.dev.yml has:"
  Show-Info "  build: { context: . }"
  Show-Info "  image: genai-toolbox:dev"
}

# Step 4: Restart containers
Show-Step "Step 4/4: Restarting GenAI Toolbox container..."
try {
  Set-Location (Join-Path $ProjectRoot "backend" "genai-toolbox")
  & docker-compose -f docker-compose.dev.yml down
  & docker-compose -f docker-compose.dev.yml up -d
  if ($LASTEXITCODE -ne 0) { throw "Docker compose restart failed" }
  Show-Ok "Container restarted successfully"
} catch {
  Show-Err "Restart failed: $($_.Exception.Message)"
  exit 1
}

# Verify
Show-Step "Verifying deployment..."
Start-Sleep -Seconds 5
try {
  $version = & docker exec genai-toolbox /toolbox --version 2>&1
  if ($LASTEXITCODE -eq 0) {
    Show-Ok "Toolbox version: $version"
  } else {
    Show-Err "Container not responding"
  }
} catch {
  Show-Err "Verification failed: $($_.Exception.Message)"
}

# Show image info
Show-Step "Docker image details..."
& docker images genai-toolbox:dev

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Rebuild Complete!                                      " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
