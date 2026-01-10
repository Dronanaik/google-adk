from google.adk.agents.llm_agent import Agent
from .subagents.jira_agent.agent import jira_agent
from .subagents.xray_agent.agent import xray_agent
import os
from dotenv import load_dotenv  


load_dotenv()
model = os.getenv("GOOGLE_MODEL_NAME")

root_agent = Agent(
    model=model,
    name='XrayAgent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
