# MCP Agent with Google ADK

This agent is built using [Google ADK](https://google.github.io/adk-docs/).

## MCP Creation
- The MCP (Model Context Protocol) was created from scratch.
- Source repo: [mcp-creation](https://github.com/Dronanaik/mcp-creation.git)

## Deployment
- The MCP is deployed on [Alpic.ai](https://alpic.ai/).
- **Sign in** with your GitHub account and deploy your MCP.

## Setting Up MCP in Google ADK
1. **Install Google ADK**
   ```bash
   pip install google-adk
   ```
2. **Set up your MCP as a tool in ADK:**
   ```python
   from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

   tools = [
       MCPToolset(
           connection_params=StreamableHTTPConnectionParams(
               url="https://your-mcp.alpic.live/",
               timeout=60.0  # Adjust timeout if needed
           )
       )
   ]
   ```
3. **Run ADK Web**
   ```bash
   adk web
   ```
4. **Call your MCP tools**
   - Use the ADK web interface to send commands to your MCP tools.

## Summary
- Build your MCP.
- Deploy on Alpic.ai.
- Integrate with Google ADK as shown above.
- Run and interact with your MCP via the ADK web interface.

---
For more details, refer to the official [Google ADK documentation](https://google.github.io/adk-docs/) and [Alpic.ai](https://alpic.ai/).
