# Start ADK Web Development Environment
# This script starts all required services for ADK Web development

Write-Host "🚀 Starting ADK Web Development Environment" -ForegroundColor Green
Write-Host ""

# Configuration
$TOOLBOX_DIR = "C:\Users\rjjaf\_Projects\orkhon\backend\toolbox"
$ADK_AGENTS_DIR = "C:\Users\rjjaf\_Projects\orkhon\backend\adk\agents"
$ADK_WEB_DIR = "C:\Users\rjjaf\_Projects\adk-web"
$VENV_PATH = "C:\Users\rjjaf\_Projects\orkhon\.venv\Scripts\Activate.ps1"

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check if Node.js is available
if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Host "✓ Node.js is installed" -ForegroundColor Green
} else {
    Write-Host "✗ Node.js is not installed" -ForegroundColor Red
    exit 1
}

# Check if Python virtual environment exists
if (Test-Path $VENV_PATH) {
    Write-Host "✓ Python virtual environment found" -ForegroundColor Green
} else {
    Write-Host "✗ Python virtual environment not found at $VENV_PATH" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔧 Starting services..." -ForegroundColor Yellow
Write-Host ""

# Step 1: Start Toolbox
Write-Host "1️⃣  Starting GenAI Toolbox..." -ForegroundColor Cyan
Set-Location $TOOLBOX_DIR
docker-compose -f docker-compose.dev.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Toolbox started on http://localhost:5000" -ForegroundColor Green
} else {
    Write-Host "   ✗ Failed to start Toolbox" -ForegroundColor Red
    exit 1
}

# Wait for Toolbox to be ready
Write-Host "   ⏳ Waiting for Toolbox to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$toolboxReady = $false

while ($attempt -lt $maxAttempts -and -not $toolboxReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $toolboxReady = $true
        }
    } catch {
        Start-Sleep -Seconds 1
        $attempt++
    }
}

if ($toolboxReady) {
    Write-Host "   ✓ Toolbox is ready!" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Toolbox may not be fully ready yet" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Start ADK API Server
Write-Host "2️⃣  Starting ADK API Server..." -ForegroundColor Cyan
Write-Host "   📂 Agents directory: $ADK_AGENTS_DIR" -ForegroundColor Gray

# Create a script block to run in a new window
$apiServerScript = @"
cd C:\Users\rjjaf\_Projects\orkhon\backend\adk
& '$VENV_PATH'
Write-Host 'Starting ADK API Server...' -ForegroundColor Green
adk api_server --allow_origins=http://localhost:4200 --host=0.0.0.0 --port=8000 agents
"@

# Save script to temp file
$tempScript = [System.IO.Path]::GetTempFileName() + ".ps1"
$apiServerScript | Out-File -FilePath $tempScript -Encoding UTF8

# Start API server in new window
Start-Process powershell -ArgumentList "-NoExit", "-File", $tempScript

Write-Host "   ✓ ADK API Server starting in new window (http://localhost:8000)" -ForegroundColor Green
Write-Host ""

# Wait a bit for API server to start
Start-Sleep -Seconds 5

# Step 3: Start ADK Web UI
Write-Host "3️⃣  Starting ADK Web UI..." -ForegroundColor Cyan

# Create a script block for web UI
$webUIScript = @"
cd $ADK_WEB_DIR
Write-Host 'Starting ADK Web UI...' -ForegroundColor Green
npm run serve --backend=http://localhost:8000
"@

# Save script to temp file
$tempWebScript = [System.IO.Path]::GetTempFileName() + ".ps1"
$webUIScript | Out-File -FilePath $tempWebScript -Encoding UTF8

# Start Web UI in new window
Start-Process powershell -ArgumentList "-NoExit", "-File", $tempWebScript

Write-Host "   ✓ ADK Web UI starting in new window (http://localhost:4200)" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "✅ All services started successfully!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Service URLs:" -ForegroundColor Yellow
Write-Host "   • ADK Web UI:        http://localhost:4200" -ForegroundColor Cyan
Write-Host "   • ADK API Server:    http://localhost:8000" -ForegroundColor Cyan
Write-Host "   • GenAI Toolbox:     http://localhost:5000" -ForegroundColor Cyan
Write-Host "   • Jaeger Tracing:    http://localhost:16686" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Wait ~30 seconds for all services to fully start"
Write-Host "   2. Open http://localhost:4200 in your browser"
Write-Host "   3. Select 'dnb_agent' from the agent dropdown"
Write-Host "   4. Start chatting with your agent!"
Write-Host ""
Write-Host "🛑 To stop all services:" -ForegroundColor Yellow
Write-Host "   • Close the ADK API Server and Web UI windows"
Write-Host "   • Run: cd $TOOLBOX_DIR; docker-compose -f docker-compose.dev.yml down"
Write-Host ""
Write-Host "💡 Tip: Check ADK_WEB_SETUP.md for troubleshooting and more info"
Write-Host ""

# Wait a bit, then open browser
Start-Sleep -Seconds 10
Write-Host "🌐 Opening ADK Web UI in browser..." -ForegroundColor Cyan
Start-Process "http://localhost:4200"
