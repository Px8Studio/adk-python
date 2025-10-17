# 🚀 Quick Start Script for Orkhon ADK Web
# This script automates the complete startup process

param(
  [switch]$SkipDiagnostics,
  [switch]$RestartToolbox,
  [int]$WaitSeconds = 30
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = "C:\Users\rjjaf\_Projects\orkhon"
$ToolboxPath = Join-Path $ProjectRoot "backend\toolbox"
$VenvActivate = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"

# Console output helpers (ASCII-only, avoid conflicts with built-ins)
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

# Simple HTTP probe helpers
function Test-Endpoint200 {
  param([string]$Url, [int]$TimeoutSec = 2)
  try {
    $resp = Invoke-WebRequest -Uri $Url -TimeoutSec $TimeoutSec -ErrorAction Stop
    return ($resp.StatusCode -eq 200)
  } catch { return $false }
}

# Helper: Safely join base URL and relative path (avoid Join-Path for HTTP)
function Join-HttpUrl {
  param(
    [Parameter(Mandatory=$true)][string]$Base,
    [Parameter(Mandatory=$true)][string]$Relative
  )
  if (-not $Base.EndsWith('/')) { $Base = "$Base/" }
  $rel = $Relative.TrimStart('/')
  $baseUri = [System.Uri]$Base
  $fullUri = [System.Uri]::new($baseUri, $rel)
  return $fullUri.AbsoluteUri
}

# Replace/define readiness probe to avoid filesystem path APIs on URLs
function Test-ToolboxReady {
  param(
    [Parameter(Mandatory=$true)][string]$BaseUrl
  )

  $probes = @(
    "health",
    "api/toolsets",   # preferred (plural)
    "api/toolset/",   # legacy path (singular)
    "ui/"
  )

  foreach ($rel in $probes) {
    try {
      $url = Join-HttpUrl -Base $BaseUrl -Relative $rel
      $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -Method Get -TimeoutSec 3
      if ($resp -and $resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) {
        return @{ Ready = $true; Url = $url }
      }
    } catch {
      # Ignore and try next endpoint
    }
  }

  return @{ Ready = $false; Url = $null }
}

# Header
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Orkhon ADK Web - Quick Start Script             " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Run Diagnostics
if (-not $SkipDiagnostics) {
  Show-Step "Step 1/4: Running system diagnostics..."
  try {
    # Prefer repo-root diagnostics, then legacy backend path
    $diagCandidates = @(
      (Join-Path $ProjectRoot "diagnose-setup.ps1"),
      (Join-Path $ProjectRoot "backend\adk\diagnose-setup.ps1")
    )

    $diagScript = $null
    foreach ($c in $diagCandidates) {
      if (Test-Path $c) { $diagScript = $c; break }
    }

    if ($diagScript) {
  Show-Info "Found diagnostics script: $diagScript"

      # Always run diagnostics in a separate PowerShell process
      Set-Location $ProjectRoot
      $result = Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $diagScript `
        -Wait -PassThru -NoNewWindow
      if ($result.ExitCode -ne 0) {
        Show-Err "Diagnostics exited with code: $($result.ExitCode)"
        Show-Info "Continuing anyway... (use -SkipDiagnostics to skip this step)"
      } else {
        Show-Ok "Diagnostics completed successfully"
      }
    } else {
      # Fallback: use cross-platform Python CLI (scripts/dev.py diagnose)
  Show-Info "Diagnostics scripts not found. Falling back to Python CLI diagnose..."
      $devCli = Join-Path $ProjectRoot "scripts/dev.py"
      $venvPy = Join-Path $ProjectRoot ".venv/Scripts/python.exe"
      # PowerShell 5.1 doesn't support the ternary operator, use if/else instead
      if (Test-Path $venvPy) {
        $python = $venvPy
      } else {
        $python = "python"
      }
      $psi = New-Object System.Diagnostics.ProcessStartInfo
      $psi.FileName = $python
      $psi.Arguments = "`"$devCli`" diagnose"
      $psi.WorkingDirectory = $ProjectRoot
      $psi.UseShellExecute = $false
      $psi.RedirectStandardOutput = $true
      $psi.RedirectStandardError = $true
      $p = [System.Diagnostics.Process]::Start($psi)
      $p.WaitForExit()
      if ($p.ExitCode -ne 0) {
        Show-Err "Diagnostics (Python CLI) exited with code: $($p.ExitCode)"
        Show-Info "Continuing anyway... (use -SkipDiagnostics to skip this step)"
      } else {
        Show-Ok "Diagnostics completed successfully (Python CLI)"
      }
    }
  } catch {
    Show-Err "Diagnostics failed: $($_.Exception.Message)"
    Show-Info "Continuing anyway... (use -SkipDiagnostics to skip this step)"
  }
} else {
  Show-Step "Step 1/4: Skipping diagnostics (-SkipDiagnostics flag)"
}

# Step 2: Start GenAI Toolbox
Show-Step "Step 2/4: Starting GenAI Toolbox (Docker)..."
try {
  Set-Location $ToolboxPath
  
  # Check if already running
  $running = & docker ps --filter "name=genai-toolbox" --format "{{.Names}}" 2>&1
  
  if ($running -and $running -like "*genai-toolbox*") {
    if ($RestartToolbox) {
  Show-Info "Restarting existing container..."
      & docker-compose -f docker-compose.dev.yml restart genai-toolbox-mcp
      if ($LASTEXITCODE -ne 0) { throw "Failed to restart container" }
      Show-Ok "Container restarted"
    } else {
      Show-Ok "GenAI Toolbox already running: $running"
    }
  } else {
    Show-Info "Starting fresh container..."
    & docker-compose -f docker-compose.dev.yml up -d
    if ($LASTEXITCODE -ne 0) { throw "Failed to start container" }
    Show-Ok "Container started successfully"
  }

  # Fast readiness probe with fallbacks
  $base = "http://localhost:5000/"
  $ready = $false
  $readyUrl = $null
  $probe = Test-ToolboxReady -BaseUrl $base
  if ($probe.Ready) {
    $ready = $true
    $readyUrl = $probe.Url
    Show-Ok "GenAI Toolbox responded at: $readyUrl (skipping wait)"
  }

  if (-not $ready) {
    # Wait for container to be ready
    Show-Info "Waiting $WaitSeconds seconds for GenAI Toolbox to initialize..."
    $elapsed = 0
    while ($elapsed -lt $WaitSeconds -and -not $ready) {
      Start-Sleep -Seconds 2
      $elapsed += 2
      $probe = Test-ToolboxReady -BaseUrl $base
      if ($probe.Ready) {
        $ready = $true
        $readyUrl = $probe.Url
        Show-Ok "GenAI Toolbox is ready (after $elapsed s) at: $readyUrl"
        break
      } else {
        Write-Host "." -NoNewline
      }
    }

    if (-not $ready) {
      Show-Err "GenAI Toolbox did not respond on any of: /health, /api/toolset/, /ui/ after $WaitSeconds seconds"
      Show-Info "Container may still be starting. Check logs:"
      Write-Host "    docker-compose -f docker-compose.dev.yml logs genai-toolbox-mcp" -ForegroundColor Yellow
      $continue = Read-Host "`nContinue anyway? (y/n)"
      if ($continue -ne "y") { exit 1 }
    }
  }
  
} catch {
  Show-Err "Failed to start GenAI Toolbox: $($_.Exception.Message)"
  Show-Info "Check Docker Desktop is running"
  Show-Info "Try: docker-compose -f docker-compose.dev.yml logs"
  exit 1
}

# Step 3: Verify Virtual Environment
Show-Step "Step 3/4: Verifying Python virtual environment..."
try {
  Set-Location $ProjectRoot
  
  if (-not (Test-Path $VenvActivate)) {
    Show-Err "Virtual environment not found at: $VenvActivate"
    Show-Info "Run: poetry install"
    exit 1
  }
  
  Show-Ok "Virtual environment found"
  
} catch {
  Show-Err "Virtual environment check failed: $($_.Exception.Message)"
  exit 1
}

# Step 4: Start ADK Web Server
Show-Step "Step 4/4: Starting ADK Web Server..."
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
    Show-Err "Port 8000 is already in use!"
    Show-Info "Find what's using it: netstat -ano | findstr :8000"
    $continue = Read-Host "`nTry to kill the process? (y/n)"
    if ($continue -eq "y") {
      $connections = netstat -ano | Select-String ":8000"
      Write-Host $connections
    }
    exit 1
  }
  
  Show-Ok "Port 8000 is available"
  Show-Info "Activating virtual environment and starting ADK Web..."
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
  Show-Err "Failed to start ADK Web: $($_.Exception.Message)"
  Show-Info "Check the error messages above"
  Show-Info "Try running manually: adk web backend\adk\agents"
  exit 1
}

# If we get here, the server was stopped
Write-Host ""
Write-Host "========================================================" -ForegroundColor Yellow
Write-Host "            ADK Web Server Stopped                      " -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Yellow
Write-Host ""
Show-Info "GenAI Toolbox is still running in Docker"
Show-Info "To stop it: cd backend\toolbox && docker-compose -f docker-compose.dev.yml down"