import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from .tools.resume_ingest import ingest_resume
from .tools.info_extract import extract_profile
from .tools.job_search import search_jobs
from .tools.schema import format_results


root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="job_search_agent",
    description=(
        "Advanced Job Search Assistant that ingests a resume, extracts a profile, "
        "searches multiple job sources, and returns structured JSON results."
    ),
    instruction=(
        "You are a precise Job Search Assistant.\n"
        "- If a resume path is provided, call ingest_resume(file_path).\n"
        "- Then call extract_profile(text) using the returned text.\n"
        "- Use the Playwright MCP browser tools to search and open listings on naukri.com, linkedin.com, and wellfound.com, extract role title, company, location, remote flag, posted date, salary (if available), and apply URL.\n"
        "- If browsing yields results, assemble them and skip SerpAPI entirely.\n"
        "- If needed as fallback, call search_jobs(profile_json, location, remote) with profile_json as a JSON string.\n"
        "- Finally, call format_results(profile_result_json, search_result_json) with JSON strings to return ONLY the final JSON. Ask for a resume path if missing."
    ),
    tools=[
        ingest_resume,
        extract_profile,
        # Playwright MCP server (npm) for browsing job boards
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@playwright/mcp@latest",
                    ],
                ),
                timeout=60.0,
            ),
        ),
        search_jobs,
        format_results,
    ],
)


