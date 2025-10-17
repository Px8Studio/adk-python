# Stop ADK Web Development Environment
# This script stops all ADK Web services

Write-Host "🛑 Stopping ADK Web Development Environment" -ForegroundColor Red
Write-Host ""

$TOOLBOX_DIR = "C:\Users\rjjaf\_Projects\orkhon\backend\toolbox"

# Stop Docker containers
Write-Host "1️⃣  Stopping GenAI Toolbox..." -ForegroundColor Yellow
Set-Location $TOOLBOX_DIR
docker-compose -f docker-compose.dev.yml down

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Toolbox stopped" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Error stopping Toolbox" -ForegroundColor Yellow
}

Write-Host ""

# Kill Node.js processes (ADK Web UI)
Write-Host "2️⃣  Stopping ADK Web UI (Node.js)..." -ForegroundColor Yellow
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    $nodeProcesses | Stop-Process -Force
    Write-Host "   ✓ Stopped $($nodeProcesses.Count) Node.js process(es)" -ForegroundColor Green
} else {
    Write-Host "   ℹ No Node.js processes found" -ForegroundColor Gray
}

Write-Host ""

# Note about Python processes
Write-Host "3️⃣  ADK API Server (Python)..." -ForegroundColor Yellow
Write-Host "   ℹ Please close the ADK API Server terminal window manually" -ForegroundColor Gray
Write-Host "   (or press Ctrl+C in that window)" -ForegroundColor Gray

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "✅ Services stopped!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
