# Kiota Setup Guide for Orkhon Project

## ✅ What's Already Done

1. **Kiota CLI Installed** - Kiota is installed as a .NET global tool
2. **Poetry Dependencies Added** - All Kiota runtime packages are in `pyproject.toml`:
   - `microsoft-kiota-abstractions`
   - `microsoft-kiota-http`
   - `microsoft-kiota-serialization-json`
   - `microsoft-kiota-serialization-text`
   - `microsoft-kiota-serialization-form`
   - `microsoft-kiota-serialization-multipart`

3. **Three Python Clients Generated**:
   - `backend/clients/dnb-echo/` - DNB Echo API
   - `backend/clients/dnb-public-register/` - DNB Public Register API
   - `backend/clients/dnb-statistics/` - DNB Statistics API

4. **Test Script Created** - `backend/clients/test_dnb_clients.py`
5. **Documentation** - `backend/clients/README.md`

## 🚀 Quick Start

### 1. Set Your API Key

```powershell
# PowerShell
$env:DNB_SUBSCRIPTION_KEY_DEV = "your-dev-api-key-here"
```

### 2. Run the Test Script

```powershell
# From project root
poetry run python backend/clients/test_dnb_clients.py
```

Expected output:
```
=== Testing DNB Echo API ===
✓ Echo API response: ...

=== Testing DNB Statistics API ===
✓ Statistics metadata retrieved (tables: X)
✓ Statistics data retrieved: ...

=== Testing DNB Public Register API ===
✓ Public Register publications search completed: ...

=== All tests completed ===
```

## 🔄 Regenerating Clients

### Using the Generation Script (Recommended)

```powershell
# Generate all clients
.\backend\clients\generate-dnb-clients.ps1

# Clean and regenerate all clients
.\backend\clients\generate-dnb-clients.ps1 -Clean

# Generate only a specific client
.\backend\clients\generate-dnb-clients.ps1 -ClientName echo
.\backend\clients\generate-dnb-clients.ps1 -ClientName public-register
.\backend\clients\generate-dnb-clients.ps1 -ClientName statistics
```

### Manual Generation

If you prefer to run Kiota commands directly:

```powershell
# Echo API
kiota generate -l python -c DnbEchoClient -n dnb_echo_client `
  -d backend/apis/dnb/specs/openapi3-echo-api.yaml `
  -o backend/clients/dnb-echo --exclude-backward-compatible

# Public Register API
kiota generate -l python -c DnbPublicRegisterClient -n dnb_public_register_client `
  -d backend/apis/dnb/specs/openapi3_publicdatav1.yaml `
  -o backend/clients/dnb-public-register --exclude-backward-compatible

# Statistics API
kiota generate -l python -c DnbStatisticsClient -n dnb_statistics_client `
  -d backend/apis/dnb/specs/openapi3_statisticsdatav2024100101.yaml `
  -o backend/clients/dnb-statistics --exclude-backward-compatible
```

## 📖 Using the Clients in Your Code

```python
import asyncio
import sys
from pathlib import Path

# Add client to path
clients_dir = Path("backend/clients")
sys.path.insert(0, str(clients_dir / "dnb-echo"))

from dnb_echo_client import DnbEchoClient
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from kiota_abstractions.authentication.api_key_authentication_provider import (
    ApiKeyAuthenticationProvider,
)

# Create auth provider
class DnbApiKeyAuthProvider(ApiKeyAuthenticationProvider):
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            key_name="Ocp-Apim-Subscription-Key",
            location=ApiKeyAuthenticationProvider.KeyLocation.Header,
        )

async def main():
    auth = DnbApiKeyAuthProvider("your-api-key")
    adapter = HttpxRequestAdapter(auth)
    client = DnbEchoClient(adapter)
    
    result = await client.helloworld.get()
    print(result)

asyncio.run(main())
```

## 🛠️ Kiota Commands Reference

### Get Info About Dependencies
```powershell
kiota info -d backend/apis/dnb/specs/openapi3-echo-api.yaml -l python
```

### Generate with Filtering
```powershell
# Include specific paths only
kiota generate -l python -c MyClient -n my_client `
  -d spec.yaml -o output `
  --include-path "**/specific/path/**" `
  --exclude-backward-compatible

# Exclude specific paths
kiota generate -l python -c MyClient -n my_client `
  -d spec.yaml -o output `
  --exclude-path "**/admin/**" `
  --exclude-backward-compatible
```

### Show Generated Client Info
```powershell
kiota show -d backend/clients/dnb-echo/kiota-lock.json
```

## 📚 Resources

- [Kiota Python Quickstart](https://learn.microsoft.com/en-us/openapi/kiota/quickstarts/python)
- [Kiota CLI Reference](https://learn.microsoft.com/en-us/openapi/kiota/using)
- [DNB API Documentation](https://api.dnb.nl/)

## 🐛 Troubleshooting

### "Filename too long" error when committing (Windows)
**Problem**: Git shows `error: Filename too long` when trying to commit generated clients.

**Solution**: Enable long path support in Git:
```powershell
git config --global core.longpaths true
git config core.longpaths true
```

This is required on Windows because Kiota generates deeply nested directory structures from OpenAPI specs.

### "Module not found" errors
Make sure you're using Poetry to run:
```powershell
poetry run python your_script.py
```

### Authentication failures
Verify your API key:
```powershell
echo $env:DNB_SUBSCRIPTION_KEY_DEV
```

### Regeneration fails
Clean the output directory first:
```powershell
Remove-Item -Recurse -Force backend/clients/dnb-echo
kiota generate ...
```
