# Load environment variables from .env file

param(
    [string]$EnvFile = ".env"
)

# Check if .env file exists
if (-not (Test-Path $EnvFile)) {
    Write-Host "Error: $EnvFile file not found" -ForegroundColor Red
    exit 1
}

Write-Host "Loading environment variables from $EnvFile..." -ForegroundColor Green

# Read and parse .env file
Get-Content $EnvFile | ForEach-Object {
    $line = $_.Trim()
    
    # Skip empty lines and comments
    if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith('#')) {
        return
    }
    
    # Parse KEY=VALUE format
    if ($line -match '^([^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        
        # Remove quotes if present
        $value = $value -replace '^[''"]|[''"]$', ''
        
        # Set environment variable
        [Environment]::SetEnvironmentVariable($key, $value, 'Process')
        Write-Host "  Set $key" -ForegroundColor Gray
    }
}

Write-Host "`nEnvironment variables loaded successfully!" -ForegroundColor Green

# Display key variables (without exposing sensitive values)
if ($env:GOOGLE_CLOUD_PROJECT) {
    Write-Host "Project ID: $env:GOOGLE_CLOUD_PROJECT" -ForegroundColor Yellow
}

if ($env:GOOGLE_APPLICATION_CREDENTIALS) {
    Write-Host "Credentials file: $env:GOOGLE_APPLICATION_CREDENTIALS" -ForegroundColor Yellow
}