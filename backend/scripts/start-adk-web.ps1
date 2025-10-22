# Start ADK Web Server (PowerShell)
param(
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ProjectRoot) { $ProjectRoot = "$PSScriptRoot" }

$VenvActivate = Join-Path $ProjectRoot ".venv/Scripts/Activate.ps1"
$DotEnv      = Join-Path $ProjectRoot ".env"
$AgentsPath  = Join-Path $ProjectRoot "backend/adk/agents"

function Show-Info { param([string]$m) Write-Host "[INFO] $m" -ForegroundColor Yellow }
function Show-Ok   { param([string]$m) Write-Host "[OK]  $m" -ForegroundColor Green }
function Show-Err  { param([string]$m) Write-Host "[ERR] $m" -ForegroundColor Red }

try {
  if (-not (Test-Path $VenvActivate)) {
    Show-Err "Virtual environment not found at: $VenvActivate"
    Show-Info "Create it and install dependencies, then retry."
    exit 1
  }

  # Load .env if present
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
  }

  # Mirror GEMINI_API_KEY -> GOOGLE_API_KEY if needed
  $gemini = [System.Environment]::GetEnvironmentVariable('GEMINI_API_KEY', 'Process')
  $google = [System.Environment]::GetEnvironmentVariable('GOOGLE_API_KEY', 'Process')
  if ($gemini -and [string]::IsNullOrWhiteSpace($google)) {
    [System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', $gemini, 'Process')
    Show-Info "Mirrored GEMINI_API_KEY -> GOOGLE_API_KEY for this session"
  }

  # Check port
  $portInUse = $false
  try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.Connect('localhost', $Port)
    $tcp.Close()
    $portInUse = $true
  } catch { $portInUse = $false }

  if ($portInUse) {
    Show-Err "Port $Port is already in use"
    exit 1
  }

  & $VenvActivate
  Show-Ok ".venv activated"

  Show-Info "Starting ADK Web on http://localhost:$Port"
  & adk web --reload_agents --host=0.0.0.0 --port=$Port $AgentsPath
}
catch {
  Show-Err "Failed to start ADK Web: $($_.Exception.Message)"
  exit 1
}
