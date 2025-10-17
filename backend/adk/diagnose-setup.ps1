# ========================================
# ADK + GenAI Toolbox Diagnostic Tool
# ========================================
# Run this to check your development environment setup

param(
  [switch]$Verbose
)

$ErrorActionPreference = "Continue"

# Get project root (two levels up from script location)
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$VenvPath = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$ToolboxPath = Join-Path $ProjectRoot "..\genai-toolbox"

Write-Host "`n========================================"
Write-Host "  ADK + GenAI Toolbox Diagnostic Tool"
Write-Host "========================================`n"

$issues = @()
$warnings = @()

# [1/7] Check Poetry installation
Write-Host "[1/7] Checking Poetry installation..." -ForegroundColor Cyan
try {
  $poetryVersion = & poetry --version 2>&1
  if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Poetry installed: $poetryVersion" -ForegroundColor Green
  } else {
    Write-Host "   ✗ Poetry not working properly" -ForegroundColor Red
    $issues += "Poetry not functioning"
  }
} catch {
  Write-Host "   ✗ Poetry not found in PATH" -ForegroundColor Red
  $issues += "Poetry not installed"
}

# [2/7] Check Poetry virtual environment
Write-Host "`n[2/7] Checking Poetry virtual environment..." -ForegroundColor Cyan
if (Test-Path $VenvPath) {
  Write-Host "   ✓ Virtual environment found at: $VenvPath" -ForegroundColor Green
  
  if (Test-Path $VenvPython) {
    try {
      $venvPyVersion = & $VenvPython --version 2>&1
      Write-Host "   ✓ Python in venv: $venvPyVersion" -ForegroundColor Green
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

# [3/7] Check required Python packages in venv
Write-Host "`n[3/7] Checking required Python packages..." -ForegroundColor Cyan
if (Test-Path $VenvPython) {
  $requiredPackages = @(
    @{Name="google-adk"; Import="google.adk"},
    @{Name="langchain"; Import="langchain"},
    @{Name="langgraph"; Import="langgraph"},
    @{Name="toolbox-core"; Import="toolbox_core"}
  )
  
  foreach ($pkg in $requiredPackages) {
    $null = & $VenvPython -c "import $($pkg.Import)" 2>&1
    if ($LASTEXITCODE -eq 0) {
      Write-Host "   ✓ $($pkg.Name) installed" -ForegroundColor Green
    } else {
      Write-Host "   ✗ $($pkg.Name) not found" -ForegroundColor Red
      $issues += "$($pkg.Name) missing from venv"
    }
  }
} else {
  Write-Host "   ⊘ Skipped (venv not available)" -ForegroundColor Yellow
}

# [4/7] Check port availability
Write-Host "`n[4/7] Checking port 5000..." -ForegroundColor Cyan
try {
  $tcp = New-Object System.Net.Sockets.TcpClient
  $tcp.Connect("localhost", 5000)
  $tcp.Close()
  Write-Host "   ⚠ Port 5000 is already in use" -ForegroundColor Yellow
  
  # Try to identify what's using it
  try {
    $null = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "     GenAI Toolbox is already running" -ForegroundColor Green
  } catch {
    Write-Host "     Another process is using port 5000" -ForegroundColor Yellow
    $warnings += "Port 5000 occupied by non-toolbox process"
  }
} catch {
  Write-Host "   ✓ Port 5000 is available" -ForegroundColor Green
}

# [5/7] Check Google Cloud credentials
Write-Host "`n[5/7] Checking Google Cloud authentication..." -ForegroundColor Cyan
$gcpConfigured = $false

if ($env:GOOGLE_APPLICATION_CREDENTIALS) {
  if (Test-Path $env:GOOGLE_APPLICATION_CREDENTIALS) {
    Write-Host "   ✓ Service account credentials: $env:GOOGLE_APPLICATION_CREDENTIALS" -ForegroundColor Green
    $gcpConfigured = $true
  } else {
    Write-Host "   ✗ Credentials file not found: $env:GOOGLE_APPLICATION_CREDENTIALS" -ForegroundColor Red
    $issues += "Invalid GOOGLE_APPLICATION_CREDENTIALS path"
  }
}

try {
  $activeAccounts = & gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
  if ($LASTEXITCODE -eq 0 -and $activeAccounts) {
    Write-Host "   ✓ gcloud authenticated as: $activeAccounts" -ForegroundColor Green
    $gcpConfigured = $true
  }
} catch {
  Write-Host "   ⊘ gcloud CLI not found" -ForegroundColor Yellow
}

if (-not $gcpConfigured) {
  Write-Host "   ⚠ No Google Cloud authentication found" -ForegroundColor Yellow
  $warnings += "No GCP authentication configured"
}

# [6/7] Check GenAI Toolbox
Write-Host "`n[6/7] Checking GenAI Toolbox..." -ForegroundColor Cyan

# Check if running via Docker
try {
  $dockerPs = & docker ps --filter "name=genai-toolbox" --format "{{.Names}}" 2>&1
  if ($LASTEXITCODE -eq 0 -and $dockerPs) {
    Write-Host "   ✓ GenAI Toolbox running in Docker: $dockerPs" -ForegroundColor Green
  }
} catch {
  # Docker not available, check binary
}

# Check binary
$toolboxBinary = Join-Path $ToolboxPath "genai-toolbox.exe"
if (Test-Path $toolboxBinary) {
  Write-Host "   ✓ GenAI Toolbox binary found at: $toolboxBinary" -ForegroundColor Green
} else {
  Write-Host "   ⚠ GenAI Toolbox binary not found" -ForegroundColor Yellow
  Write-Host "     Expected at: $toolboxBinary" -ForegroundColor Yellow
  $warnings += "GenAI Toolbox binary not found (Docker recommended)"
}

# Check Docker Compose files
$dockerComposeFile = Join-Path $ProjectRoot "backend\toolbox\docker-compose.dev.yml"
if (Test-Path $dockerComposeFile) {
  Write-Host "   ✓ Docker Compose config found: docker-compose.dev.yml" -ForegroundColor Green
} else {
  Write-Host "   ⚠ Docker Compose config not found" -ForegroundColor Yellow
  $warnings += "Docker Compose configuration missing"
}

# [7/7] Check project structure
Write-Host "`n[7/7] Checking project structure..." -ForegroundColor Cyan

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

# Summary
Write-Host "`n========================================"
Write-Host "  Diagnosis Summary"
Write-Host "========================================`n"

if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
  Write-Host "✓ All checks passed! Your environment is ready." -ForegroundColor Green
  Write-Host "`nNext steps:" -ForegroundColor Cyan
  Write-Host "  1. Start GenAI Toolbox: cd backend\toolbox && docker-compose -f docker-compose.dev.yml up -d"
  Write-Host "  2. Run ADK Web: cd backend\adk && .\start-adk-web.ps1"
} else {
  if ($issues.Count -gt 0) {
    Write-Host "⚠ ISSUES FOUND ($($issues.Count)):" -ForegroundColor Red
    foreach ($issue in $issues) {
      Write-Host "   • $issue" -ForegroundColor Red
    }
    Write-Host ""
  }
  
  if ($warnings.Count -gt 0) {
    Write-Host "⚠ WARNINGS ($($warnings.Count)):" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
      Write-Host "   • $warning" -ForegroundColor Yellow
    }
    Write-Host ""
  }
  
  Write-Host "Recommended fixes:" -ForegroundColor Cyan
  if ($issues -contains "Poetry not installed") {
    Write-Host "  • Install Poetry: (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
  }
  if ($issues -contains "Virtual environment not created") {
    Write-Host "  • Create venv: cd '$ProjectRoot' && poetry install"
  }
  if ($warnings -contains "GenAI Toolbox binary not found (Docker recommended)") {
    Write-Host "  • Use Docker: cd backend\toolbox && docker-compose -f docker-compose.dev.yml up -d"
  }
  if ($warnings -contains "No GCP authentication configured") {
    Write-Host "  • Set up GCP: gcloud auth login && gcloud config set project YOUR_PROJECT_ID"
  }
}

Write-Host "`n========================================"
Write-Host "For more help, run with -Verbose flag"
Write-Host "========================================`n"
