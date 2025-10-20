#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Generate Python HTTP clients for DNB APIs using Kiota

.DESCRIPTION
    This script generates Python HTTP clients from OpenAPI specifications for:
    - DNB Echo API
    - DNB Public Register API
    - DNB Statistics API

.PARAMETER Clean
    Remove existing client directories before regenerating

.PARAMETER ClientName
    Generate only a specific client: 'echo', 'public-register', or 'statistics'

.EXAMPLE
    .\generate-dnb-clients.ps1
    Generate all three clients

.EXAMPLE
    .\generate-dnb-clients.ps1 -Clean
    Clean existing clients and regenerate all

.EXAMPLE
    .\generate-dnb-clients.ps1 -ClientName echo
    Generate only the Echo API client
#>

[CmdletBinding()]
param(
    [switch]$Clean,
    [ValidateSet('echo', 'public-register', 'statistics', 'all')]
    [string]$ClientName = 'all'
)

# Get script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)

# Paths
$specsDir = Join-Path $projectRoot "backend\apis\dnb\specs"
$clientsDir = Join-Path $projectRoot "backend\clients"

# Client configurations
$clients = @{
    'echo' = @{
        Name = 'Echo'
        ClassName = 'DnbEchoClient'
        Namespace = 'dnb_echo_client'
        SpecFile = 'openapi3-echo-api.yaml'
        OutputDir = 'dnb-echo'
    }
    'public-register' = @{
        Name = 'Public Register'
        ClassName = 'DnbPublicRegisterClient'
        Namespace = 'dnb_public_register_client'
        SpecFile = 'openapi3_publicdatav1.yaml'
        OutputDir = 'dnb-public-register'
    }
    'statistics' = @{
        Name = 'Statistics'
        ClassName = 'DnbStatisticsClient'
        Namespace = 'dnb_statistics_client'
        SpecFile = 'openapi3_statisticsdatav2024100101.yaml'
        OutputDir = 'dnb-statistics'
    }
}

# Check if Kiota is installed
Write-Host "? Checking for Kiota CLI..." -ForegroundColor Cyan
try {
    $kiotaVersion = kiota --version 2>&1
    Write-Host "? Kiota found: $kiotaVersion" -ForegroundColor Green
}
catch {
    Write-Host "? Kiota CLI not found. Install it with: dotnet tool install --global Microsoft.OpenApi.Kiota" -ForegroundColor Red
    exit 1
}

# Check if specs directory exists
if (-not (Test-Path $specsDir)) {
    Write-Host "? Specs directory not found: $specsDir" -ForegroundColor Red
    exit 1
}

# Function to generate a single client
function Generate-Client {
    param(
        [string]$Key,
        [hashtable]$Config
    )

    $specPath = Join-Path $specsDir $Config.SpecFile
    $outputPath = Join-Path $clientsDir $Config.OutputDir

    Write-Host "? Generating $($Config.Name) client..." -ForegroundColor Cyan
    Write-Host "  Spec: $specPath" -ForegroundColor Gray
    Write-Host "  Output: $outputPath" -ForegroundColor Gray

    # Check if spec file exists
    if (-not (Test-Path $specPath)) {
        Write-Host "? Spec file not found: $specPath" -ForegroundColor Red
        return $false
    }

    # Clean if requested
    if ($Clean -and (Test-Path $outputPath)) {
        Write-Host "? Removing existing client directory: $outputPath" -ForegroundColor Yellow
        Remove-Item -Path $outputPath -Recurse -Force
    }

    # Generate client
    $kiotaArgs = @(
        'generate'
        '-l', 'python'
        '-c', $Config.ClassName
        '-n', $Config.Namespace
        '-d', $specPath
        '-o', $outputPath
        '--exclude-backward-compatible'
    )

    Write-Host "  Running: kiota $($kiotaArgs -join ' ')" -ForegroundColor Gray

    try {
        & kiota @kiotaArgs
        if ($LASTEXITCODE -eq 0) {
            Write-Host "? $($Config.Name) client generated successfully" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "? Failed to generate $($Config.Name) client (exit code: $LASTEXITCODE)" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "? Error generating $($Config.Name) client: $_" -ForegroundColor Red
        return $false
    }
}

# Main execution
Write-Host ""
Write-Host "???????????????????????????????????????????????" -ForegroundColor Cyan
Write-Host "  DNB API Client Generator (Kiota)" -ForegroundColor Cyan
Write-Host "???????????????????????????????????????????????" -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failCount = 0

if ($ClientName -eq 'all') {
    # Generate all clients
    foreach ($key in $clients.Keys) {
        if (Generate-Client -Key $key -Config $clients[$key]) {
            $successCount++
        }
        else {
            $failCount++
        }
        Write-Host ""
    }
}
else {
    # Generate specific client
    if ($clients.ContainsKey($ClientName)) {
        if (Generate-Client -Key $ClientName -Config $clients[$ClientName]) {
            $successCount++
        }
        else {
            $failCount++
        }
    }
    else {
        Write-Host "? Unknown client name: $ClientName" -ForegroundColor Red
        Write-Host "? Valid options: echo, public-register, statistics, all" -ForegroundColor Cyan
        exit 1
    }
}

# Summary
Write-Host "???????????????????????????????????????????????" -ForegroundColor Cyan
Write-Host "  Generation Summary" -ForegroundColor Cyan
Write-Host "???????????????????????????????????????????????" -ForegroundColor Cyan
Write-Host "? Successful: $successCount" -ForegroundColor Green
if ($failCount -gt 0) {
    Write-Host "? Failed: $failCount" -ForegroundColor Red
}
Write-Host ""

# Next steps
if ($successCount -gt 0) {
    Write-Host "? Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Set your API key: " -NoNewline -ForegroundColor Gray
    Write-Host '$env:DNB_SUBSCRIPTION_KEY_DEV = "your-key"' -ForegroundColor Yellow
    Write-Host "  2. Test clients: " -NoNewline -ForegroundColor Gray
    Write-Host "poetry run python backend/clients/test_dnb_clients.py" -ForegroundColor Yellow
    Write-Host ""
}

# Exit with appropriate code
if ($failCount -gt 0) {
    exit 1
}
else {
    exit 0
}
