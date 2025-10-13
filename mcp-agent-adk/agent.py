# pyright: reportMissingImports=false
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="greeting_agent",
    instruction="""Greet the user warmly and ask how you can assist them today. using the MCP tools""",
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp-creation-06152dab.alpic.live/",
                timeout=60.0  # Adjust timeout if needed
            )
        )
    ],
    description="You are an Greeting agent"
)
