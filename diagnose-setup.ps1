<#
  Orkhon Diagnostics Script (standalone)

  This script performs light preflight checks with no external dependencies
  and no custom helper functions, for maximum compatibility with
  Windows PowerShell 5.1.
#>

param(
  [switch]$SkipDiagnostics
)

$ErrorActionPreference = 'Stop'

Write-Host ""; Write-Host "==> Step 1/6: Running system diagnostics..." -ForegroundColor Cyan

if ($SkipDiagnostics) {
  Write-Host "[INFO] Skipping diagnostics due to flag." -ForegroundColor Yellow
  exit 0
}

try {
  # Determine project root based on script location if not provided
  if (-not $script:ProjectRoot) {
    $scriptDir = Split-Path -Parent $PSCommandPath
    $ProjectRoot = Resolve-Path (Join-Path $scriptDir '.')
  }
  Write-Host "[INFO] Project root: $ProjectRoot" -ForegroundColor Yellow

  # 1) Check Docker CLI presence
  $dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
  if ($null -ne $dockerCmd) {
    $dockerVersion = (& docker --version) 2>$null
    if ($LASTEXITCODE -eq 0 -and $dockerVersion) {
      Write-Host "[OK]  Docker CLI detected ($dockerVersion)" -ForegroundColor Green
    } else {
      Write-Host "[WARN] Docker CLI in PATH, but version check failed." -ForegroundColor Yellow
    }
  } else {
    Write-Host "[ERR] Docker not detected. Please install/start Docker Desktop." -ForegroundColor Red
  }

  # 2) Check Docker Compose file exists
  $composeFile = Join-Path $ProjectRoot 'backend\toolbox\docker-compose.dev.yml'
  if (Test-Path $composeFile) {
    Write-Host "[OK]  Found docker-compose.dev.yml" -ForegroundColor Green
  } else {
    Write-Host "[INFO] docker-compose.dev.yml not found at: $composeFile" -ForegroundColor Yellow
  }

  # 3) Check Python venv presence
  $venvActivate = Join-Path $ProjectRoot '.venv\Scripts\Activate.ps1'
  if (Test-Path $venvActivate) {
    Write-Host "[OK]  Python virtual environment detected" -ForegroundColor Green
  } else {
    Write-Host "[INFO] Venv not found. Run 'poetry install' or 'python -m venv .venv'" -ForegroundColor Yellow
  }

  # 4) Network ports availability
  function Test-PortFree {
    param([int]$Port)
    try {
      $client = New-Object System.Net.Sockets.TcpClient
      $client.Connect('localhost', $Port)
      $client.Close()
      return $false # in-use
    } catch { return $true } # free
  }

  # Check essential ports
  $portsToCheck = @{
    8000 = "ADK Web Server"
    5000 = "GenAI Toolbox"
    16686 = "Jaeger UI"
    4318 = "Jaeger OTLP"
  }

  foreach ($port in $portsToCheck.Keys) {
    $portFree = Test-PortFree -Port $port
    $service = $portsToCheck[$port]
    if ($portFree) {
      Write-Host "[OK]  Port $port available ($service)" -ForegroundColor Green
    } else {
      Write-Host "[INFO] Port $port in use ($service)" -ForegroundColor Yellow
    }
  }

  # 5) Check Docker network
  $networkName = "orkhon-network"
  try {
    $null = & docker network inspect $networkName 2>&1
    if ($LASTEXITCODE -eq 0) {
      Write-Host "[OK]  Docker network exists: $networkName" -ForegroundColor Green
    } else {
      Write-Host "[INFO] Docker network not found: $networkName (will be created)" -ForegroundColor Yellow
    }
  } catch {
    Write-Host "[INFO] Could not check Docker network (Docker may not be running)" -ForegroundColor Yellow
  }

  Write-Host "[OK]  Diagnostics completed successfully" -ForegroundColor Green
  exit 0
} catch {
  Write-Host "[ERR] Diagnostics failed: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}
