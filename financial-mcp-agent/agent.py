
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset,StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import StdioServerParameters
import os

# Set the API key as an environment variable expected by mcp-remote
os.environ["X_API_KEY"] = "f2659e73-510e-4623-8ddd-4533ce371c73"

root_agent = LlmAgent(
    model="gemini-2.5-pro",
    name="financial_datasets_agent",
    instruction="""
    You are an autonomous agent interacting with Financial Datasets API via MCP.
    Use the provided MCP tools for fetching financial data and answering queries.
    """,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.financialdatasets.ai/api",
                headers={"X-API-KEY": "f2659e73-510e-4623-8ddd-4533ce371c73"}
            )
        )
    ],
    description="Agent to interact with Financial Datasets MCP remote server"
)




