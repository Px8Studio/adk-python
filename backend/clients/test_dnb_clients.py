"""
Test script for DNB API clients generated with Kiota.

This script demonstrates how to use the generated clients with the DNB APIs.
It automatically loads API keys from the .env file in the project root.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

from kiota_abstractions.authentication.api_key_authentication_provider import (
    ApiKeyAuthenticationProvider,
    KeyLocation,
)
from kiota_abstractions.authentication.authentication_provider import (
    AuthenticationProvider,
)
from kiota_http.httpx_request_adapter import HttpxRequestAdapter

# Import generated clients using the wrapper modules
# These wrappers handle the sys.path manipulation needed for hyphenated directories
from echo_client import DnbEchoClient
from statistics_client import DnbStatisticsClient
from public_register_client import DnbPublicRegisterClient


class DnbApiKeyAuthProvider(ApiKeyAuthenticationProvider):
  """Custom auth provider for DNB APIs that uses Ocp-Apim-Subscription-Key header."""

  def __init__(self, api_key: str):
    super().__init__(
        key_location=KeyLocation.Header,
        api_key=api_key,
        parameter_name="Ocp-Apim-Subscription-Key",
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
    # Try to get exchange rates data (sample endpoint)
    result = await client.exchange_rates_of_the_euro_and_gold_price_day.get()
    if result:
      print(f"✓ Statistics API - Exchange rates retrieved successfully")
      print(f"  Type: {type(result).__name__}")
    else:
      print(f"✗ Statistics API - No data returned")
  except Exception as e:
    print(f"✗ Statistics API error: {e}")


async def test_public_register_client(auth_provider: AuthenticationProvider) -> None:
  """Test the DNB Public Register API client."""
  print("\n=== Testing DNB Public Register API ===")
  request_adapter = HttpxRequestAdapter(auth_provider)
  client = DnbPublicRegisterClient(request_adapter)

  try:
    # Check available endpoints
    print(f"✓ Public Register client initialized")
    print(f"  Base URL: {client.request_adapter.base_url}")
  except Exception as e:
    print(f"✗ Public Register API error: {e}")


async def main() -> None:
  """Run all client tests."""
  # Get API key from environment (loaded from .env file)
  dnb_env = os.getenv("DNB_ENVIRONMENT", "dev")
  
  if dnb_env == "prod":
    api_key = os.getenv("DNB_SUBSCRIPTION_KEY_PROD")
  else:
    api_key = os.getenv("DNB_SUBSCRIPTION_KEY_DEV")
  
  if not api_key:
    print("ERROR: DNB API key not found in .env file")
    print(f"Looking for: DNB_SUBSCRIPTION_KEY_{dnb_env.upper()}")
    print(f"Please check your .env file at: {env_path}")
    return

  print(f"Using DNB {dnb_env.upper()} environment")
  print(f"API key: {api_key[:8]}..." if api_key else "API key not set")
  print()

  # Create auth provider
  auth_provider = DnbApiKeyAuthProvider(api_key)

  # Run all tests
  await test_echo_client(auth_provider)
  await test_statistics_client(auth_provider)
  await test_public_register_client(auth_provider)

  print("\n=== All tests completed ===")


if __name__ == "__main__":
  asyncio.run(main())
