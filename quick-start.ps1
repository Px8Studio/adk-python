# 🚀 Quick Start Script for Orkhon ADK Web
# This script automates the complete startup process

param(
  [switch]$SkipDiagnostics,
  [switch]$RestartToolbox,
  [int]$WaitSeconds = 15
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = "C:\Users\rjjaf\_Projects\orkhon"
$ToolboxPath = Join-Path $ProjectRoot "backend\toolbox"
$VenvActivate = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"

# Color helper functions
function Write-Step {
  param([string]$Message)
  Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Write-Success {
  param([string]$Message)
  Write-Host "    ✓ $Message" -ForegroundColor Green
}

function Write-Error {
  param([string]$Message)
  Write-Host "    ✗ $Message" -ForegroundColor Red
}

function Write-Info {
  param([string]$Message)
  Write-Host "    ℹ $Message" -ForegroundColor Yellow
}

# Header
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Orkhon ADK Web - Quick Start Script             " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Run Diagnostics
if (-not $SkipDiagnostics) {
  Write-Step "Step 1/4: Running system diagnostics..."
  try {
    Set-Location $ProjectRoot
    & "$ProjectRoot\backend\adk\diagnose-setup.ps1"
    Write-Success "Diagnostics completed"
  } catch {
    Write-Error "Diagnostics failed: $($_.Exception.Message)"
    Write-Info "Continuing anyway... (use -SkipDiagnostics to skip this step)"
  }
} else {
  Write-Step "Step 1/4: Skipping diagnostics (-SkipDiagnostics flag)"
}

# Step 2: Start GenAI Toolbox
Write-Step "Step 2/4: Starting GenAI Toolbox (Docker)..."
try {
  Set-Location $ToolboxPath
  
  # Check if already running
  $running = & docker ps --filter "name=genai-toolbox" --format "{{.Names}}" 2>&1
  
  if ($running -and $running -like "*genai-toolbox*") {
    if ($RestartToolbox) {
      Write-Info "Restarting existing container..."
      & docker-compose -f docker-compose.dev.yml restart genai-toolbox-mcp
      if ($LASTEXITCODE -ne 0) { throw "Failed to restart container" }
      Write-Success "Container restarted"
    } else {
      Write-Success "GenAI Toolbox already running: $running"
    }
  } else {
    Write-Info "Starting fresh container..."
    & docker-compose -f docker-compose.dev.yml up -d
    if ($LASTEXITCODE -ne 0) { throw "Failed to start container" }
    Write-Success "Container started successfully"
  }
  
  # Wait for container to be ready
  Write-Info "Waiting $WaitSeconds seconds for GenAI Toolbox to initialize..."
  $elapsed = 0
  $ready = $false
  
  while ($elapsed -lt $WaitSeconds -and -not $ready) {
    Start-Sleep -Seconds 2
    $elapsed += 2
    try {
      $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
      if ($response.StatusCode -eq 200) {
        $ready = $true
        Write-Success "GenAI Toolbox is ready! (responded after $elapsed seconds)"
        break
      }
    } catch {
      Write-Host "." -NoNewline
    }
  }
  
  if (-not $ready) {
    Write-Error "GenAI Toolbox did not respond after $WaitSeconds seconds"
    Write-Info "Container may still be starting. Check logs:"
    Write-Host "    docker-compose -f docker-compose.dev.yml logs genai-toolbox-mcp" -ForegroundColor Yellow
    $continue = Read-Host "`nContinue anyway? (y/n)"
    if ($continue -ne "y") { exit 1 }
  }
  
} catch {
  Write-Error "Failed to start GenAI Toolbox: $($_.Exception.Message)"
  Write-Info "Check Docker Desktop is running"
  Write-Info "Try: docker-compose -f docker-compose.dev.yml logs"
  exit 1
}

# Step 3: Verify Virtual Environment
Write-Step "Step 3/4: Verifying Python virtual environment..."
try {
  Set-Location $ProjectRoot
  
  if (-not (Test-Path $VenvActivate)) {
    Write-Error "Virtual environment not found at: $VenvActivate"
    Write-Info "Run: poetry install"
    exit 1
  }
  
  Write-Success "Virtual environment found"
  
} catch {
  Write-Error "Virtual environment check failed: $($_.Exception.Message)"
  exit 1
}

# Step 4: Start ADK Web Server
Write-Step "Step 4/4: Starting ADK Web Server..."
try {
  Set-Location $ProjectRoot
  
  # Check if port 8000 is in use
  $portInUse = $false
  try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.Connect("localhost", 8000)
    $tcp.Close()
    $portInUse = $true
  } catch {
    $portInUse = $false
  }
  
  if ($portInUse) {
    Write-Error "Port 8000 is already in use!"
    Write-Info "Find what's using it: netstat -ano | findstr :8000"
    $continue = Read-Host "`nTry to kill the process? (y/n)"
    if ($continue -eq "y") {
      $connections = netstat -ano | Select-String ":8000"
      Write-Host $connections
    }
    exit 1
  }
  
  Write-Success "Port 8000 is available"
  Write-Info "Activating virtual environment and starting ADK Web..."
  Write-Host ""
  Write-Host "========================================================" -ForegroundColor Green
  Write-Host "            ADK Web Server Starting...                  " -ForegroundColor Green
  Write-Host "                                                        " -ForegroundColor Green
  Write-Host "  Access the web UI at: http://localhost:8000          " -ForegroundColor Green
  Write-Host "  Press CTRL+C to stop the server                      " -ForegroundColor Green
  Write-Host "========================================================" -ForegroundColor Green
  Write-Host ""
  
  # Activate venv and start server
  & $VenvActivate
  & adk web --reload_agents --host=0.0.0.0 --port=8000 "$ProjectRoot\backend\adk\agents"
  
} catch {
  Write-Error "Failed to start ADK Web: $($_.Exception.Message)"
  Write-Info "Check the error messages above"
  Write-Info "Try running manually: adk web backend\adk\agents"
  exit 1
}

# If we get here, the server was stopped
Write-Host ""
Write-Host "========================================================" -ForegroundColor Yellow
Write-Host "            ADK Web Server Stopped                      " -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Yellow
Write-Host ""
Write-Info "GenAI Toolbox is still running in Docker"
Write-Info "To stop it: cd backend\toolbox && docker-compose -f docker-compose.dev.yml down"