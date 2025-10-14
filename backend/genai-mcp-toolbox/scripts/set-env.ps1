# ============================================================================
# Environment Selection Script (PowerShell)
# ============================================================================
# Usage: .\scripts\set-env.ps1 -Environment dev|prod

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "prod")]
    [string]$Environment = "dev"
)

$envFile = ".env"

# Update DNB_ENVIRONMENT in .env
(Get-Content $envFile) -replace "^DNB_ENVIRONMENT=.*", "DNB_ENVIRONMENT=$Environment" | Set-Content $envFile

# Load and export environment-specific variables
$envContent = Get-Content $envFile | ConvertFrom-StringData

if ($Environment -eq "dev") {
    $env:DNB_SUBSCRIPTION_KEY = $envContent.DNB_SUBSCRIPTION_KEY_DEV
    $env:DNB_SUBSCRIPTION_NAME = $envContent.DNB_SUBSCRIPTION_NAME_DEV
} else {
    $env:DNB_SUBSCRIPTION_KEY = $envContent.DNB_SUBSCRIPTION_KEY_PROD
    $env:DNB_SUBSCRIPTION_NAME = $envContent.DNB_SUBSCRIPTION_NAME_PROD
}

Write-Host "✓ Environment set to: $Environment" -ForegroundColor Green
Write-Host "  - Subscription Key: $($env:DNB_SUBSCRIPTION_KEY.Substring(0,10))..." -ForegroundColor Gray
Write-Host "  - Subscription Name: $env:DNB_SUBSCRIPTION_NAME" -ForegroundColor Gray