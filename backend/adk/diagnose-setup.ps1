# ADK Setup Diagnostic Tool
# Checks all prerequisites and dependencies for ADK Web development

$ErrorActionPreference = "Continue"
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$issues = @()
$warnings = @()

Write-Host "========================================"
Write-Host "  ADK Setup Diagnostic Tool"
Write-Host "========================================`n"

# [1/7] Check Poetry
Write-Host "[1/7] Checking Poetry installation..." -ForegroundColor Cyan
try {
  $poetryVersion = & poetry --version 2>&1
  if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Poetry installed: $poetryVersion" -ForegroundColor Green
  } else {
    Write-Host "   ✗ Poetry command failed" -ForegroundColor Red
    $issues += "Poetry not installed"
  }
} catch {
  Write-Host "   ✗ Poetry not found in PATH" -ForegroundColor Red
  $issues += "Poetry not installed"
}

# [2/7] Check Virtual Environment
Write-Host "`n[2/7] Checking Poetry virtual environment..." -ForegroundColor Cyan
$venvPath = Join-Path $ProjectRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"

if (Test-Path $venvPath) {
  Write-Host "   ✓ Virtual environment exists at: $venvPath" -ForegroundColor Green
  
  if (Test-Path $venvPython) {
    try {
      $pyVersion = & $venvPython --version 2>&1
      if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Python executable found: $pyVersion" -ForegroundColor Green
      } else {
        Write-Host "   ✗ Python executable not working" -ForegroundColor Red
        $issues += "Python in venv not working"
      }
    } catch {
      Write-Host "   ✗ Failed to check Python version" -ForegroundColor Red
      $issues += "Python in venv not working"
    }
  } else {
    Write-Host "   ✗ Python executable not found in venv" -ForegroundColor Red
    $issues += "Python executable missing from venv"
  }
} else {
  Write-Host "   ✗ Virtual environment not found at: $venvPath" -ForegroundColor Red
  $issues += "Virtual environment not created"
}

# [3/7] Check Docker
Write-Host "`n[3/7] Checking Docker..." -ForegroundColor Cyan
try {
  $dockerVersion = & docker --version 2>&1
  if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Docker installed: $dockerVersion" -ForegroundColor Green
    
    # Check if Docker is running
    try {
      $null = & docker ps 2>&1
      if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Docker daemon is running" -ForegroundColor Green
      } else {
        Write-Host "   ⚠ Docker installed but daemon not running" -ForegroundColor Yellow
        $warnings += "Docker daemon not running"
      }
    } catch {
      Write-Host "   ⚠ Docker installed but daemon not accessible" -ForegroundColor Yellow
      $warnings += "Docker daemon not accessible"
    }
  } else {
    Write-Host "   ✗ Docker command failed" -ForegroundColor Red
    $issues += "Docker not installed"
  }
} catch {
  Write-Host "   ✗ Docker not found in PATH" -ForegroundColor Red
  $issues += "Docker not installed"
}

# [4/7] Check Node.js and npm
Write-Host "`n[4/7] Checking Node.js and npm..." -ForegroundColor Cyan
try {
  $nodeVersion = & node --version 2>&1
  if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Node.js installed: $nodeVersion" -ForegroundColor Green
  } else {
    Write-Host "   ✗ Node.js command failed" -ForegroundColor Red
    $warnings += "Node.js not working properly"
  }
} catch {
  Write-Host "   ⚠ Node.js not found (required for ADK Web UI)" -ForegroundColor Yellow
  $warnings += "Node.js not installed"
}

try {
  $npmVersion = & npm --version 2>&1
  if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ npm installed: $npmVersion" -ForegroundColor Green
  } else {
    Write-Host "   ✗ npm command failed" -ForegroundColor Red
    $warnings += "npm not working properly"
  }
} catch {
  Write-Host "   ⚠ npm not found" -ForegroundColor Yellow
  $warnings += "npm not installed"
}

# [5/7] Check Google Cloud SDK and credentials
Write-Host "`n[5/7] Checking Google Cloud configuration..." -ForegroundColor Cyan
$gcpConfigured = $false

if ($env:GOOGLE_APPLICATION_CREDENTIALS) {
  Write-Host "   GOOGLE_APPLICATION_CREDENTIALS set" -ForegroundColor Cyan
  if (Test-Path $env:GOOGLE_APPLICATION_CREDENTIALS) {
    Write-Host "   ✓ Credentials file found: $env:GOOGLE_APPLICATION_CREDENTIALS" -ForegroundColor Green
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
  # gcloud not installed or not in PATH
}

if (-not $gcpConfigured) {
  Write-Host "   ⚠ No GCP authentication configured" -ForegroundColor Yellow
  $warnings += "No GCP authentication configured"
}

# [6/7] Check GenAI Toolbox
Write-Host "`n[6/7] Checking GenAI Toolbox..." -ForegroundColor Cyan

# Check for Docker container first (recommended approach)
try {
  $toolboxContainer = & docker ps --filter "name=genai-toolbox" --format "{{.Names}}" 2>&1
  if ($LASTEXITCODE -eq 0 -and $toolboxContainer) {
    Write-Host "   ✓ GenAI Toolbox container running: $toolboxContainer" -ForegroundColor Green
  } else {
  Write-Host "   ⚠ GenAI Toolbox container not running" -ForegroundColor Yellow
  Write-Host "   ℹ Start with: cd backend\toolbox; docker-compose -f docker-compose.dev.yml up -d" -ForegroundColor Cyan
  }
} catch {
  Write-Host "   ⚠ Could not check Docker containers" -ForegroundColor Yellow
}

# Check for binary as fallback
$toolboxBinary = Join-Path $ProjectRoot "..\genai-toolbox\genai-toolbox.exe"
if (Test-Path $toolboxBinary) {
  Write-Host "   ✓ GenAI Toolbox binary found: $toolboxBinary" -ForegroundColor Green
} else {
  Write-Host "   ⚠ GenAI Toolbox binary not found (Docker recommended)" -ForegroundColor Yellow
  $warnings += "GenAI Toolbox binary not found (Docker recommended)"
}

# [7/7] Check project structure
Write-Host "`n[7/7] Checking project structure..." -ForegroundColor Cyan

$requiredPaths = @(
  @{Path = "pyproject.toml"; Type = "Poetry configuration"},
  @{Path = "backend\adk\agents"; Type = "ADK agents directory"},
  @{Path = "backend\toolbox"; Type = "Toolbox configuration"}
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
  Write-Host "  1. Start GenAI Toolbox: cd backend\toolbox; docker-compose -f docker-compose.dev.yml up -d"
  Write-Host "  2. Run ADK Web: cd backend\adk; .\start-adk-web.ps1"
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
    Write-Host "  • Create venv: cd '$ProjectRoot'; poetry install"
  }
  if ($warnings -contains "GenAI Toolbox binary not found (Docker recommended)") {
    Write-Host "  • Start Toolbox: cd backend\toolbox; docker-compose -f docker-compose.dev.yml up -d"
  }
  if ($warnings -contains "No GCP authentication configured") {
    Write-Host "  • Configure GCP: gcloud auth application-default login"
  }
}

Write-Host "`n========================================"
Write-Host ""