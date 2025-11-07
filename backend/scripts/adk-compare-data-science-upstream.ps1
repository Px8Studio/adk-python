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

Write-Host "📥 Fetching from adk-samples remote..." -ForegroundColor Cyan
git fetch adk-samples

Write-Host ""
Write-Host "📊 File differences between local and upstream:" -ForegroundColor Cyan
Write-Host ""

git diff --stat HEAD adk-samples/main -- python/agents/data-science

Write-Host ""
Write-Host "💡 Use 'git diff HEAD adk-samples/main -- python/agents/data-science/<file>' for detailed diff" -ForegroundColor Yellow
