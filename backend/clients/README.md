# DNB API Clients (Kiota-generated)

This directory contains Python HTTP clients for the DNB APIs, generated using the [Kiota](https://learn.microsoft.com/en-us/openapi/kiota/overview) tool.

## 📁 Directory Structure

```
backend/clients/
├── dnb-echo/              # DNB Echo API client
├── dnb-public-register/   # DNB Public Register API client
├── dnb-statistics/        # DNB Statistics API client
├── test_dnb_clients.py    # Test script for all clients
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** managed by Poetry
- **DNB API Key** stored in `.env` file in project root

All Kiota runtime dependencies are managed by Poetry in the root `pyproject.toml`.

### Environment Setup

Your API keys are loaded automatically from the `.env` file:

```ini
# In C:\Users\rjjaf\_Projects\orkhon\.env
DNB_SUBSCRIPTION_KEY_DEV=your-dev-key-here
DNB_SUBSCRIPTION_KEY_PROD=your-prod-key-here
DNB_ENVIRONMENT=dev  # or 'prod'
```

### Running the Test Script

```powershell
# From project root
poetry run python backend/clients/test_dnb_clients.py
```

## 📖 Usage Examples

### Echo API

```python
import asyncio
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from backend.clients.dnb_echo_client.dnb_echo_client import DnbEchoClient

async def test_echo():
    auth_provider = DnbApiKeyAuthProvider(api_key)
    request_adapter = HttpxRequestAdapter(auth_provider)
    client = DnbEchoClient(request_adapter)
    
    result = await client.helloworld.get()
    print(result)

asyncio.run(test_echo())
```

### Statistics API

```python
import asyncio
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from backend.clients.dnb_statistics_client.dnb_statistics_client import DnbStatisticsClient

async def get_metadata():
    auth_provider = DnbApiKeyAuthProvider(api_key)
    request_adapter = HttpxRequestAdapter(auth_provider)
    client = DnbStatisticsClient(request_adapter)
    
    # Get metadata
    metadata = await client.metadata.get()
    print(f"Available tables: {len(metadata.tables)}")
    
    # Query data with filters
    data = await client.data.get(query_parameters={"limit": 10})
    print(data)

asyncio.run(get_metadata())
```

### Public Register API

```python
import asyncio
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from backend.clients.dnb_public_register_client.dnb_public_register_client import (
    DnbPublicRegisterClient,
)

async def search_publications():
    auth_provider = DnbApiKeyAuthProvider(api_key)
    request_adapter = HttpxRequestAdapter(auth_provider)
    client = DnbPublicRegisterClient(request_adapter)
    
    search_params = {
        "languageCode": "NL",
        "RegisterCode": "WFTAF",
        "page": 1,
        "pageSize": 10,
    }
    
    publications = await client.publicregister.publications.search.post(
        body=search_params
    )
    print(publications)

asyncio.run(search_publications())
```

## 🔧 Regenerating Clients

### Automated Script (Recommended)

Use the included PowerShell script to regenerate clients:

```powershell
# Generate all clients
.\backend\clients\generate-dnb-clients.ps1

# Clean existing clients and regenerate
.\backend\clients\generate-dnb-clients.ps1 -Clean

# Generate only a specific client
.\backend\clients\generate-dnb-clients.ps1 -ClientName echo
```

### Manual Commands

If the OpenAPI specs are updated, you can also regenerate manually:

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

## 🔐 Authentication

All DNB APIs use API key authentication via the `Ocp-Apim-Subscription-Key` header. The `DnbApiKeyAuthProvider` class in `test_dnb_clients.py` demonstrates how to configure this.

```python
from kiota_abstractions.authentication.api_key_authentication_provider import (
    ApiKeyAuthenticationProvider,
)

class DnbApiKeyAuthProvider(ApiKeyAuthenticationProvider):
    def __init__(self, api_key: str):
        super().__init__(
            api_key=api_key,
            key_name="Ocp-Apim-Subscription-Key",
            location=ApiKeyAuthenticationProvider.KeyLocation.Header,
        )
```

## 📚 Resources

- [Kiota Documentation](https://learn.microsoft.com/en-us/openapi/kiota/)
- [Kiota Python Quickstart](https://learn.microsoft.com/en-us/openapi/kiota/quickstarts/python)
- [DNB API Documentation](https://api.dnb.nl/)

## 🐛 Troubleshooting

### "Filename too long" Git Error (Windows)

If you encounter `error: Filename too long` when committing, enable Git long path support:

```powershell
git config --global core.longpaths true
git config core.longpaths true
```

This is necessary on Windows due to the deeply nested directory structures Kiota generates.

### Import Errors

Make sure you're in the Poetry virtual environment:

```bash
poetry shell
```

### Missing Dependencies

If Kiota dependencies are missing:

```bash
poetry install
```

### Authentication Errors

Verify your API key is set correctly:

```powershell
echo $env:DNB_SUBSCRIPTION_KEY
```
