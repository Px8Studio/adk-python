# 🚀 Quick Start Script for Orkhon ADK Web
# This script automates the complete startup process for the full stack:
#   - Docker network creation
#   - GenAI Toolbox MCP Server + Jaeger + PostgreSQL (if configured)
#   - ADK Web Server
#   - Opens Web UIs automatically

param(
  [switch]$SkipDiagnostics,
  [switch]$RestartToolbox,
  [bool]$OpenUIs = $true,    # Automatically open web UIs
  [int]$WaitSeconds = 60,     # Increased default wait time
  [switch]$ForceRecreate      # Force recreate containers
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = "C:\Users\rjjaf\_Projects\orkhon"
$ToolboxPath = Join-Path $ProjectRoot "backend\toolbox"
$VenvActivate = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"
$DotEnv = Join-Path $ProjectRoot ".env"

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
Write-Host "  Orkhon Full Stack - Quick Start Script                " -ForegroundColor Cyan
Write-Host "  Starting: Toolbox + Jaeger + ADK Web + UIs            " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Run Diagnostics
if (-not $SkipDiagnostics) {
  Show-Step "Step 1/6: Running system diagnostics..."
  try {
    # Use new location in backend/scripts
    $diagCandidates = @(
      (Join-Path $ProjectRoot "backend\scripts\diagnose-setup.ps1")
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
      Show-Info "Diagnostics scripts not found. Skipping diagnostics step."
    }
  } catch {
    Show-Err "Diagnostics failed: $($_.Exception.Message)"
    Show-Info "Continuing anyway... (use -SkipDiagnostics to skip this step)"
  }
} else {
  Show-Step "Step 1/6: Skipping diagnostics (-SkipDiagnostics flag)"
}

# Step 2: Ensure Docker Network Exists
Show-Step "Step 2/6: Ensuring Docker network exists..."
try {
  $networkName = "orkhon-network"

  # Try to inspect the network and capture output (stderr + stdout)
  $inspectOutput = & docker network inspect $networkName 2>&1
  if ($LASTEXITCODE -ne 0) {
    $errText = ($inspectOutput -join "`n").ToString()

    # Detect common signs that the Docker daemon (Docker Desktop) is not reachable
    if ($errText -match "dockerDesktopLinuxEngine" -or
        $errText -match "open //./pipe" -or
        $errText -match "cannot connect to the Docker daemon" -or
        $errText -match "Is the docker daemon running") {

      Show-Err "Docker engine not reachable. This usually means Docker Desktop (daemon) is not running."
      Show-Info "Action: Start Docker Desktop and ensure the Docker daemon/WSL backend is running."
      Show-Info "  - On Windows: Start 'Docker Desktop' from the Start Menu or system tray."
      Show-Info "  - Wait a minute for Docker to finish initializing, then re-run this script."
      Show-Info "If you prefer to continue without Docker, re-run with -SkipDiagnostics (not recommended)."
      exit 2
    }

    # Otherwise attempt to create the network (normal create path)
    Show-Info "Creating Docker network: $networkName"
    $createOutput = & docker network create $networkName 2>&1
    if ($LASTEXITCODE -eq 0) {
      Show-Ok "Docker network created: $networkName"
    } else {
      Show-Err "Failed to create Docker network: $($createOutput -join ' ')"
      exit 1
    }
  } else {
    Show-Ok "Docker network already exists: $networkName"
  }
} catch {
  Show-Err "Failed to check/create Docker network: $($_.Exception.Message)"
  Show-Info "Hint: Ensure Docker Desktop is installed and running. Start Docker Desktop and try again."
  exit 1
}

# Step 3: Start GenAI Toolbox Stack (Toolbox + Jaeger + PostgreSQL if configured)
Show-Step "Step 3/6: Starting GenAI Toolbox Stack (Docker)..."
try {
  Set-Location $ToolboxPath
  
  # Check if containers are already running
  $runningContainers = & docker ps --filter "name=orkhon-" --format "{{.Names}}" 2>&1
  
  if ($ForceRecreate) {
    Show-Info "Force recreating containers..."
    & docker-compose -f docker-compose.dev.yml down
    & docker-compose -f docker-compose.dev.yml up -d --force-recreate
    if ($LASTEXITCODE -ne 0) { throw "Failed to recreate containers" }
    Show-Ok "Containers recreated successfully"
  }
  elseif ($runningContainers -and $runningContainers -like "*genai-toolbox*") {
    if ($RestartToolbox) {
      Show-Info "Restarting existing containers..."
      & docker-compose -f docker-compose.dev.yml restart
      if ($LASTEXITCODE -ne 0) { throw "Failed to restart containers" }
      Show-Ok "Containers restarted"
    } else {
      Show-Ok "GenAI Toolbox Stack already running"
      Show-Info "Use -RestartToolbox to restart, or -ForceRecreate to recreate"
    }
  } else {
    Show-Info "Starting fresh containers..."
    & docker-compose -f docker-compose.dev.yml up -d
    if ($LASTEXITCODE -ne 0) { throw "Failed to start containers" }
    Show-Ok "Containers started successfully"
  }

  # Display running containers
  Show-Info "Checking container status..."
  $containers = & docker ps --filter "name=orkhon-" --format "table {{.Names}}\t{{.Status}}" 2>&1
  Write-Host $containers -ForegroundColor Yellow

  # Comprehensive readiness check for multiple services
  Show-Info "Waiting for services to be ready (up to $WaitSeconds seconds)..."
  
  $services = @{
    "Toolbox" = @{
      Url = "http://localhost:5000"
      Probes = @("health", "api/toolsets", "api/toolset/", "ui/")
      Ready = $false
    }
    "Jaeger" = @{
      Url = "http://localhost:16686"
      Probes = @("", "search")  # Root and search endpoint
      Ready = $false
    }
  }

  $elapsed = 0
  $allReady = $false
  
  while ($elapsed -lt $WaitSeconds -and -not $allReady) {
    $allReady = $true
    
    foreach ($serviceName in $services.Keys) {
      if (-not $services[$serviceName].Ready) {
        $base = $services[$serviceName].Url
        $probes = $services[$serviceName].Probes
        
        foreach ($rel in $probes) {
          try {
            $url = if ($rel) { Join-HttpUrl -Base $base -Relative $rel } else { $base }
            $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -Method Get -TimeoutSec 2 -ErrorAction Stop
            if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) {
              $services[$serviceName].Ready = $true
              Show-Ok "$serviceName is ready at: $url"
              break
            }
          } catch {
            # Service not ready yet, continue checking
          }
        }
        
        if (-not $services[$serviceName].Ready) {
          $allReady = $false
        }
      }
    }
    
    if (-not $allReady) {
      Start-Sleep -Seconds 3
      $elapsed += 3
      Write-Host "." -NoNewline
    }
  }

  Write-Host ""  # New line after dots
  
  # Report final status
  $anyFailed = $false
  foreach ($serviceName in $services.Keys) {
    if (-not $services[$serviceName].Ready) {
      Show-Err "$serviceName did not become ready after $WaitSeconds seconds"
      Show-Info "Check logs: docker-compose -f docker-compose.dev.yml logs $serviceName"
      $anyFailed = $true
    }
  }
  
  if ($anyFailed) {
    Show-Info "Some services may still be starting. Container logs:"
    Write-Host "  docker-compose -f docker-compose.dev.yml logs --tail=50" -ForegroundColor Yellow
    $continue = Read-Host "`nContinue anyway? (y/n)"
    if ($continue -ne "y") { exit 1 }
  } else {
    Show-Ok "All services are ready!"
  }
  
} catch {
  Show-Err "Failed to start GenAI Toolbox Stack: $($_.Exception.Message)"
  Show-Info "Check Docker Desktop is running"
  Show-Info "Try: docker-compose -f docker-compose.dev.yml logs"
  exit 1
}

# Step 4: Open Web UIs
if ($OpenUIs) {
  Show-Step "Step 4/6: Opening Web UIs..."
  try {
    # Only open UIs for services that are ready
    if ($services["Toolbox"].Ready) {
      Show-Info "Opening GenAI Toolbox UI..."
      Start-Process "http://localhost:5000/ui/"
      Start-Sleep -Seconds 1
    }
    
    if ($services["Jaeger"].Ready) {
      Show-Info "Opening Jaeger Tracing UI..."
      Start-Process "http://localhost:16686"
      Start-Sleep -Seconds 1
    }
    
    Show-Ok "Web UIs opened in browser"
  } catch {
    Show-Info "Could not open web UIs automatically: $($_.Exception.Message)"
    Show-Info "Open manually:"
    Write-Host "  - Toolbox UI: http://localhost:5000/ui/" -ForegroundColor Yellow
    Write-Host "  - Jaeger UI:  http://localhost:16686" -ForegroundColor Yellow
  }
} else {
  Show-Step "Step 4/6: Skipping Web UI opening (-OpenUIs=$false)"
  Show-Info "Access services at:"
  Write-Host "  - Toolbox UI: http://localhost:5000/ui/" -ForegroundColor Yellow
  Write-Host "  - Jaeger UI:  http://localhost:16686" -ForegroundColor Yellow
}

# Step 5: Verify Virtual Environment
Show-Step "Step 5/6: Verifying Python virtual environment..."
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

# Step 6: Start ADK Web Server
Show-Step "Step 6/6: Starting ADK Web Server..."
try {
  Set-Location $ProjectRoot

  # Load .env if present (simple parser; ignores comments/empty lines)
  if (Test-Path $DotEnv) {
    Show-Info "Loading environment from .env"
    try {
      Get-Content -Path $DotEnv | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith('#')) { return }
        $idx = $line.IndexOf('=')
        if ($idx -gt 0) {
          $key = $line.Substring(0, $idx).Trim()
          $val = $line.Substring($idx + 1).Trim().Trim('"').Trim("'")
          if (-not [string]::IsNullOrWhiteSpace($key)) {
            # Only set if not already present in the current process environment
            $current = [System.Environment]::GetEnvironmentVariable($key, 'Process')
            if ([string]::IsNullOrWhiteSpace($current)) {
              [System.Environment]::SetEnvironmentVariable($key, $val, 'Process')
            }
          }
        }
      }
    } catch {
      Show-Info "Failed to parse .env (continuing): $($_.Exception.Message)"
    }
  } else {
    Show-Info ".env not found (optional). You can copy .env.example and fill values."
  }
  
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
  Write-Host "  Full Stack Running:                                  " -ForegroundColor Green
  Write-Host "  • ADK Web:     http://localhost:8000                 " -ForegroundColor Green
  Write-Host "  • Toolbox UI:  http://localhost:5000/ui/             " -ForegroundColor Green
  Write-Host "  • Jaeger UI:   http://localhost:16686                " -ForegroundColor Green
  Write-Host "                                                        " -ForegroundColor Green
  Write-Host "  Press CTRL+C to stop the ADK server                  " -ForegroundColor Green
  Write-Host "  (Toolbox services will continue running in Docker)   " -ForegroundColor Green
  Write-Host "========================================================" -ForegroundColor Green
  Write-Host ""
  
  # Activate venv and start server
  & $VenvActivate
  # If only GEMINI_API_KEY is set, mirror it to GOOGLE_API_KEY for downstream libs
  $gemini = [System.Environment]::GetEnvironmentVariable('GEMINI_API_KEY', 'Process')
  $google = [System.Environment]::GetEnvironmentVariable('GOOGLE_API_KEY', 'Process')
  if ($gemini -and [string]::IsNullOrWhiteSpace($google)) {
    [System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', $gemini, 'Process')
    Show-Info "Mirrored GEMINI_API_KEY -> GOOGLE_API_KEY for this session"
  }
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
Show-Info "Docker services are still running:"
Write-Host "  • GenAI Toolbox: http://localhost:5000/ui/" -ForegroundColor Yellow
Write-Host "  • Jaeger:        http://localhost:16686" -ForegroundColor Yellow
Write-Host ""
Show-Info "To stop all services:"
Write-Host "  cd backend\toolbox" -ForegroundColor Cyan
Write-Host "  docker-compose -f docker-compose.dev.yml down" -ForegroundColor Cyan
Write-Host ""
Show-Info "To stop Docker services only:"
Write-Host "  docker stop orkhon-genai-toolbox-mcp orkhon-jaeger" -ForegroundColor Cyan