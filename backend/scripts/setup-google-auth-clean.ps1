#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Setup Google Cloud authentication with service account
.DESCRIPTION
    Creates a service account, grants necessary permissions, downloads key file,
    and updates .env configuration for the Orkhon project.
    
.PARAMETER ProjectId
    Google Cloud Project ID (default: woven-art-475517-n4)
.PARAMETER ServiceAccountName
    Name for the service account (default: orkhon-service-account)
.PARAMETER SkipPermissions
    Skip granting IAM permissions (useful if already granted)
.PARAMETER Force
    Overwrite existing service account key file
    
.EXAMPLE
    .\setup-google-auth.ps1
    
.EXAMPLE
    .\setup-google-auth.ps1 -ProjectId "my-project" -ServiceAccountName "my-sa"
    
.EXAMPLE
    .\setup-google-auth.ps1 -SkipPermissions
#>

param(
    [string]$ProjectId = "woven-art-475517-n4",
    [string]$ServiceAccountName = "orkhon-service-account",
    [switch]$SkipPermissions,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Colors
function Write-Success { param($msg) Write-Host "??? $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "??????  $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "??????  $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "??? $msg" -ForegroundColor Red }
function Write-Step { param($msg) Write-Host "`n???? $msg" -ForegroundColor Blue }

# Paths
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$KeyFile = Join-Path $ProjectRoot "service-account-key.json"
$EnvFile = Join-Path $ProjectRoot ".env"

Write-Host "`n??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????" -ForegroundColor Magenta
Write-Host "???  Google Cloud Authentication Setup for Orkhon                 ???" -ForegroundColor Magenta
Write-Host "??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????`n" -ForegroundColor Magenta

Write-Info "Project Root: $ProjectRoot"
Write-Info "Project ID: $ProjectId"
Write-Info "Service Account: $ServiceAccountName"
Write-Info "Key File: $KeyFile"

# Check gcloud CLI
Write-Step "Checking prerequisites..."
try {
    $gcloudVersion = gcloud version --format=json | ConvertFrom-Json
    Write-Success "gcloud CLI installed: $($gcloudVersion.'Google Cloud SDK')"
} catch {
    Write-Error "gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Check if already logged in
try {
    $currentAccount = gcloud config get-value account 2>$null
    if ($currentAccount) {
        Write-Success "Logged in as: $currentAccount"
    } else {
        Write-Warning "Not logged in to gcloud. Running 'gcloud auth login'..."
        gcloud auth login
    }
} catch {
    Write-Warning "Could not verify gcloud authentication"
}

# Set project
Write-Step "Setting active project..."
gcloud config set project $ProjectId
Write-Success "Active project: $ProjectId"

# Check if service account exists
Write-Step "Checking if service account exists..."
$saEmail = "${ServiceAccountName}@${ProjectId}.iam.gserviceaccount.com"
$saExists = gcloud iam service-accounts list --filter="email:$saEmail" --format="value(email)" 2>$null

if ($saExists) {
    Write-Info "Service account already exists: $saEmail"
} else {
    Write-Step "Creating service account..."
    gcloud iam service-accounts create $ServiceAccountName `
        --description="Orkhon project service account for all GCP operations" `
        --display-name="Orkhon Service Account"
    Write-Success "Service account created: $saEmail"
}

# Grant permissions
if (-not $SkipPermissions) {
    Write-Step "Granting IAM permissions..."
    
    $roles = @(
        @{Role="roles/bigquery.dataEditor"; Description="BigQuery Data Editor"},
        @{Role="roles/bigquery.jobUser"; Description="BigQuery Job User"},
        @{Role="roles/storage.admin"; Description="Cloud Storage Admin"},
        @{Role="roles/aiplatform.user"; Description="Vertex AI User"}
    )
    
    foreach ($roleInfo in $roles) {
        Write-Info "Granting $($roleInfo.Description)..."
        gcloud projects add-iam-policy-binding $ProjectId `
            --member="serviceAccount:$saEmail" `
            --role="$($roleInfo.Role)" `
            --condition=None `
            --quiet
    }
    Write-Success "All permissions granted"
} else {
    Write-Warning "Skipping permission grants (-SkipPermissions flag set)"
}

# Download key
Write-Step "Creating service account key..."
if (Test-Path $KeyFile) {
    if ($Force) {
        Write-Warning "Overwriting existing key file"
        Remove-Item $KeyFile -Force
    } else {
        Write-Error "Key file already exists: $KeyFile"
        Write-Info "Use -Force to overwrite, or manually delete the file"
        exit 1
    }
}

gcloud iam service-accounts keys create $KeyFile `
    --iam-account=$saEmail

Write-Success "Service account key created: $KeyFile"

# Update .env file
Write-Step "Updating .env file..."
if (-not (Test-Path $EnvFile)) {
    Write-Warning ".env file not found, creating new one"
    New-Item -Path $EnvFile -ItemType File -Force | Out-Null
}

$envContent = Get-Content $EnvFile -Raw -ErrorAction SilentlyContinue
if ($envContent -match "GOOGLE_APPLICATION_CREDENTIALS") {
    Write-Info ".env already contains GOOGLE_APPLICATION_CREDENTIALS"
    Write-Warning "Please manually update the path to: $KeyFile"
} else {
    $newLine = "`n# Service Account Authentication (never expires)`nGOOGLE_APPLICATION_CREDENTIALS=$KeyFile`n"
    Add-Content -Path $EnvFile -Value $newLine
    Write-Success "Added GOOGLE_APPLICATION_CREDENTIALS to .env"
}

# Verify setup
Write-Step "Verifying authentication..."
$env:GOOGLE_APPLICATION_CREDENTIALS = $KeyFile

Write-Success "Service account setup complete!"

Write-Host 'Setup complete!' -ForegroundColor Green
