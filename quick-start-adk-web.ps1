# Enhanced version with better error handling and diagnostics
# Uses Poetry virtual environment for Python commands

param(
  [switch]$Debug,
  [switch]$SkipToolbox,
  [int]$Timeout = 60
)

$ErrorActionPreference = "Continue"

# Get project root (two levels up from script location)
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$VenvPath = Join-Path $ProjectRoot ".venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$ToolboxPath = Join-Path $ProjectRoot "..\genai-toolbox"

function Write-Status {
  param([string]$Message, [string]$Type = "Info")
  $colors = @{
    "Info" = "Cyan"
    "Success" = "Green"
    "Warning" = "Yellow"
    "Error" = "Red"
  }
  Write-Host "   $Message" -ForegroundColor $colors[$Type]
}

function Test-Port {
  param([int]$Port)
  try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.Connect("localhost", $Port)
    $tcp.Close()
    return $true
  } catch {
    return $false
  }
}

function Get-ToolboxLogs {
  $logPath = Join-Path $PSScriptRoot "toolbox.log"
  if (Test-Path $logPath) {
    Write-Status "Recent toolbox logs:" "Warning"
    Get-Content $logPath -Tail 20 | ForEach-Object { Write-Host "     $_" }
  }
}

Write-Host "`n========================================"
Write-Host "  ADK Web UI + GenAI Toolbox Launcher"
Write-Host "========================================`n"

# Check Poetry virtual environment
Write-Status "Checking Poetry virtual environment..."
if (-not (Test-Path $VenvPython)) {
  Write-Status "Virtual environment not found at: $VenvPath" "Error"
  Write-Status "Please run 'poetry install' in project root first" "Error"
  exit 1
}

try {
  $pyVersion = & $VenvPython --version 2>&1
  Write-Status "Using Python: $pyVersion" "Success"
} catch {
  Write-Status "Failed to get Python version: $($_.Exception.Message)" "Error"
  exit 1
}

# Check if port 5000 is already in use
Write-Status "Checking port 5000 availability..."
$skipToolboxStart = $false
if (Test-Port -Port 5000) {
  try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Status "GenAI Toolbox is already running and responding" "Success"
    $skipToolboxStart = $true
  } catch {
    Write-Status "Port 5000 is in use but not responding to health check" "Warning"
    Write-Status "Another process may be using the port. Please check:" "Warning"
    Write-Host "  netstat -ano | findstr :5000" -ForegroundColor Yellow
    exit 1
  }
} else {
  # Check if Docker toolbox container is running but not responding yet
  try {
    $dockerPs = & docker ps --filter "name=genai-toolbox" --format "{{.Names}}" 2>&1
    if ($LASTEXITCODE -eq 0 -and $dockerPs) {
      Write-Status "GenAI Toolbox container found: $dockerPs" "Warning"
      Write-Status "Container is starting up, waiting for it to be ready..." "Info"
      # Don't start a new one, just wait for the existing container
      $skipToolboxStart = $true
    }
  } catch {
    # Docker not available or error checking, will try to start toolbox later
  }
}

if (-not $SkipToolbox -and -not $skipToolboxStart) {
  Write-Status "Starting GenAI Toolbox server..."
  
  # Check for GenAI Toolbox binary
  $toolboxBinary = Join-Path $ToolboxPath "genai-toolbox.exe"
  if (-not (Test-Path $toolboxBinary)) {
    # Try to find it in common locations
    $toolboxBinary = "genai-toolbox"  # Try PATH
    try {
      & where.exe genai-toolbox 2>&1 | Out-Null
      if ($LASTEXITCODE -ne 0) {
        throw "Not found in PATH"
      }
    } catch {
      Write-Status "GenAI Toolbox binary not found" "Error"
      Write-Status "Expected at: $toolboxBinary" "Error"
      Write-Status "Please build GenAI Toolbox first (Go binary)" "Error"
      Write-Status "Or run Docker container from backend/toolbox/" "Error"
      exit 1
    }
  }
  
  Write-Status "Found GenAI Toolbox at: $toolboxBinary" "Success"
  
  # Prepare log file
  $logPath = Join-Path $PSScriptRoot "toolbox.log"
  
  # Start toolbox process
  try {
    $processParams = @{
      FilePath = $toolboxBinary
      ArgumentList = @("serve")  # Standard command for GenAI Toolbox
      RedirectStandardOutput = $logPath
      RedirectStandardError = "${logPath}.err"
      NoNewWindow = (-not $Debug)
      PassThru = $true
      WorkingDirectory = $ToolboxPath
    }
    
    $toolboxProcess = Start-Process @processParams
    Write-Status "Toolbox process started (PID: $($toolboxProcess.Id))" "Success"
    
    # Wait for startup
    Write-Status "Waiting for GenAI Toolbox to be ready..."
    $attempts = 0
    $maxAttempts = $Timeout / 2
    $ready = $false
    
    while ($attempts -lt $maxAttempts -and -not $ready) {
      $attempts++
      Write-Status "Attempt $attempts/$maxAttempts..."
      
      Start-Sleep -Seconds 2
      
      try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 1 -ErrorAction Stop
        $ready = $true
        Write-Status "GenAI Toolbox is ready!" "Success"
      } catch {
        # Check if process is still running
        if ($toolboxProcess.HasExited) {
          Write-Status "Toolbox process terminated unexpectedly!" "Error"
          Write-Status "Exit code: $($toolboxProcess.ExitCode)" "Error"
          Get-ToolboxLogs
          exit 1
        }
      }
    }
    
    if (-not $ready) {
      Write-Status "GenAI Toolbox failed to start within ${Timeout}s timeout" "Error"
      Write-Status "Process is still running but not responding" "Warning"
      Get-ToolboxLogs
      
      # Check error log
      $errLogPath = "${logPath}.err"
      if (Test-Path $errLogPath) {
        Write-Status "`nError output:" "Error"
        Get-Content $errLogPath | ForEach-Object { Write-Host "     $_" -ForegroundColor Red }
      }
      
      Write-Status "`nTroubleshooting tips:" "Warning"
      Write-Status "1. Check if all dependencies are installed: pip install -r requirements.txt"
      Write-Status "2. Verify your Google Cloud credentials are configured"
      Write-Status "3. Check firewall settings for port 5000"
      Write-Status "4. Run with -Debug flag for more details"
      Write-Status "5. Check full logs at: $logPath"
      
      exit 1
    }
  } catch {
    Write-Status "Failed to start toolbox: $($_.Exception.Message)" "Error"
    exit 1
  }
}

# Start ADK Web UI
Write-Status "`nStarting ADK Web UI..."
try {
  # Check for ADK Web server script or use poetry run
  $adkWebScript = Join-Path $PSScriptRoot "start_web.py"
  if (Test-Path $adkWebScript) {
    Write-Status "Using venv Python: $VenvPython" "Info"
    & $VenvPython $adkWebScript
  } else {
    Write-Status "Using poetry run to start ADK..." "Info"
    Set-Location $ProjectRoot
    & poetry run python -m google.adk.web
  }
} catch {
  Write-Status "Failed to start ADK Web: $($_.Exception.Message)" "Error"
  exit 1
}

# ========================================
# DIAGNOSTIC SECTION (for troubleshooting)
# Run this script with -Debug to see diagnostic info
# ========================================

if ($Debug) {
  Write-Host "`n========================================"
  Write-Host "  GenAI Toolbox Diagnostic Tool"
  Write-Host "========================================`n"

  # Check Poetry venv
  Write-Host "[1/6] Checking Poetry virtual environment..."
  if (Test-Path $VenvPython) {
    try {
      $versionInfo = & $VenvPython --version 2>&1
      Write-Host "   ✓ Python found: $versionInfo" -ForegroundColor Green
      
      # Check installed packages
      $requiredPackages = @("google-adk", "fastapi", "uvicorn")
      Write-Host "`n   Checking installed packages..."
      foreach ($package in $requiredPackages) {
        try {
          $result = & $VenvPython -c "import $($package.Replace('-', '_')); print($($package.Replace('-', '_')).__version__)" 2>&1
          if ($LASTEXITCODE -eq 0) {
            Write-Host "      ✓ $package installed: $result" -ForegroundColor Green
          } else {
            Write-Host "      ✗ $package not found" -ForegroundColor Red
          }
        } catch {
          Write-Host "      ✗ Error checking $package : $($_.Exception.Message)" -ForegroundColor Red
        }
      }
    } catch {
      Write-Host "   ✗ Error checking Python: $($_.Exception.Message)" -ForegroundColor Red
    }
  } else {
    Write-Host "   ✗ Python not found at $VenvPython" -ForegroundColor Red
  }

  # Check Toolbox Path
  Write-Host "`n[2/6] Checking GenAI Toolbox path..."
  if (Test-Path $ToolboxPath) {
    Write-Host "   ✓ Toolbox path exists: $ToolboxPath" -ForegroundColor Green
    $toolboxBinary = Join-Path $ToolboxPath "genai-toolbox.exe"
    if (Test-Path $toolboxBinary) {
      Write-Host "   ✓ Binary found: $toolboxBinary" -ForegroundColor Green
    } else {
      Write-Host "   ⚠ Binary not found at: $toolboxBinary" -ForegroundColor Yellow
    }
  } else {
    Write-Host "   ✗ Toolbox path not found: $ToolboxPath" -ForegroundColor Red
  }

  # Check port availability
  Write-Host "`n[3/6] Checking port availability..."
  if (Test-Port -Port 5000) {
    Write-Host "   ⚠ Port 5000 is in use" -ForegroundColor Yellow
  } else {
    Write-Host "   ✓ Port 5000 is available" -ForegroundColor Green
  }

  # Check Google Cloud credentials
  Write-Host "`n[4/6] Checking Google Cloud credentials..."
  if ($env:GOOGLE_APPLICATION_CREDENTIALS) {
    if (Test-Path $env:GOOGLE_APPLICATION_CREDENTIALS) {
      Write-Host "   ✓ Credentials file found at $env:GOOGLE_APPLICATION_CREDENTIALS" -ForegroundColor Green
    } else {
      Write-Host "   ✗ Credentials file not found at $env:GOOGLE_APPLICATION_CREDENTIALS" -ForegroundColor Red
    }
  } else {
    Write-Host "   ⚠ GOOGLE_APPLICATION_CREDENTIALS not set" -ForegroundColor Yellow
    Write-Host "     Trying gcloud auth..." -ForegroundColor Yellow
    try {
      $null = & gcloud auth list 2>&1
      if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ gcloud auth configured" -ForegroundColor Green
      } else {
        Write-Host "   ✗ No gcloud authentication" -ForegroundColor Red
      }
    } catch {
      Write-Host "   ✗ gcloud not found" -ForegroundColor Red
    }
  }

  # Check GenAI Toolbox binary
  Write-Host "`n[5/6] Checking GenAI Toolbox..."
  if (Test-Path (Join-Path $ToolboxPath "genai-toolbox.exe")) {
    Write-Host "   ✓ GenAI Toolbox binary found" -ForegroundColor Green
  } else {
    Write-Host "   ✗ GenAI Toolbox binary not found" -ForegroundColor Yellow
    Write-Host "     Expected at: $(Join-Path $ToolboxPath 'genai-toolbox.exe')" -ForegroundColor Yellow
  }

  # Check recent logs
  Write-Host "`n[6/6] Checking recent logs..."
  $logPath = Join-Path $PSScriptRoot "toolbox.log"
  if (Test-Path $logPath) {
    Write-Host "   Recent log entries:" -ForegroundColor Cyan
    Get-Content $logPath -Tail 10 | ForEach-Object { Write-Host "     $_" }
  } else {
    Write-Host "   No log file found" -ForegroundColor Yellow
  }

  Write-Host "`n========================================"
  Write-Host "Diagnosis complete!"
  Write-Host "========================================`n"
}