#!/usr/bin/env pwsh
# Quick Start ADK Web - Simple launcher from Orkhon root
# Usage: .\quick-start-adk-web.ps1

#requires -Version 5.1

[CmdletBinding()]
param(
    [switch]$Help
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

#region Constants
$script:PROJECT_ROOT = Get-Location
$script:VENV_PATH = Join-Path $PROJECT_ROOT ".venv"
$script:VENV_PYTHON = Join-Path $VENV_PATH "Scripts\python.exe"
$script:TOOLBOX_DIR = Join-Path $PROJECT_ROOT "backend\toolbox"
$script:ADK_DIR = Join-Path $PROJECT_ROOT "backend\adk"

$script:PORTS = @{
    Toolbox = 5000
    ApiServer = 8000
    WebUI = 4200
    Jaeger = 16686
}

$script:TIMEOUTS = @{
    ToolboxStartup = 30
    ApiServerStartup = 10
}
#endregion

#region Helper Functions
function Show-Help {
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
    • Toolbox:    http://localhost:$($PORTS.Toolbox)
    • API Server: http://localhost:$($PORTS.ApiServer)
    • Web UI:     http://localhost:$($PORTS.WebUI)
    • Jaeger:     http://localhost:$($PORTS.Jaeger)

TO STOP:
    .\backend\adk\stop-adk-web.ps1
    OR press Ctrl+C in all terminal windows

TROUBLESHOOTING:
    .\backend\adk\diagnose-setup.ps1

MORE INFO:
    See ADK_WEB_MANAGEMENT.md for detailed guide

"@
}

function Show-Header {
    param([string]$Message)
    Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║  $($Message.PadRight(60))  ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan
}

function Test-ProjectRoot {
    if (-not (Test-Path (Join-Path $PROJECT_ROOT "backend\adk\agents"))) {
        Write-Host "❌ Error: Must run from Orkhon project root" -ForegroundColor Red
        Write-Host "   Current directory: $PROJECT_ROOT" -ForegroundColor Yellow
        Write-Host "   Expected structure: backend\adk\agents" -ForegroundColor Yellow
        return $false
    }
    Write-Host "📍 Running from: $PROJECT_ROOT" -ForegroundColor Green
    Write-Host ""
    return $true
}

function Test-VirtualEnvironment {
    Write-Host "[1/4] Checking Poetry virtual environment..." -ForegroundColor Cyan
    
    if (-not (Test-Path $VENV_PATH)) {
        Write-Host "   ✗ Virtual environment not found at: $VENV_PATH" -ForegroundColor Red
        Write-Host "     Run 'poetry install' in: $PROJECT_ROOT" -ForegroundColor Yellow
        return $false
    }
    Write-Host "   ✓ Virtual environment found: $VENV_PATH" -ForegroundColor Green
    
    if (-not (Test-Path $VENV_PYTHON)) {
        Write-Host "   ✗ Python executable not found in venv" -ForegroundColor Red
        return $false
    }
    Write-Host "   ✓ Python executable found" -ForegroundColor Green
    
    try {
        $pyVersion = & $VENV_PYTHON --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✓ Python version: $pyVersion" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "   ✗ Python in venv not working: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    return $false
}

function Test-ServiceHealth {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 2
    )
    
    try {
        $null = Invoke-RestMethod -Uri $Url -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Start-ToolboxService {
    Write-Host "`n[2/4] Checking GenAI Toolbox..." -ForegroundColor Cyan
    
    $healthUrl = "http://localhost:$($PORTS.Toolbox)/health"
    
    if (Test-ServiceHealth -Url $healthUrl) {
        Write-Host "   ✓ GenAI Toolbox is already running" -ForegroundColor Green
        return $true
    }
    
    Write-Host "   ✗ GenAI Toolbox not responding" -ForegroundColor Yellow
    Write-Host "   Attempting to start GenAI Toolbox..." -ForegroundColor Cyan
    
    if (-not (Test-Path $TOOLBOX_DIR)) {
        Write-Host "   ✗ Toolbox directory not found: $TOOLBOX_DIR" -ForegroundColor Red
        return $false
    }
    
    Push-Location $TOOLBOX_DIR
    try {
        $null = docker-compose -f docker-compose.dev.yml up -d 2>&1
        
        # Wait for service to become healthy
        $maxWait = $TIMEOUTS.ToolboxStartup
        $waited = 0
        while ($waited -lt $maxWait) {
            if (Test-ServiceHealth -Url $healthUrl -TimeoutSeconds 1) {
                Write-Host "   ✓ GenAI Toolbox started successfully" -ForegroundColor Green
                return $true
            }
            Start-Sleep -Seconds 2
            $waited += 2
        }
        
        Write-Host "   ⚠ GenAI Toolbox may still be starting..." -ForegroundColor Yellow
        return $true
    } catch {
        Write-Host "   ✗ Failed to start GenAI Toolbox: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    } finally {
        Pop-Location
    }
}

function Test-Docker {
    Write-Host "`n[3/4] Checking Docker..." -ForegroundColor Cyan
    
    try {
        $null = docker --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✓ Docker is available" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "   ✗ Docker not found" -ForegroundColor Red
        return $false
    }
    
    Write-Host "   ✗ Docker command failed" -ForegroundColor Red
    return $false
}

function Test-ProjectStructure {
    Write-Host "`n[4/4] Checking project structure..." -ForegroundColor Cyan
    
    $requiredPaths = @(
        @{Path = "pyproject.toml"; Type = "Poetry config"}
        @{Path = "backend\adk"; Type = "ADK backend"}
        @{Path = "backend\toolbox"; Type = "Toolbox config"}
    )
    
    $allFound = $true
    foreach ($item in $requiredPaths) {
        $fullPath = Join-Path $PROJECT_ROOT $item.Path
        if (Test-Path $fullPath) {
            Write-Host "   ✓ $($item.Type) found" -ForegroundColor Green
        } else {
            Write-Host "   ✗ $($item.Type) missing: $($item.Path)" -ForegroundColor Red
            $allFound = $false
        }
    }
    
    return $allFound
}

function Invoke-PreflightChecks {
    Write-Host "Running pre-flight checks..." -ForegroundColor Cyan
    Write-Host ""
    
    $checks = @(
        @{Name = "Virtual Environment"; Test = { Test-VirtualEnvironment }}
        @{Name = "Toolbox Service"; Test = { Start-ToolboxService }}
        @{Name = "Docker"; Test = { Test-Docker }}
        @{Name = "Project Structure"; Test = { Test-ProjectStructure }}
    )
    
    $failed = @()
    foreach ($check in $checks) {
        if (-not (& $check.Test)) {
            $failed += $check.Name
        }
    }
    
    Write-Host ""
    
    if ($failed.Count -gt 0) {
        Write-Host "❌ Cannot start: Found $($failed.Count) issue(s)" -ForegroundColor Red
        foreach ($issue in $failed) {
            Write-Host "   • $issue" -ForegroundColor Red
        }
        Write-Host "`nRun diagnostics for more info:" -ForegroundColor Yellow
        Write-Host "   .\backend\adk\diagnose-setup.ps1" -ForegroundColor Cyan
        return $false
    }
    
    Write-Host "✓ All pre-flight checks passed!" -ForegroundColor Green
    Write-Host ""
    return $true
}

function Wait-ForToolboxReady {
    Write-Host "   Waiting for Toolbox to be ready..." -ForegroundColor Gray
    
    $healthUrl = "http://localhost:$($PORTS.Toolbox)/health"
    $maxAttempts = $TIMEOUTS.ToolboxStartup
    
    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
        if (Test-ServiceHealth -Url $healthUrl -TimeoutSeconds 1) {
            Write-Host ""
            Write-Host "   ✓ Toolbox ready!" -ForegroundColor Green
            return $true
        }
        Write-Host "." -NoNewline -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
    
    Write-Host ""
    Write-Host "   ⚠ Toolbox may still be starting..." -ForegroundColor Yellow
    return $false
}

function Start-ApiServer {
    Write-Host "Step 2/3: Starting ADK API Server..." -ForegroundColor Cyan
    Write-Host "         (Opening in new window)" -ForegroundColor Gray
    Write-Host ""
    
    $apiServerScript = @"
Set-Location '$PROJECT_ROOT'
Write-Host '╔════════════════════════════════════════════════════════════════╗' -ForegroundColor Cyan
Write-Host '║              ADK API Server (Keep this window open)           ║' -ForegroundColor Cyan
Write-Host '╚════════════════════════════════════════════════════════════════╝' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Starting ADK API Server...' -ForegroundColor Yellow
Write-Host ''
Set-Location '$ADK_DIR'
& '$VENV_PYTHON' -m google.adk.cli.cli_tools_click web --port $($PORTS.ApiServer)
"@
    
    $scriptPath = Join-Path $ADK_DIR ".start-api-server.ps1"
    $apiServerScript | Out-File -FilePath $scriptPath -Encoding UTF8
    
    Start-Process powershell -ArgumentList "-NoExit", "-File", $scriptPath
    
    Write-Host "   ✓ API Server starting in new window" -ForegroundColor Green
    Write-Host ""
}

function Start-WebUI {
    Write-Host "Step 3/3: Starting ADK Web UI..." -ForegroundColor Cyan
    Write-Host "         (Opening in new window)" -ForegroundColor Gray
    Write-Host ""
    
    $webUiScript = @"
Set-Location 'C:\Users\rjjaf\_Projects\adk-web'
Write-Host '╔════════════════════════════════════════════════════════════════╗' -ForegroundColor Cyan
Write-Host '║               ADK Web UI (Keep this window open)              ║' -ForegroundColor Cyan
Write-Host '╚════════════════════════════════════════════════════════════════╝' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Starting ADK Web UI...' -ForegroundColor Yellow
Write-Host ''
npm run serve -- --backend=http://localhost:$($PORTS.ApiServer)
"@
    
    $scriptPath = Join-Path $ADK_DIR ".start-web-ui.ps1"
    $webUiScript | Out-File -FilePath $scriptPath -Encoding UTF8
    
    Start-Process powershell -ArgumentList "-NoExit", "-File", $scriptPath
    
    Write-Host "   ✓ Web UI starting in new window" -ForegroundColor Green
    Write-Host "   (Wait for Angular compilation to complete)" -ForegroundColor Gray
    Write-Host ""
}

function Show-CompletionMessage {
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
    Write-Host "  👉 http://localhost:$($PORTS.WebUI)" -ForegroundColor Cyan -BackgroundColor Black
    Write-Host ""
    
    Write-Host "Other Services:" -ForegroundColor Cyan
    Write-Host "  • Toolbox UI:  http://localhost:$($PORTS.Toolbox)/ui/" -ForegroundColor White
    Write-Host "  • API Docs:    http://localhost:$($PORTS.ApiServer)/docs" -ForegroundColor White
    Write-Host "  • Jaeger:      http://localhost:$($PORTS.Jaeger)" -ForegroundColor White
    Write-Host ""
    
    Write-Host "To stop all services:" -ForegroundColor Cyan
    Write-Host "  .\backend\adk\stop-adk-web.ps1" -ForegroundColor Yellow
    Write-Host ""
}
#endregion

#region Main Execution
function Main {
    if ($Help) {
        Show-Help
        return
    }
    
    Show-Header "🚀 ADK Web Quick Start"
    
    if (-not (Test-ProjectRoot)) {
        exit 1
    }
    
    if (-not (Invoke-PreflightChecks)) {
        exit 1
    }
    
    # Step 1: Ensure Toolbox is running
    Write-Host "Step 1/3: Starting GenAI Toolbox..." -ForegroundColor Cyan
    Write-Host "         (This may take 20-30 seconds)" -ForegroundColor Gray
    Write-Host ""
    
    Wait-ForToolboxReady | Out-Null
    Write-Host ""
    
    # Step 2: Start API Server
    Start-ApiServer
    
    # Step 3: Start Web UI
    Start-WebUI
    
    # Show completion message
    Show-CompletionMessage
    
    # Wait and open browser
    Start-Sleep -Seconds 10
    Write-Host "Opening browser..." -ForegroundColor Gray
    Start-Process "http://localhost:$($PORTS.WebUI)"
    
    Write-Host ""
    Write-Host "✨ Happy agent building!" -ForegroundColor Green
    Write-Host ""
}

# Entry point
Main
#endregion
