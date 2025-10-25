#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Load environment variables from .env file into current PowerShell session

.DESCRIPTION
    Reads .env file and sets environment variables for the current session.
    Useful for running Python scripts that expect environment variables to be set.

.EXAMPLE
    . .\backend\scripts\load-env.ps1
    poetry run python -m backend.gcp.upload_parquet --datasource dnb_statistics --all
#>

$ErrorActionPreference = 'Stop'

$EnvFile = Join-Path $PSScriptRoot ".." ".." ".env"

if (-not (Test-Path $EnvFile)) {
    Write-Warning ".env file not found at: $EnvFile"
    exit 1
}

Write-Host "Loading environment variables from .env..." -ForegroundColor Cyan

Get-Content $EnvFile | ForEach-Object {
    $line = $_.Trim()
    
    # Skip empty lines and comments
    if ($line -eq "" -or $line.StartsWith("#")) {
        return
    }
    
    # Parse KEY=VALUE
    if ($line -match '^([^=]+)=(.*)$') {
        $key = $Matches[1].Trim()
        $value = $Matches[2].Trim()
        
        # Remove quotes if present
        $value = $value -replace '^"(.*)"$', '$1'
        $value = $value -replace "^'(.*)'$", '$1'
        
        # Set environment variable
        Set-Item -Path "env:$key" -Value $value
        Write-Host "  ✓ $key" -ForegroundColor Green
    }
}

Write-Host "`nEnvironment variables loaded successfully!" -ForegroundColor Green
Write-Host "Project ID: $env:GOOGLE_CLOUD_PROJECT" -ForegroundColor Yellow
