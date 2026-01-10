
import os
from google.adk.agents import Agent
from google.genai import types
from dotenv import load_dotenv

# Import the new tools and the updated prompt
from .prompts import JIRA_AGENT_PROMPT
from .tools import list_jira_projects, fetch_project_epics

# Load environment variables from a .env file 
load_dotenv()
model = os.getenv("GOOGLE_MODEL_NAME")

# The agent is defined at the top level for Agent Engine deployment
jira_agent = Agent(
    name="jira_agent", 
    model=model,
    description="An agent that can list JIRA projects and fetch epic/issue details from a selected project.",
    
    # The instruction is now clean and flexible, with no hardcoded credentials
    instruction=JIRA_AGENT_PROMPT,
    
    generate_content_config=types.GenerateContentConfig(temperature=0.4),
    
    # The agent now has two tools in its "toolbelt"
    tools=[
        list_jira_projects, 
        fetch_project_epics
    ],
    
    output_key="jira_operations_agent_output"
)

print(f"Agent '{jira_operations_agent.name}' created successfully.")
