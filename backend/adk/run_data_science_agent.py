"""Development test runner for Data Science Coordinator.

⚠️ DEVELOPMENT USE ONLY - NOT FOR PRODUCTION
This test runner allows isolated testing of the data science coordinator
without going through the full root_agent workflow.

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
import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# IMPORTANT: Load from PROJECT ROOT, not agent subdirectory
# This follows ADK convention - single .env at project root
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"

if env_file.exists():
  load_dotenv(env_file, override=True)
  print(f"✓ Loaded environment from {env_file}")
else:
  print(f"⚠ Warning: .env file not found at {env_file}")
  print("  Expected location: project_root/.env")
  print("  This is the standard ADK pattern - single .env at project root")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_env():
    """Load environment variables from .env file."""
    # Check for required environment variables
    required_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "BQ_DATA_PROJECT_ID",
        "BQ_COMPUTE_PROJECT_ID",
        "BQ_DATASET_ID",
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"  • {var}")
        logger.error(f"\nPlease configure your .env file at: {env_file}")
        sys.exit(1)


async def run_agent(query: str):
    """Run the data science agent with the given query."""
    try:
        # Import ADK components
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        
        # Import our agent
    from backend.adk.agents.data_science.agent import root_agent  # pylint: disable=import-error
        
        # Create session service
        session_service = InMemorySessionService()
        
        # Create runner
        runner = Runner(
            agent=root_agent,
            session_service=session_service
        )
        
        # Run the query
        logger.info(f"🤖 Running query: {query}")
        response = await runner.run(message=query)
        
        # Print response
        print("\n" + "="*50)
        print("📊 Data Science Agent Response:")
        print("="*50)
        print(response.content if hasattr(response, 'content') else str(response))
        print("="*50 + "\n")
        
        return response
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure ADK is installed: pip install google-adk")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error running agent: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run the Data Science Agent standalone"
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        required=True,
        help="Query to send to the agent"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load environment
    load_env()
    
    # Run the agent
    asyncio.run(run_agent(args.query))


if __name__ == "__main__":
    main()
