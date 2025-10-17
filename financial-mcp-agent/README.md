# Financial MCP Agent

## Overview
This package provides a `google.adk` `LlmAgent` configured to interact with the Financial Datasets MCP remote server via HTTP streaming.

## Folder Structure
```text
financial_agent
|_____agent.py
|_____ .env
|_____ __init__.py
```
## Setup .env file 
```text
    GOOGLE_API_KEY="YOUR_api_key"
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    FINANCIAL_DATASETS_API_KEY="your api key"
```

## Requirements
- **Python**: 3.10+
- **Dependencies**: `google-adk` and its MCP tooling stack available in the runtime environment
- **Network access**: Ability to reach `https://mcp.financialdatasets.ai/api`

## Configuration
1. Obtain a valid Financial Datasets API key.
2. Export it as `X_API_KEY` in your shell before starting any ADK session:
   ```bash
   export X_API_KEY="<your-api-key>"
   ```
3. If you need to use multiple environments, consider injecting the key at runtime instead of editing `agent.py` directly.

## Usage 
```python

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset,StreamableHTTPConnectionParams

root_agent = LlmAgent(
    model="gemini-2.5-pro",
    name="financial_datasets_agent",
    instruction="""
    You are an autonomous agent interacting with Financial Datasets API via MCP.
    Use the provided MCP tools for fetching financial data and answering queries..........
    """,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp.financialdatasets.ai/api",
                headers={"X-API-KEY": "<your-api-key>"}
            )
        )
    ],
    description="Agent to interact with Financial Datasets MCP remote server"
)
```

## Customization
- **Model**: Update the `model` field in `agent.py:11` to switch to a different GenAI backend available in your Google ADK setup.
- **Instruction**: Adjust the multi-line `instruction` block in `agent.py:14-16` to tailor agent guidance for your workflows.
- **Tooling**: Modify the `MCPToolset` configuration in `agent.py:18-23` to point at alternate MCP remotes or to add additional tools.
