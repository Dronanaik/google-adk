"""Example usage of the Test Data Generator Agent.

This script demonstrates how to use the agent programmatically.
"""

import asyncio
import os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import root_agent

# Load environment variables
load_dotenv()

# Configuration
APP_NAME = "test_data_generator"
USER_ID = "example_user"
SESSION_ID = "example_session"


async def setup_session_and_runner():
    """Set up the session and runner for the agent."""
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    return session, runner


async def call_agent(query: str):
    """Call the agent with a query and print the response."""
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    
    events = runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    )
    
    async for event in events:
        if event.is_final_response():
            response = event.content.parts[0].text
            print("Agent Response:")
            print(response)
            print()


async def main():
    """Run example queries."""
    print("\n" + "="*80)
    print("Test Data Generator Agent - Example Usage")
    print("="*80)
    
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠️  ERROR: GOOGLE_API_KEY not found in environment variables!")
        print("Please set your API key in the .env file or environment.")
        print("Get your API key from: https://aistudio.google.com/apikey")
        return
    
    # Example 1: Generate user profiles
    await call_agent("Generate 3 user profiles for testing")
    
    # Example 2: Generate emails
    await call_agent("I need 5 email addresses with domain testcompany.com")
    
    # Example 3: Generate business data
    await call_agent("Create 3 invoices with multiple items")
    
    # Example 4: Generate numeric data
    await call_agent("Generate 10 random dates in December 2024")
    
    # Example 5: Generate custom pattern
    await call_agent("Generate 5 strings matching the pattern [A-Z]{3}-\\d{4}")
    
    # Example 6: Generate structured data
    await call_agent(
        "Generate JSON data with 5 records. Each record should have: "
        "id (uuid), name (name), email (email), age (integer), active (boolean)"
    )
    
    print("\n" + "="*80)
    print("Examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
