#!/usr/bin/env pwsh
# Quick Start ADK Web - Simple launcher from Orkhon root
# Usage: .\quick-start-adk-web.ps1

param(
    [switch]$Help
)

if ($Help) {
    Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                    ADK Web Quick Start                         ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
  .\quick-start-adk-web.ps1          Start all services
  .\quick-start-adk-web.ps1 -Help    Show this help

WHAT IT DOES:
  1. Starts GenAI Toolbox (Docker)
  2. Starts ADK API Server (Python FastAPI)
  3. Starts ADK Web UI (Angular)
  4. Opens browser to http://localhost:4200

SERVICES:
  • Toolbox:    http://localhost:5000
  • API Server: http://localhost:8000  
  • Web UI:     http://localhost:4200
  • Jaeger:     http://localhost:16686

TO STOP:
  .\backend\adk\stop-adk-web.ps1
  OR press Ctrl+C in all terminal windows

TROUBLESHOOTING:
  .\backend\adk\diagnose-setup.ps1

MORE INFO:
  See ADK_WEB_MANAGEMENT.md for detailed guide

"@
    exit 0
}

$ErrorActionPreference = "Stop"

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║                    🚀 ADK Web Quick Start                      ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Initialize tracking
$issues = @()
$warnings = @()
$ProjectRoot = Get-Location

# Check if we're in the right directory
if (-not (Test-Path "backend\adk\agents")) {
    Write-Host "❌ Error: Must run from Orkhon project root" -ForegroundColor Red
    Write-Host "   Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "   Expected: C:\Users\rjjaf\_Projects\orkhon" -ForegroundColor Yellow
    exit 1
}

Write-Host "📍 Running from: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# Pre-flight checks
Write-Host "Running pre-flight checks..." -ForegroundColor Cyan
Write-Host ""

# [1/4] Check virtual environment
Write-Host "[1/4] Checking Poetry virtual environment..." -ForegroundColor Cyan
$VenvPath = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"

if (Test-Path $VenvPath) {
  Write-Host "   ✓ Virtual environment found: $VenvPath" -ForegroundColor Green
  
  if (Test-Path $VenvPython) {
    Write-Host "   ✓ Python executable found" -ForegroundColor Green
    
    try {
      $pyVersion = & $VenvPython --version 2>&1
      if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Python version: $pyVersion" -ForegroundColor Green
      }
    } catch {
      Write-Host "   ✗ Python in venv not working" -ForegroundColor Red
      $issues += "Virtual environment Python not functional"
    }
  } else {
    Write-Host "   ✗ Python executable not found in venv" -ForegroundColor Red
    $issues += "Virtual environment incomplete"
  }
} else {
  Write-Host "   ✗ Virtual environment not found at: $VenvPath" -ForegroundColor Red
  Write-Host "     Run 'poetry install' in: $ProjectRoot" -ForegroundColor Yellow
  $issues += "Virtual environment not created"
}

# [2/4] Check GenAI Toolbox
Write-Host "`n[2/4] Checking GenAI Toolbox..." -ForegroundColor Cyan
$toolboxRunning = $false
try {
  $response = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 2 -ErrorAction Stop
  Write-Host "   ✓ GenAI Toolbox is running" -ForegroundColor Green
  $toolboxRunning = $true
} catch {
  Write-Host "   ✗ GenAI Toolbox not responding on port 5000" -ForegroundColor Yellow
  Write-Host "   Attempting to start GenAI Toolbox..." -ForegroundColor Cyan
  
  # Try to start toolbox using Docker
  $toolboxDir = Join-Path $ProjectRoot "backend\toolbox"
  if (Test-Path $toolboxDir) {
    Push-Location $toolboxDir
    try {
      docker-compose -f docker-compose.dev.yml up -d 2>&1 | Out-Null
      
      # Wait for toolbox to start
      $maxWait = 30
      $waited = 0
      while ($waited -lt $maxWait) {
        try {
          $null = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 1 -ErrorAction Stop
          Write-Host "   ✓ GenAI Toolbox started successfully" -ForegroundColor Green
          $toolboxRunning = $true
          break
        } catch {
          Start-Sleep -Seconds 2
          $waited += 2
        }
      }
      
      if (-not $toolboxRunning) {
        Write-Host "   ⚠ GenAI Toolbox may still be starting..." -ForegroundColor Yellow
      }
    } catch {
      Write-Host "   ✗ Failed to start GenAI Toolbox: $($_.Exception.Message)" -ForegroundColor Red
    } finally {
      Pop-Location
    }
  }
}

# [3/4] Check Docker
Write-Host "`n[3/4] Checking Docker..." -ForegroundColor Cyan
try {
  $null = docker --version 2>&1
  if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Docker is available" -ForegroundColor Green
  } else {
    Write-Host "   ✗ Docker command failed" -ForegroundColor Red
    $issues += "Docker not working properly"
  }
} catch {
  Write-Host "   ✗ Docker not found" -ForegroundColor Red
  $issues += "Docker not installed"
}

# [4/4] Check project structure
Write-Host "`n[4/4] Checking project structure..." -ForegroundColor Cyan

$requiredPaths = @(
  @{Path="pyproject.toml"; Type="Poetry config"},
  @{Path="backend\adk"; Type="ADK backend"},
  @{Path="backend\toolbox"; Type="Toolbox config"}
)

foreach ($item in $requiredPaths) {
  $fullPath = Join-Path $ProjectRoot $item.Path
  if (Test-Path $fullPath) {
    Write-Host "   ✓ $($item.Type) found" -ForegroundColor Green
  } else {
    Write-Host "   ✗ $($item.Type) missing: $($item.Path)" -ForegroundColor Red
    $issues += "$($item.Type) not found"
  }
}

Write-Host ""

# Check for blocking issues
if ($issues.Count -gt 0) {
  Write-Host "❌ Cannot start: Found $($issues.Count) issue(s)" -ForegroundColor Red
  foreach ($issue in $issues) {
    Write-Host "   • $issue" -ForegroundColor Red
  }
  Write-Host "`nRun diagnostics for more info:" -ForegroundColor Yellow
  Write-Host "   .\backend\adk\diagnose-setup.ps1" -ForegroundColor Cyan
  exit 1
}

# Show warnings but continue
if ($warnings.Count -gt 0) {
  Write-Host "⚠ Found $($warnings.Count) warning(s):" -ForegroundColor Yellow
  foreach ($warning in $warnings) {
    Write-Host "   • $warning" -ForegroundColor Yellow
  }
  Write-Host ""
}

Write-Host "✓ All pre-flight checks passed!" -ForegroundColor Green
Write-Host ""

# Step 1: Start Toolbox
Write-Host "Step 1/3: Starting GenAI Toolbox..." -ForegroundColor Cyan
Write-Host "         (This may take 20-30 seconds)" -ForegroundColor Gray
Write-Host ""

$toolboxDir = "backend\toolbox"
Set-Location $toolboxDir

try {
    $null = docker-compose -f docker-compose.dev.yml up -d 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker compose failed"
    }
} catch {
    Write-Host "❌ Failed to start Toolbox" -ForegroundColor Red
    Write-Host "   Run: docker-compose -f docker-compose.dev.yml up -d" -ForegroundColor Yellow
    Set-Location ..\..
    exit 1
}

Set-Location ..\..

# Wait for Toolbox to be ready
Write-Host "   Waiting for Toolbox to be ready..." -ForegroundColor Gray
$attempts = 0
$maxAttempts = 30
$ready = $false

while ($attempts -lt $maxAttempts -and -not $ready) {
    $attempts++
    Start-Sleep -Seconds 1
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 1 -ErrorAction Stop
        $ready = $true
    } catch {
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
}

if ($ready) {
    Write-Host ""
    Write-Host "   ✓ Toolbox ready!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "   ⚠ Toolbox may still be starting..." -ForegroundColor Yellow
}
Write-Host ""

# Step 2: Start ADK API Server
Write-Host "Step 2/3: Starting ADK API Server..." -ForegroundColor Cyan
Write-Host "         (Opening in new window)" -ForegroundColor Gray
Write-Host ""

$apiServerScript = @"
cd C:\Users\rjjaf\_Projects\orkhon
Write-Host '╔════════════════════════════════════════════════════════════════╗' -ForegroundColor Cyan
Write-Host '║              ADK API Server (Keep this window open)           ║' -ForegroundColor Cyan
Write-Host '╚════════════════════════════════════════════════════════════════╝' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Starting ADK API Server...' -ForegroundColor Yellow
Write-Host ''
$webUiScript = @"
# ADK Web UI Startup Script
`$ProjectRoot = "$ProjectRoot"
`$VenvPython = "$VenvPython"

Write-Host '╔════════════════════════════════════════════════════════════════╗' -ForegroundColor Cyan
Write-Host '║               ADK Web UI (Keep this window open)              ║' -ForegroundColor Cyan
Write-Host '╚════════════════════════════════════════════════════════════════╝' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Starting ADK Web UI...' -ForegroundColor Yellow
Write-Host ''
Set-Location "`$ProjectRoot\backend\adk"
& `$VenvPython -m google.adk.cli.cli_tools_click web --port 8080
"@

$webUiScriptPath = "backend\adk\.start-web-ui.ps1"
$webUiScript | Out-File -FilePath $webUiScriptPath -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-File", $webUiScriptPath

# Step 3: Start ADK Web UI
Write-Host "Step 3/3: Starting ADK Web UI..." -ForegroundColor Cyan
Write-Host "         (Opening in new window)" -ForegroundColor Gray
Write-Host ""

$webUiScript = @"
cd C:\Users\rjjaf\_Projects\adk-web
Write-Host '╔════════════════════════════════════════════════════════════════╗' -ForegroundColor Cyan
Write-Host '║               ADK Web UI (Keep this window open)              ║' -ForegroundColor Cyan
Write-Host '╚════════════════════════════════════════════════════════════════╝' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Starting ADK Web UI...' -ForegroundColor Yellow
Write-Host ''
npm run serve -- --backend=http://localhost:8000
"@

$webUiScriptPath = "backend\adk\.start-web-ui.ps1"
$webUiScript | Out-File -FilePath $webUiScriptPath -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-File", $webUiScriptPath

Write-Host "   ✓ Web UI starting in new window" -ForegroundColor Green
Write-Host "   (Wait for Angular compilation to complete)" -ForegroundColor Gray
Write-Host ""

# Final instructions
Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║                      ✅ Services Starting!                      ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green

Write-Host "Two new windows opened:" -ForegroundColor Cyan
Write-Host "  1. ADK API Server (Python FastAPI)" -ForegroundColor White
Write-Host "  2. ADK Web UI (Angular)" -ForegroundColor White
Write-Host ""

Write-Host "Wait 30-60 seconds for compilation, then visit:" -ForegroundColor Yellow
Write-Host "  👉 http://localhost:4200" -ForegroundColor Cyan -BackgroundColor Black
Write-Host ""

Write-Host "Other Services:" -ForegroundColor Cyan
Write-Host "  • Toolbox UI:  http://localhost:5000/ui/" -ForegroundColor White
Write-Host "  • API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host "  • Jaeger:      http://localhost:16686" -ForegroundColor White
Write-Host ""

Write-Host "To stop all services:" -ForegroundColor Cyan
Write-Host "  .\backend\adk\stop-adk-web.ps1" -ForegroundColor Yellow
Write-Host ""

# Wait a bit then open browser
Start-Sleep -Seconds 10
Write-Host "Opening browser..." -ForegroundColor Gray
Start-Process "http://localhost:4200"

Write-Host ""
Write-Host "✨ Happy agent building!" -ForegroundColor Green
Write-Host ""
