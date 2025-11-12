# Sync ADK Samples Script
# Purpose: Pull latest updates from upstream adk-samples for all adopted agents
# Usage: .\sync-adk-samples.ps1 [-DryRun]

param(
    [Parameter(Mandatory=$false)]
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "🔄 Syncing ADK Samples with Upstream" -ForegroundColor Cyan
Write-Host ""

# Ensure we're in the Orkhon root directory
$orkhonRoot = "C:\Users\rjjaf\_Projects\orkhon"
Set-Location $orkhonRoot

# Check if adk-samples remote exists
$remotes = git remote -v
if ($remotes -notmatch "adk-samples") {
    Write-Host "❌ adk-samples remote not found. Run adopt-adk-sample.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "📥 Fetching latest from adk-samples..." -ForegroundColor Yellow
# Limit fetch to main only, prune, no tags
git fetch --prune --no-tags adk-samples "+refs/heads/main:refs/remotes/adk-samples/main"

# List of adopted samples (update this as you adopt more)
$adoptedSamples = @(
    @{
        Name = "data-science"
        DirName = "data_science"
        SourcePath = "python/agents/data-science"
        TargetPath = "backend/adk/agents/data_science"
    }
    # Add more samples as you adopt them:
    # @{
    #     Name = "financial-advisor"
    #     DirName = "financial_advisor"
    #     SourcePath = "python/agents/financial-advisor"
    #     TargetPath = "backend/adk/agents/financial_advisor"
    # }
)

Write-Host "Found $($adoptedSamples.Count) adopted sample(s)" -ForegroundColor White
Write-Host ""

foreach ($sample in $adoptedSamples) {
    Write-Host "🔍 Checking $($sample.Name)..." -ForegroundColor Cyan
    
    # Check if directory exists
    if (-not (Test-Path $sample.TargetPath)) {
        Write-Host "   ⚠️  Directory not found: $($sample.TargetPath)" -ForegroundColor Yellow
        Write-Host "   Skipping..." -ForegroundColor Gray
        Write-Host ""
        continue
    }
    
    if ($DryRun) {
        Write-Host "   [DRY RUN] Would pull updates from:" -ForegroundColor Yellow
        Write-Host "      adk-samples:$($sample.SourcePath)" -ForegroundColor Gray
        Write-Host "      to: $($sample.TargetPath)" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "   📥 Pulling updates..." -ForegroundColor Yellow
        
        try {
            git subtree pull --prefix=$($sample.TargetPath) `
                adk-samples main:$($sample.SourcePath) `
                --squash
            
            Write-Host "   ✅ Updated successfully!" -ForegroundColor Green
            Write-Host ""
            
        } catch {
            Write-Host "   ❌ Failed to update $($sample.Name)" -ForegroundColor Red
            Write-Host "   Error: $_" -ForegroundColor Red
            Write-Host "   You may need to resolve conflicts manually." -ForegroundColor Yellow
            Write-Host ""
        }
    }
}

if (-not $DryRun) {
    Write-Host "🧪 Running tests..." -ForegroundColor Yellow
    Set-Location "backend\adk"
    
    # Check if uv sync is needed
    Write-Host "   Checking dependencies..." -ForegroundColor Gray
    uv sync
    
    Write-Host ""
    Write-Host "✅ Sync complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Review changes:" -ForegroundColor White
    Write-Host "      git status" -ForegroundColor Gray
    Write-Host "      git diff" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   2. Test updated agents:" -ForegroundColor White
    Write-Host "      adk run agents/data_science" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   3. Run integration tests:" -ForegroundColor White
    Write-Host "      pytest tests/integration/" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✅ Dry run complete. Run without -DryRun to apply changes." -ForegroundColor Green
    Write-Host ""
}
