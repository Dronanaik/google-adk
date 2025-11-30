from google.adk.agents.llm_agent import Agent



import asyncio
import json
from typing import Any
from rich import print as rprint
from rich.syntax import Syntax
from rich.prompt import Prompt
import uuid
import os

from google.genai import types
from google.genai.types import Content,Part

from dotenv import load_dotenv
load_dotenv()
MODEL_NAME =  os.getenv("MODEL_NAME")


from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.models.google_llm import Gemini

retry_config=types.HttpRetryOptions(
    attempts=5,         # Maximum retry attempts
    exp_base=7,         # Delay multiplier
    initial_delay=1,    # Initial delay before first retry (in seconds)
    http_status_codes=[
        429, # Too Many Requests
        500, # Internal Server Error
        503, # Service Unavailable
        504, # Gateway Timeout
        ]    # Retry on these HTTP errors
)


story_agent = Agent(
    model=Gemini(
        model=MODEL_NAME,
        retry_options=retry_config
    ),
    name='story_agent',
    description='An agent that creates engaging stories based on user prompts.',
    instruction='Create an engaging and imaginative story based on the user prompt.',
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    sub_agents=[story_agent],
)


APP_NAME = "StoryApp"
USER_ID = "user_123"
SESSION_ID = str(uuid.uuid4())

async def main():
    """Initialize the agent and session, then run the agent loop. continuously accept user queries and provide agent responses."""
    db_url = "sqlite:///./agentmemo.db"
    session_service = DatabaseSessionService(db_url=db_url)
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

    while True:
        rprint(f"[bold red]{'=' * 100}[/bold red]")
        rprint(f"[bold red]TYPE 'exit' or 'quit' to end the session![/bold red]")
        rprint(f"[bold red]{'=' * 100}[/bold red]")
        user_query = Prompt.ask("[bold yellow]You: [/bold yellow]")
        if user_query.lower() in ['exit', 'quit',':q']:
            rprint(f"[bold green]{'=' * 100}[/bold green]")
            rprint(f"[bold green]Ending the session. Goodbye![/bold green]")
            rprint(f"[bold green]{'=' * 100}[/bold green]")
            break

        new_message = Content(role="user",parts=[Part(text=user_query)])

        events = runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=new_message

        )

        final_response = ""
        i = 0
        async for event in events:
            i += 1

            print_json_response(event, f"Event {i}")
            
            if event.is_final_response():
                final_response = event.content.parts[0].text

                rprint(f"\n[bold green]{'='* 50}Final Response from Agent{'=' * 50}[/bold green]\n")
                rprint(f"\n[bold green]Agent : [/bold green][bold purple]{final_response}[/bold purple]")
                break

def print_json_response(response: Any, title: str):

    rprint(f"[bold blue]{'='*50}{title}{'=' * 50}[/bold blue]")
    try:
        if hasattr(response,"root"):
            data = response.root.model_dump(mode="json",exclude_none=True)
        else:
            data = response.model_dump(mode="json",exclude_none=True)
        
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        rprint(syntax)
        rprint(f"[bold blue]{'='*100}[/bold blue]")

    except Exception as e:

        rprint(f"[red]Error printing JSON response:[/red] {e}")
        rprint(repr(response))


if __name__ == "__main__":
    asyncio.run(main())


           
