# 🚀 Quick Start Script for Orkhon ADK Web
# This script automates the complete startup process for the full stack:
#   - Docker network creation
#   - GenAI Toolbox MCP Server + Jaeger + PostgreSQL (if configured)
#   - ADK Web Server
#   - Opens Web UIs automatically

param(
  [switch]$SkipDiagnostics,
  [switch]$RestartToolbox,
  [bool]$OpenUIs = $true,
  [int]$WaitSeconds = 60,
  [switch]$ForceRecreate
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Paths and environment
$ProjectRoot = "C:\Users\rjjaf\_Projects\orkhon"
$ToolboxPath = Join-Path $ProjectRoot "backend\toolbox"
$DiagnosticsScript = Join-Path $ProjectRoot "backend\scripts\diagnose-setup.ps1"
$VenvActivate = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"
$DotEnv = Join-Path $ProjectRoot ".env"
$ProjectName = "orkhon"
$env:COMPOSE_PROJECT_NAME = $ProjectName

# Console helpers
function Show-Step { param([string]$Message) Write-Host "`n==> $Message" -ForegroundColor Cyan }
function Show-Ok { param([string]$Message) Write-Host "  [OK]  $Message" -ForegroundColor Green }
function Show-Err { param([string]$Message) Write-Host "  [ERR] $Message" -ForegroundColor Red }
function Show-Info { param([string]$Message) Write-Host "  [INFO] $Message" -ForegroundColor Yellow }

# HTTP utilities
function Join-HttpUrl {
  param(
    [Parameter(Mandatory = $true)][string]$Base,
    [Parameter(Mandatory = $true)][string]$Relative
  )
  if (-not $Base.EndsWith('/')) { $Base = "$Base/" }
  $rel = $Relative.TrimStart('/')
  $baseUri = [System.Uri]$Base
  $fullUri = [System.Uri]::new($baseUri, $rel)
  return $fullUri.AbsoluteUri
}

# Port utilities
function Test-PortFree {
  param([int]$Port)
  try {
    $client = New-Object System.Net.Sockets.TcpClient
    $client.Connect('localhost', $Port)
    $client.Close()
    return $false
  } catch { return $true }
}

function Resolve-PortConflict {
  param(
    [int]$Port,
    [string]$ServiceName
  )

  Write-Host ("  [WARN] Port {0} in use. Attempting to free for {1}..." -f $Port, $ServiceName) -ForegroundColor Yellow
  $containers = & docker ps --filter ("publish={0}" -f $Port) --format "{{.ID}} {{.Names}}" 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $containers) {
    Write-Host ("  [WARN] Port {0} held by a non-docker process or docker query failed. Please free it manually and rerun." -f $Port) -ForegroundColor Yellow
    return $false
  }

  $resolved = $false
  foreach ($entry in $containers) {
    $parts = $entry -split '\s+', 2
    $id = $parts[0]
    $name = if ($parts.Length -gt 1) { $parts[1] } else { $id }
    Write-Host ("  [INFO] Stopping container '{0}' holding port {1}..." -f $name, $Port)
    try {
      & docker stop $id | Out-Null
      & docker rm $id | Out-Null
      $resolved = $true
    } catch {
      Write-Host ("  [ERR] Failed to stop/remove container {0}: {1}" -f $name, $_.Exception.Message) -ForegroundColor Red
      return $false
    }
  }

  if ($resolved) {
    Write-Host ("  [OK]  Port {0} freed for {1}" -f $Port, $ServiceName)
  }
  return $resolved
}

function Ensure-CriticalPortsFree {
  param([array]$PortInfoList)

  foreach ($info in $PortInfoList) {
    $port = [int]$info.Port
    $service = $info.Service
    if (-not (Test-PortFree -Port $port)) {
      Write-Host ("  [INFO] Port {0} in use ({1}). Attempting to free existing binding..." -f $port, $service) -ForegroundColor Yellow
      $null = Resolve-PortConflict -Port $port -ServiceName $service
      if (-not (Test-PortFree -Port $port)) {
        throw ("Port {0} remains busy after cleanup. Free the port manually and rerun the quick-start script." -f $port)
      }
    }
  }
}

# Header
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Orkhon Full Stack - Quick Start Script                " -ForegroundColor Cyan
Write-Host "  Starting: Toolbox + Jaeger + ADK Web + UIs            " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Diagnostics
if (-not $SkipDiagnostics) {
  Show-Step "Step 1/6: Running system diagnostics..."
  if (Test-Path $DiagnosticsScript) {
    Show-Info "Found diagnostics script: $DiagnosticsScript"
    try {
      Set-Location $ProjectRoot
      $result = Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $DiagnosticsScript, `
                      "-ProjectRoot", "$ProjectRoot" `
        -Wait -PassThru -NoNewWindow
      if ($result.ExitCode -ne 0) {
        Show-Err "Diagnostics exited with code: $($result.ExitCode)"
        Show-Info "Continuing anyway... (use -SkipDiagnostics to skip this step)"
      } else {
        Show-Ok "Diagnostics completed successfully"
      }
    } catch {
      Show-Err "Diagnostics failed: $($_.Exception.Message)"
      Show-Info "Continuing anyway... (use -SkipDiagnostics to skip this step)"
    }
  } else {
    Show-Info "Diagnostics script not found. Skipping."
  }
} else {
  Show-Step "Step 1/6: Skipping diagnostics (-SkipDiagnostics flag)"
}

# Step 2: Ensure Docker network
Show-Step "Step 2/6: Ensuring Docker network exists..."
try {
  $networkName = "orkhon-network"
  $inspectOutput = & docker network inspect $networkName 2>&1
  if ($LASTEXITCODE -ne 0) {
    $errText = ($inspectOutput -join "`n").ToString()
    if ($errText -match "dockerDesktopLinuxEngine" -or
        $errText -match "open //./pipe" -or
        $errText -match "cannot connect to the Docker daemon" -or
        $errText -match "Is the docker daemon running") {
      Show-Err "Docker engine not reachable. Docker Desktop daemon may be stopped."
      Show-Info "Start Docker Desktop, wait for it to initialize, then rerun this script."
      exit 2
    }
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
  Show-Err "Failed to ensure Docker network: $($_.Exception.Message)"
  Show-Info "Hint: Verify Docker Desktop is running."
  exit 1
}

# Step 3: Start Toolbox + Jaeger stack
Show-Step "Step 3/6: Starting GenAI Toolbox Stack (Docker)..."
try {
  Set-Location $ToolboxPath

  # Ensure .env exists
  $toolboxEnv = Join-Path $ToolboxPath ".env"
  if (-not (Test-Path $toolboxEnv)) {
    Show-Info "Toolbox .env not found at: $toolboxEnv"
    Show-Info "Creating minimal .env (edit to add real secrets)..."
    @"
# Auto-generated by quick-start.ps1
OTEL_SERVICE_NAME=orkhon-toolbox
# DNB keys (optional). Set real values as needed.
DNB_SUBSCRIPTION_KEY_DEV=
DNB_SUBSCRIPTION_KEY_PROD=
DNB_SUBSCRIPTION_NAME_DEV=
DNB_SUBSCRIPTION_NAME_PROD=
"@ | Out-File -FilePath $toolboxEnv -Encoding utf8 -Force
    Show-Ok "Created $toolboxEnv"
  }

  # Select compose file
  $composeCandidates = @("docker-compose.dev.yml", "docker-compose.yml")
  $ComposeFilePath = $null
  foreach ($candidate in $composeCandidates) {
    $candidatePath = Join-Path $ToolboxPath $candidate
    if (Test-Path $candidatePath) {
      $ComposeFilePath = $candidatePath
      break
    }
  }
  if (-not $ComposeFilePath) {
    throw "No compose file found (looked for docker-compose.dev.yml, docker-compose.yml)."
  }
  $composeFileName = Split-Path $ComposeFilePath -Leaf
  Show-Info ("Using compose file: {0}" -f $composeFileName)

  # Ensure critical ports are free
  $CriticalPorts = @(
    @{ Port = 4318; Service = "Jaeger OTLP" },
    @{ Port = 5000; Service = "GenAI Toolbox" },
    @{ Port = 16686; Service = "Jaeger UI" }
  )
  Ensure-CriticalPortsFree -PortInfoList $CriticalPorts

  # Determine current containers
  $runningContainers = & docker ps --filter "name=orkhon-" --format "{{.Names}}" 2>&1

  if ($ForceRecreate) {
    Show-Info "Force recreating containers..."
    & docker-compose -f $ComposeFilePath down --remove-orphans
    & docker-compose -f $ComposeFilePath up -d --force-recreate
    if ($LASTEXITCODE -ne 0) { throw "Failed to recreate containers." }
    Show-Ok "Containers recreated successfully"
  } elseif ($RestartToolbox -or ($runningContainers -and $runningContainers -like "*genai-toolbox*")) {
    Show-Info "Restarting existing containers to load latest configuration..."
    & docker-compose -f $ComposeFilePath restart
    if ($LASTEXITCODE -ne 0) { throw "Failed to restart containers." }
    Show-Ok "Containers restarted successfully"
  } else {
    Show-Info "Starting fresh containers..."
    & docker-compose -f $ComposeFilePath up -d
    if ($LASTEXITCODE -ne 0) { throw "Failed to start containers." }
    Show-Ok "Containers started successfully"
  }

  Show-Info "Checking container status..."
  $containers = & docker ps --filter "name=orkhon-" --format "table {{.Names}}\t{{.Status}}" 2>&1
  Write-Host $containers -ForegroundColor Yellow

  # Service readiness checks
  Show-Info "Waiting for services to be ready (up to $WaitSeconds seconds)..."
  $services = @{}
  $services["Toolbox"] = @{
    Url = "http://localhost:5000"
    Probes = @("health", "api/toolsets", "api/toolset/", "ui/")
    Ready = $false
  }
  $services["Jaeger"] = @{
    Url = "http://localhost:16686"
    Probes = @("", "search")
    Ready = $false
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
              Show-Ok ("{0} is ready at: {1}" -f $serviceName, $url)
              break
            }
          } catch { }
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
  Write-Host ""

  $anyFailed = $false
  foreach ($serviceName in $services.Keys) {
    if (-not $services[$serviceName].Ready) {
      Show-Err ("{0} did not become ready after {1} seconds" -f $serviceName, $WaitSeconds)
      Show-Info ("Check logs: docker-compose -f {0} logs {1}" -f $composeFileName, $serviceName.ToLower())
      $anyFailed = $true
    }
  }
  if ($anyFailed) {
    Show-Info "Some services may still be starting. Recent logs:"
    Write-Host ("  docker-compose -f {0} logs --tail=50" -f $composeFileName) -ForegroundColor Yellow
    $continue = Read-Host "`nContinue anyway? (y/n)"
    if ($continue -ne "y") { exit 1 }
  } else {
    Show-Ok "All services are ready!"
  }
} catch {
  Show-Err "Failed to start GenAI Toolbox Stack: $($_.Exception.Message)"
  Show-Info "Ensure Docker Desktop is running."
  Show-Info ("Try: docker-compose -f {0} logs" -f $composeFileName)
  exit 1
}

# Step 4: Open UIs
if ($OpenUIs) {
  Show-Step "Step 4/6: Opening Web UIs..."
  try {
    if ($services.ContainsKey("Toolbox") -and $services["Toolbox"].Ready) {
      Show-Info "Opening GenAI Toolbox UI..."
      Start-Process "http://localhost:5000/ui/"
      Start-Sleep -Seconds 1
    }
    if ($services.ContainsKey("Jaeger") -and $services["Jaeger"].Ready) {
      Show-Info "Opening Jaeger Tracing UI..."
      Start-Process "http://localhost:16686"
      Start-Sleep -Seconds 1
    }
    Show-Ok "Web UIs opened in browser"
    Show-Info "ADK Web UI will open automatically once the server starts..."
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

# Step 5: Verify virtual environment
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

# Port utilities
function Test-PortFree {
  param([int]$Port)
  try {
    $client = New-Object System.Net.Sockets.TcpClient
    $client.Connect('localhost', $Port)
    $client.Close()
    return $false
  } catch { return $true }
}

function Resolve-PortConflict {
  param(
    [int]$Port,
    [string]$ServiceName
  )

  Write-Host ("  [WARN] Port {0} in use. Attempting to free for {1}..." -f $Port, $ServiceName) -ForegroundColor Yellow
  $containers = & docker ps --filter ("publish={0}" -f $Port) --format "{{.ID}} {{.Names}}" 2>$null
  if ($LASTEXITCODE -ne 0 -or -not $containers) {
    Write-Host ("  [WARN] Port {0} held by a non-docker process or docker query failed. Please free it manually and rerun." -f $Port) -ForegroundColor Yellow
    return $false
  }

  $resolved = $false
  foreach ($entry in $containers) {
    $parts = $entry -split '\s+', 2
    $id = $parts[0]
    $name = if ($parts.Length -gt 1) { $parts[1] } else { $id }
    Write-Host ("  [INFO] Stopping container '{0}' holding port {1}..." -f $name, $Port)
    try {
      & docker stop $id | Out-Null
      & docker rm $id | Out-Null
      $resolved = $true
    } catch {
      Write-Host ("  [ERR] Failed to stop/remove container {0}: {1}" -f $name, $_.Exception.Message) -ForegroundColor Red
      return $false
    }
  }

  if ($resolved) {
    Write-Host ("  [OK]  Port {0} freed for {1}" -f $Port, $ServiceName)
  }
  return $resolved
}

function Ensure-CriticalPortsFree {
  param([array]$PortInfoList)

  foreach ($info in $PortInfoList) {
    $port = [int]$info.Port
    $service = $info.Service
    if (-not (Test-PortFree -Port $port)) {
      Write-Host ("  [INFO] Port {0} in use ({1}). Attempting to free existing binding..." -f $port, $service) -ForegroundColor Yellow
      $null = Resolve-PortConflict -Port $port -ServiceName $service
      if (-not (Test-PortFree -Port $port)) {
        throw ("Port {0} remains busy after cleanup. Free the port manually and rerun the quick-start script." -f $port)
      }
    }
  }
}

function Ensure-GoogleNamespaceClean {
  param([string]$PythonExe)
  try {
    & $PythonExe -m pip show google *> $null
    if ($LASTEXITCODE -eq 0) {
      Show-Info "Detected top-level 'google' package which can block 'google.adk'."
      $resp = Read-Host "Uninstall 'google' now? (y/N)"
      if ($resp -eq "y") {
        & $PythonExe -m pip uninstall -y google
      } else {
        Show-Info "Continuing, but 'google' may prevent 'google.adk' imports."
      }
    }
  } catch { }
}

function Test-AdkInstalled {
  param([string]$PythonExe)
  & $PythonExe -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('google.adk') else 1)"
  return ($LASTEXITCODE -eq 0)
}

function Ensure-AdkInstalled {
  param([string]$PythonExe, [string]$ProjectRoot)
  if (Test-AdkInstalled -PythonExe $PythonExe) {
    return
  }
  # Prefer local dev install if adk-python sibling exists
  $parent = Split-Path $ProjectRoot -Parent
  $adkDev = Join-Path $parent "adk-python"
  Ensure-GoogleNamespaceClean -PythonExe $PythonExe
  if (Test-Path $adkDev) {
    Show-Info "Installing google-adk from local source: $adkDev"
    & $PythonExe -m pip install -e "$adkDev"
  } else {
    Show-Info "Installing google-adk from PyPI"
    & $PythonExe -m pip install google-adk
  }
  if (-not (Test-AdkInstalled -PythonExe $PythonExe)) {
    throw "google-adk is not importable after installation. Check for conflicting 'google' package."
  }
}

function Start-AdkWeb {
  param(
    [string]$PythonExe,
    [string]$AgentsPath,
    [int]$Port
  )
  try {
    & adk web --reload_agents --host=0.0.0.0 --port=$Port $AgentsPath
  } catch {
    Show-Info "Falling back to python -m google.adk.cli.cli_tools_click web"
    & $PythonExe -m google.adk.cli.cli_tools_click web --reload_agents --host=0.0.0.0 --port=$Port $AgentsPath
  }
}

# Step 6: Start ADK Web
Show-Step "Step 6/6: Starting ADK Web Server..."
try {
  Set-Location $ProjectRoot

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

  if (-not (Test-PortFree -Port 8000)) {
    Show-Err "Port 8000 is already in use!"
    Show-Info "Find process: netstat -ano | findstr :8000"
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

  if ($OpenUIs) {
    Show-Info "ADK Web UI will open in 5 seconds..."
    Start-Job -ScriptBlock {
      Start-Sleep -Seconds 5
      Start-Process "http://localhost:8000"
    } | Out-Null
  }

  & $VenvActivate
  $pythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
  $gemini = [System.Environment]::GetEnvironmentVariable('GEMINI_API_KEY', 'Process')
  $google = [System.Environment]::GetEnvironmentVariable('GOOGLE_API_KEY', 'Process')
  if ($gemini -and [string]::IsNullOrWhiteSpace($google)) {
    [System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', $gemini, 'Process')
    Show-Info "Mirrored GEMINI_API_KEY -> GOOGLE_API_KEY for this session"
  }

  # NEW: Ensure ADK is installed and importable
  Ensure-AdkInstalled -PythonExe $pythonExe -ProjectRoot $ProjectRoot

  # Start (with fallback)
  Start-AdkWeb -PythonExe $pythonExe -AgentsPath "$ProjectRoot\backend\adk\agents" -Port 8000
} catch {
  Show-Err "Failed to start ADK Web: $($_.Exception.Message)"
  Show-Info "Check the error messages above."
  Show-Info "Try running manually: adk web backend\adk\agents"
  exit 1
}

# Shutdown note
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
Write-Host ("  docker-compose -f {0} down" -f $composeFileName) -ForegroundColor Cyan
Write-Host ""
Show-Info "To stop Docker services only:"
Write-Host "  docker stop orkhon-genai-toolbox-mcp orkhon-jaeger" -ForegroundColor Cyan