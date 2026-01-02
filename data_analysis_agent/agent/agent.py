from google.adk.agents.llm_agent import Agent
from ..utils.db_connector import DatabaseConnector
from ..utils.schema_inspector import SchemaInspector
import os

# Global connector instance (for simplicity in this demo)
# In a real app, this would be managed per session/user
db_connector = None
schema_inspector = None

def init_db_connection(config):
    global db_connector, schema_inspector
    db_connector = DatabaseConnector(
        db_type=config.get('type', 'postgresql'),
        user=config.get('user'),
        password=config.get('password'),
        host=config.get('host'),
        port=config.get('port'),
        dbname=config.get('dbname'),
        project_id=config.get('project_id'), # For BigQuery
        dataset_id=config.get('dataset_id')  # For BigQuery
    )
    schema_inspector = SchemaInspector(db_connector)

def list_tables() -> list:
    """Lists all tables in the connected database."""
    if schema_inspector:
        return schema_inspector.get_all_tables()
    return []

def get_schema(table_name: str) -> str:
    """Gets the schema for a specific table."""
    if schema_inspector:
        df = schema_inspector.get_table_schema(table_name)
        return df.to_string()
    return "Database not connected."

def execute_sql(query: str) -> str:
    """Executes a SQL query and returns the results as a string."""
    if db_connector:
        try:
            # Basic safety check (should be more robust in production)
            if "drop" in query.lower() or "delete" in query.lower() or "update" in query.lower():
                return "Error: Destructive queries are not allowed."
            
            df = db_connector.execute_query(query)
            return df.to_string() # Return string representation for the agent
        except Exception as e:
            return f"Error executing query: {str(e)}"
    return "Database not connected."

def create_agent(api_key: str = None):
    """
    Creates and configures the Data Analysis Agent.
    """
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        
    agent = Agent(
        model='gemini-2.5-flash',
        name='data_analyst',
        description="A senior data analyst agent capable of querying databases and visualizing data.",
        instruction="""
        You are a Senior Data Analyst. Your goal is to help users understand their data.
        
        Workflow:
        1. Understand the user's question.
        2. Use `list_tables` to see what tables are available.
        3. Use `get_schema` to understand the columns of relevant tables.
        4. Construct a valid SQL query (read-only).
        5. Use `execute_sql` to run the query.
        6. Analyze the results and provide an answer.
        
        Always ensure your SQL queries are safe and read-only.
        If the result is large, summarize it.
        """,
        tools=[list_tables, get_schema, execute_sql],
    )
    return agent

import asyncio
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

# Global runner instance
runner = None
session_service = InMemorySessionService()
app_name = "data_analysis_agent"

def run_agent(agent, prompt: str) -> str:
    """
    Synchronously runs the agent with the given prompt using the ADK Runner.
    """
    global runner
    if runner is None:
        runner = Runner(agent=agent, session_service=session_service, app_name=app_name)

    async def _run():
        # Ensure session exists
        user_id = "demo_user"
        session_id = "demo_session"
        
        try:
            await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
        except Exception:
            # Session might not exist, try creating it
            # Note: get_session usually returns None if not found, but let's be safe
            pass
            
        # Check if session actually exists, if not create it
        session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
        if not session:
             await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

        # Create a simple text content for the user message
        user_content = types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )
        
        response_text = ""
        # Use a fixed session/user ID for this demo
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_content
        ):
            # Capture the final response from the agent
            if event.is_final_response() and event.content:
                 for part in event.content.parts:
                     if part.text:
                         response_text += part.text
        return response_text

    return asyncio.run(_run())
