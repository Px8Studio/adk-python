# ADK Web UI Launcher with GenAI Toolbox Integration
# This script starts the ADK web interface with GenAI Toolbox tools

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ADK Web UI + GenAI Toolbox Launcher  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if GenAI Toolbox is running
Write-Host "Checking GenAI Toolbox status..." -ForegroundColor Yellow

$toolboxReady = $false
try {
  $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET -TimeoutSec 5 -UseBasicParsing
  if ($response.StatusCode -eq 200) {
    $toolboxReady = $true
  }
} catch {
  Write-Host "   Warning: GenAI Toolbox not responding at http://localhost:5000" -ForegroundColor Yellow
}

if ($toolboxReady) {
  Write-Host "   checkmark GenAI Toolbox is running" -ForegroundColor Green
  Write-Host ""
  
  # Verify Python environment
  Write-Host "Verifying Python environment..." -ForegroundColor Yellow
  
  $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
  if (-not $pythonCmd) {
    Write-Host "   X Python not found in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure Python is installed and in your PATH" -ForegroundColor Red
    exit 1
  }
  
  Write-Host "   checkmark Python found: $($pythonCmd.Source)" -ForegroundColor Green
  
  # Check if ADK is installed
  $adkInstalled = python -m pip show google-adk 2>$null
  if (-not $adkInstalled) {
    Write-Host "   Warning: google-adk not found" -ForegroundColor Yellow
    Write-Host "   Installing google-adk..." -ForegroundColor Yellow
    python -m pip install google-adk
  } else {
    Write-Host "   checkmark ADK installed" -ForegroundColor Green
  }
} else {
  Write-Host ""
  Write-Host "GenAI Toolbox is not running. Starting it now..." -ForegroundColor Yellow
  Write-Host ""
  
  # Start GenAI Toolbox in a new window
  $toolboxPath = Join-Path $PSScriptRoot "..\toolbox"
  
  if (-not (Test-Path $toolboxPath)) {
    Write-Host "   X GenAI Toolbox directory not found at: $toolboxPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure GenAI Toolbox is set up in the backend/toolbox directory" -ForegroundColor Red
    exit 1
  }
  
  Write-Host "   Starting GenAI Toolbox server..." -ForegroundColor Yellow
  
  $toolboxScript = @"
Write-Host "Starting GenAI Toolbox..." -ForegroundColor Cyan
Set-Location "$toolboxPath"
python -m toolbox_core.server
"@
  
  $tempToolboxScript = [System.IO.Path]::GetTempFileName() + ".ps1"
  $toolboxScript | Out-File -FilePath $tempToolboxScript -Encoding UTF8
  
  Start-Process powershell -ArgumentList "-NoExit", "-File", $tempToolboxScript
  
  Write-Host "   checkmark GenAI Toolbox starting in new window" -ForegroundColor Green
  Write-Host ""
  Write-Host "Waiting for GenAI Toolbox to be ready..." -ForegroundColor Yellow
  
  $maxAttempts = 30
  $attempt = 0
  $toolboxReady = $false
  
  while ($attempt -lt $maxAttempts -and -not $toolboxReady) {
    Start-Sleep -Seconds 2
    $attempt++
    
    try {
      $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -Method GET -TimeoutSec 2 -UseBasicParsing
      if ($response.StatusCode -eq 200) {
        $toolboxReady = $true
        Write-Host "   checkmark GenAI Toolbox is ready!" -ForegroundColor Green
      }
    } catch {
      Write-Host "   Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
    }
  }
  
  if (-not $toolboxReady) {
    Write-Host ""
    Write-Host "   X GenAI Toolbox failed to start within timeout" -ForegroundColor Red
    Write-Host "   Please check the Toolbox window for errors" -ForegroundColor Red
    exit 1
  }
}

Write-Host ""
Write-Host "Starting ADK Web UI..." -ForegroundColor Yellow
Write-Host ""

# Navigate to the ADK agents directory
$agentsPath = Split-Path $PSScriptRoot -Parent
Set-Location $agentsPath

# Start ADK Web UI in a new window
$webUIScript = @"
Write-Host "ADK Web UI - GenAI Toolbox Integration" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the UI at: http://localhost:4200" -ForegroundColor Green
Write-Host ""
Set-Location "$agentsPath"
uv run adk web . --port 4200 --reload_agents
"@

$tempWebScript = [System.IO.Path]::GetTempFileName() + ".ps1"
$webUIScript | Out-File -FilePath $tempWebScript -Encoding UTF8

# Start Web UI in new window
Start-Process powershell -ArgumentList "-NoExit", "-File", $tempWebScript

Write-Host "   checkmark ADK Web UI starting in new window (http://localhost:4200)" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!                      " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services running:" -ForegroundColor White
Write-Host "  - GenAI Toolbox: http://localhost:5000" -ForegroundColor Gray
Write-Host "  - ADK Web UI:    http://localhost:4200" -ForegroundColor Gray
Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "  1. Select the 'adk' folder in the UI to interact with agents" -ForegroundColor Gray
Write-Host "  2. Agents can access GenAI Toolbox tools automatically" -ForegroundColor Gray
Write-Host "  3. Check the terminal windows for logs" -ForegroundColor Gray
Write-Host ""

# Wait a moment then open browser
Start-Sleep -Seconds 3
Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Process "http://localhost:4200"

Write-Host ""
Write-Host "Press any key to exit this window (services will continue running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")