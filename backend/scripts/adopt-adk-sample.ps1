# Script: adopt-adk-sample.ps1
# Purpose: Import an ADK sample agent via git subtree
# Usage: .\adopt-adk-sample.ps1 -SampleName "data-science"

param(
    [Parameter(Mandatory=$true)]
    [string]$SampleName,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Configuration
$ORKHON_ROOT = "C:\Users\rjjaf\_Projects\orkhon"
$ADK_SAMPLES_REMOTE = "adk-samples"
$ADK_SAMPLES_URL = "https://github.com/google/adk-samples.git"

# Target paths
$TARGET_PREFIX = "backend/adk/agents/$SampleName"
$SOURCE_PATH = "python/agents/$SampleName"

Write-Host "🚀 ADK Sample Adoption Tool" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Sample: $SampleName"
Write-Host "Target: $TARGET_PREFIX"
Write-Host ""

# Change to Orkhon root
Push-Location $ORKHON_ROOT

try {
    # Step 1: Check if remote exists, add if not
    Write-Host "📡 Step 1: Checking git remote..." -ForegroundColor Yellow
    $remotes = git remote
    if ($remotes -notcontains $ADK_SAMPLES_REMOTE) {
        Write-Host "Adding remote '$ADK_SAMPLES_REMOTE'..." -ForegroundColor Yellow
        if (-not $DryRun) {
            git remote add $ADK_SAMPLES_REMOTE $ADK_SAMPLES_URL
            git fetch $ADK_SAMPLES_REMOTE
        }
        Write-Host "✅ Remote added successfully" -ForegroundColor Green
    } else {
        Write-Host "✅ Remote already exists" -ForegroundColor Green
        Write-Host "Fetching latest changes..." -ForegroundColor Yellow
        if (-not $DryRun) {
            git fetch $ADK_SAMPLES_REMOTE
        }
    }
    
    # Step 2: Check if sample exists in adk-samples
    Write-Host ""
    Write-Host "🔍 Step 2: Verifying sample exists in adk-samples..." -ForegroundColor Yellow
    $sampleExists = git ls-tree -r $ADK_SAMPLES_REMOTE/main --name-only | Select-String "^$SOURCE_PATH/"
    if (-not $sampleExists) {
        throw "Sample '$SampleName' not found at $SOURCE_PATH in adk-samples repository"
    }
    Write-Host "✅ Sample exists in upstream" -ForegroundColor Green
    
    # Step 3: Check if already imported
    Write-Host ""
    Write-Host "📋 Step 3: Checking if sample already imported..." -ForegroundColor Yellow
    if (Test-Path $TARGET_PREFIX) {
        Write-Host "⚠️  WARNING: $TARGET_PREFIX already exists" -ForegroundColor Red
        $continue = Read-Host "Continue and update? [y/n]"
        if ($continue -ne 'y') {
            Write-Host "Aborted by user" -ForegroundColor Red
            exit 1
        }
        
        # Pull updates instead
        Write-Host "Pulling updates via git subtree..." -ForegroundColor Yellow
        if (-not $DryRun) {
            git subtree pull --prefix=$TARGET_PREFIX `
                $ADK_SAMPLES_REMOTE main:$SOURCE_PATH `
                --squash
        }
        Write-Host "✅ Sample updated successfully" -ForegroundColor Green
    } else {
        # Add new subtree
        Write-Host "Importing sample via git subtree..." -ForegroundColor Yellow
        if (-not $DryRun) {
            git subtree add --prefix=$TARGET_PREFIX `
                $ADK_SAMPLES_REMOTE main:$SOURCE_PATH `
                --squash
        }
        Write-Host "✅ Sample imported successfully" -ForegroundColor Green
    }
    
    # Step 4: Post-import instructions
    Write-Host ""
    Write-Host "✨ Success! Next steps:" -ForegroundColor Green
    Write-Host ""
    Write-Host "1. Review the imported agent:"
    Write-Host "   cd $TARGET_PREFIX"
    Write-Host "   code README.md"
    Write-Host ""
    Write-Host "2. Copy and configure .env file:"
    Write-Host "   cd $TARGET_PREFIX"
    Write-Host "   copy .env.example .env"
    Write-Host "   notepad .env"
    Write-Host ""
    Write-Host "3. Install dependencies:"
    Write-Host "   cd backend/adk"
    Write-Host "   # Merge dependencies from $TARGET_PREFIX/pyproject.toml"
    Write-Host "   uv sync"
    Write-Host ""
    Write-Host "4. Test the agent:"
    Write-Host "   adk run $TARGET_PREFIX"
    Write-Host ""
    Write-Host "5. Commit the changes:"
    Write-Host "   git commit -m 'feat(adk): Import $SampleName from ADK samples'"
    Write-Host "   git push origin dev"
    Write-Host ""
    
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
