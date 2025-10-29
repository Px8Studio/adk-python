#!/usr/bin/env python3
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

"""Development test runner for the data science coordinator agent.

⚠️  DEVELOPMENT ONLY - NOT FOR PRODUCTION USE

This script provides direct access to the data science coordinator for faster
development iteration. In production, access should go through the integrated
root_agent which handles multi-domain routing.

Purpose:
  - Rapid testing of data science features in isolation
  - Faster development cycles (bypasses root_agent routing)
  - Debugging data science-specific functionality

Production Usage:
  Use run_root_agent.py or adk web for the full integrated system.

Usage:
    # Interactive CLI mode
    python backend/adk/run_data_science_agent.py

    # Single query mode
    python backend/adk/run_data_science_agent.py --query "What data do you have?"
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from .env file
env_file = backend_dir / "adk" / "agents" / "data_science" / ".env"
if env_file.exists():
  load_dotenv(env_file)
  print(f"✓ Loaded environment from {env_file}")
else:
  print(f"⚠ Warning: .env file not found at {env_file}")
  print("  Copy .env.example to .env and configure your settings")

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def run_interactive() -> None:
  """Run the agent in interactive CLI mode (development testing only)."""
  from google.adk.runners import Runner
  from adk.agents.data_science import data_science_coordinator

  logger.info("Starting Data Science Coordinator (DEVELOPMENT MODE)")
  logger.info("Type 'quit' or 'exit' to stop")

  runner = Runner(data_science_coordinator)

  print("\n" + "=" * 70)
  print("⚠️  DEVELOPMENT MODE - Data Science Coordinator")
  print("=" * 70)
  print("\nThis is a test runner for development only.")
  print("Production usage should go through the integrated root_agent.")
  print("\nAvailable capabilities:")
  print("  • BigQuery data access via natural language")
  print("  • Python data analysis and visualization")
  print("  • Multi-step query planning and execution")
  print("\nType your questions or 'quit' to exit")
  print("=" * 70 + "\n")

  while True:
    try:
      user_input = input("You: ").strip()

      if user_input.lower() in ["quit", "exit", "q"]:
        print("\nGoodbye! 👋")
        break

      if not user_input:
        continue

      print("\nAgent: ", end="", flush=True)
      response = runner.run(user_input)

      # Handle different response types
      if hasattr(response, "content"):
        print(response.content)
      else:
        print(response)

      print()  # Add blank line for readability

    except KeyboardInterrupt:
      print("\n\nGoodbye! 👋")
      break
    except Exception as e:  # pylint: disable=broad-except
      logger.error("Error processing query: %s", e, exc_info=True)
      print(f"\n❌ Error: {e}\n")


def run_single_query(query: str) -> None:
  """Run a single query and exit (development testing only).

  Args:
    query: The question to ask the agent
  """
  from google.adk.runners import Runner
  from adk.agents.data_science import data_science_coordinator

  logger.info("Running single query (DEVELOPMENT MODE): %s", query)

  runner = Runner(data_science_coordinator)

  print(f"\n{'=' * 70}")
  print(f"Query: {query}")
  print(f"{'=' * 70}\n")

  try:
    response = runner.run(query)

    print("Response:")
    print("-" * 70)
    if hasattr(response, "content"):
      print(response.content)
    else:
      print(response)
    print("-" * 70 + "\n")

  except Exception as e:  # pylint: disable=broad-except
    logger.error("Error processing query: %s", e, exc_info=True)
    print(f"❌ Error: {e}")
    sys.exit(1)


def main() -> None:
  """Main entry point for the development test runner."""
  parser = argparse.ArgumentParser(
      description="Development test runner for Data Science Coordinator",
      formatter_class=argparse.RawDescriptionHelpFormatter,
      epilog="""
⚠️  DEVELOPMENT ONLY - NOT FOR PRODUCTION USE

This script is for development/testing of data science features in isolation.
Production usage should access the data science coordinator through the
integrated root_agent.

Examples:
  # Interactive mode
  python backend/adk/run_data_science_agent.py

  # Single query mode
  python backend/adk/run_data_science_agent.py --query "What data do you have?"

For production, use:
  python backend/adk/run_root_agent.py
  # or
  adk web --agents-dir backend/adk/agents
      """,
  )

  parser.add_argument(
      "--query",
      "-q",
      type=str,
      help="Run a single query and exit (instead of interactive mode)",
  )

  parser.add_argument(
      "--env-file",
      type=str,
      help="Path to .env file (default: backend/adk/agents/data_science/.env)",
  )

  args = parser.parse_args()

  # Load custom env file if specified
  if args.env_file:
    custom_env = Path(args.env_file)
    if custom_env.exists():
      load_dotenv(custom_env)
      print(f"✓ Loaded environment from {custom_env}")
    else:
      print(f"❌ Error: .env file not found at {custom_env}")
      sys.exit(1)

  # Validate required environment variables
  required_vars = ["GOOGLE_CLOUD_PROJECT", "BQ_DATA_PROJECT_ID", "BQ_DATASET_ID"]
  missing_vars = [var for var in required_vars if not os.getenv(var)]

  if missing_vars:
    print("❌ Error: Missing required environment variables:")
    for var in missing_vars:
      print(f"  • {var}")
    print("\nPlease configure your .env file")
    sys.exit(1)

  # Run in appropriate mode
  if args.query:
    run_single_query(args.query)
  else:
    run_interactive()


if __name__ == "__main__":
  main()
