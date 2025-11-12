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

Write-Host "[>] Fetching from adk-samples remote..." -ForegroundColor Cyan
# Fetch only main to prevent all branches from being tracked
git fetch --prune --no-tags adk-samples "+refs/heads/main:refs/remotes/adk-samples/main"

Write-Host ""
Write-Host "[~] Pulling updates for data-science agent..." -ForegroundColor Cyan
Write-Host ""

# Fix: git subtree pull requires the full remote reference
git subtree pull --prefix=backend/adk/agents/data-science adk-samples main --squash

if ($LASTEXITCODE -eq 0) {
  Write-Host ""
  Write-Host "[+] Update complete! Review changes and test agent." -ForegroundColor Green
  Write-Host ""
  Write-Host "Next steps:" -ForegroundColor Cyan
  Write-Host "  1. Review changes: git log -p --since='1 hour ago' backend/adk/agents/data-science"
  Write-Host "  2. Test agent: cd backend/adk; uv sync; uv run adk run agents/data-science"
  Write-Host "  3. Commit if satisfied: git add .; git commit -m 'chore(adk): Update data-science agent from upstream'"
} else {
  Write-Host ""
  Write-Host "[!] Update failed - see errors above" -ForegroundColor Red
  exit 1
}

