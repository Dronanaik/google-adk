# pyright: reportMissingImports=false

from google.adk.agents import LlmAgent
# Corrected import to include StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import StdioServerParameters
import sys

# Create the LlmAgent
root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="playwright_agent",
    instruction="""
    You are an expert web automation assistant. Your goal is to use the Playwright tools to fulfill user requests that require browser interaction.

    Follow these steps carefully:
    1.  **Navigate**: Use the `playwright.goto(url=...)` tool to navigate to the website specified by the user.
    2.  **Interact & Extract**: Analyze the user's prompt to understand what information needs to be extracted or what actions need to be performed. Use the `playwright.page_content()` tool to get the current state of the page and decide on the next action.
    3.  **Respond**: Once you have successfully extracted the information, present it clearly to the user. If you cannot fulfill the request, explain why.

    Always think step-by-step and use the tools provided.
    """,
    tools=[
        MCPToolset(
            # Use StdioConnectionParams to set a timeout
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["@playwright/mcp@latest"],
                    timeout_sec=120.0
                ),
                # Set a longer timeout in seconds (e.g., 60 seconds)
                timeout=60.0
            )
        )
    ],
    description="You are an playwrite NLP agent"
)