"""
Test script for DNB API clients generated with Kiota.

This script demonstrates how to use the generated clients with the DNB APIs.
You'll need to set the DNB_SUBSCRIPTION_KEY environment variable.
"""
from __future__ import annotations

import asyncio
import os
from typing import Any

from kiota_abstractions.authentication.api_key_authentication_provider import (
    ApiKeyAuthenticationProvider,
)
from kiota_abstractions.authentication.authentication_provider import (
    AuthenticationProvider,
)
from kiota_http.httpx_request_adapter import HttpxRequestAdapter

# Import generated clients
import sys
from pathlib import Path

# Add client directories to path
clients_dir = Path(__file__).parent
sys.path.insert(0, str(clients_dir / "dnb-echo"))
sys.path.insert(0, str(clients_dir / "dnb-public-register"))
sys.path.insert(0, str(clients_dir / "dnb-statistics"))

from dnb_echo_client import DnbEchoClient
from dnb_public_register_client import DnbPublicRegisterClient
from dnb_statistics_client import DnbStatisticsClient


class DnbApiKeyAuthProvider(ApiKeyAuthenticationProvider):
  """Custom auth provider for DNB APIs that uses Ocp-Apim-Subscription-Key header."""

  def __init__(self, api_key: str):
    super().__init__(
        api_key=api_key,
        key_name="Ocp-Apim-Subscription-Key",
        location=ApiKeyAuthenticationProvider.KeyLocation.Header,
    )


async def test_echo_client(auth_provider: AuthenticationProvider) -> None:
  """Test the DNB Echo API client."""
  print("\n=== Testing DNB Echo API ===")
  request_adapter = HttpxRequestAdapter(auth_provider)
  client = DnbEchoClient(request_adapter)

  try:
    # Test the helloworld endpoint
    result = await client.helloworld.get()
    print(f"✓ Echo API response: {result}")
  except Exception as e:
    print(f"✗ Echo API error: {e}")


async def test_statistics_client(auth_provider: AuthenticationProvider) -> None:
  """Test the DNB Statistics API client."""
  print("\n=== Testing DNB Statistics API ===")
  request_adapter = HttpxRequestAdapter(auth_provider)
  client = DnbStatisticsClient(request_adapter)

  try:
    # Get metadata
    metadata = await client.metadata.get()
    print(f"✓ Statistics metadata retrieved (tables: {len(metadata.tables) if metadata.tables else 0})")

    # Get sample data (limited to 5 records)
    data_response = await client.data.get(
        query_parameters={"limit": 5}
    )
    print(f"✓ Statistics data retrieved: {data_response}")
  except Exception as e:
    print(f"✗ Statistics API error: {e}")


async def test_public_register_client(auth_provider: AuthenticationProvider) -> None:
  """Test the DNB Public Register API client."""
  print("\n=== Testing DNB Public Register API ===")
  request_adapter = HttpxRequestAdapter(auth_provider)
  client = DnbPublicRegisterClient(request_adapter)

  try:
    # Search for publications
    search_params = {
        "languageCode": "NL",
        "RegisterCode": "WFTAF",
        "page": 1,
        "pageSize": 5,
    }
    publications = await client.publicregister.publications.search.post(
        body=search_params
    )
    print(f"✓ Public Register publications search completed: {publications}")
  except Exception as e:
    print(f"✗ Public Register API error: {e}")


async def main() -> None:
  """Run all client tests."""
  # Get API key from environment
  api_key = os.getenv("DNB_SUBSCRIPTION_KEY") or os.getenv("DNB_SUBSCRIPTION_KEY_DEV")
  
  if not api_key:
    print("ERROR: DNB_SUBSCRIPTION_KEY or DNB_SUBSCRIPTION_KEY_DEV environment variable not set")
    print("Please set one of these variables and try again.")
    return

  # Create auth provider
  auth_provider = DnbApiKeyAuthProvider(api_key)

  # Run all tests
  await test_echo_client(auth_provider)
  await test_statistics_client(auth_provider)
  await test_public_register_client(auth_provider)

  print("\n=== All tests completed ===")


if __name__ == "__main__":
  asyncio.run(main())
