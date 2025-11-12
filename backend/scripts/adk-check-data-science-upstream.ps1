#Requires -Version 5.1
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Enforce single-branch tracking for 'adk-samples' to avoid noisy branches
git config --unset-all remote.adk-samples.fetch 2>$null
git config --add remote.adk-samples.fetch "+refs/heads/main:refs/remotes/adk-samples/main"
git config remote.adk-samples.tagOpt "--no-tags"
git config remote.adk-samples.prune "true"

Write-Host "📥 Fetching from adk-samples remote..." -ForegroundColor Cyan
# Fetch only main to prevent all branches from being tracked
git fetch --prune --no-tags adk-samples "+refs/heads/main:refs/remotes/adk-samples/main"

Write-Host ""
Write-Host "📊 Changes in upstream data-science agent:" -ForegroundColor Cyan
Write-Host ""

$changes = git log --oneline --graph HEAD..adk-samples/main -- python/agents/data-science | Select-Object -First 20

if ($changes) {
  $changes
  Write-Host ""
  Write-Host "💡 Run 'ADK: Pull data-science Agent Updates' to apply these changes" -ForegroundColor Yellow
} else {
  Write-Host "✅ No upstream changes found - you are up to date!" -ForegroundColor Green
}

# Example comparison remains on main-only tracking
git diff --stat HEAD adk-samples/main -- python/agents/data-science
