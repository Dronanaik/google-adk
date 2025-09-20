from __future__ import annotations
from typing import Literal, TypedDict
import asyncio
import os

import streamlit as st
import logfire
from supabase import create_client, Client

# We don't need to import the OpenAI client here anymore
from pydantic_ai.messages import ModelRequest, ModelResponse, UserPromptPart, TextPart
from ai_expert import pydantic_ai_expert, PydanticAIDeps

# Load environment variables (this is now very important)
from dotenv import load_dotenv
load_dotenv()

# We only need to initialize Supabase here
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Configure logfire
logfire.configure(send_to_logfire='never')

# ... (ChatMessage and display_message_part functions are unchanged) ...
class ChatMessage(TypedDict):
    role: Literal['user', 'model']
    timestamp: str
    content: str

def display_message_part(part):
    if part.part_kind == 'system-prompt':
        with st.chat_message("system"): st.markdown(f"**System**: {part.content}")
    elif part.part_kind == 'user-prompt':
        with st.chat_message("user"): st.markdown(part.content)
    elif part.part_kind == 'text':
        with st.chat_message("assistant"): st.markdown(part.content)

async def run_agent_with_streaming(user_input: str):
    """Run the agent and stream the response."""
    # Prepare the simplified dependencies
    deps = PydanticAIDeps(supabase=supabase)

    # The agent will create its own Azure client internally using the environment variables
    async with pydantic_ai_expert.run_stream(
        user_input,
        deps=deps,
        message_history=st.session_state.messages[:-1],
    ) as result:
        partial_text = ""
        message_placeholder = st.empty()

        async for chunk in result.stream_text(delta=True):
            partial_text += chunk
            message_placeholder.markdown(partial_text)

        # Update session state
        filtered_messages = [
            msg for msg in result.new_messages()
            if not any(part.part_kind == 'user-prompt' for part in getattr(msg, 'parts', []))
        ]
        st.session_state.messages.extend(filtered_messages)

        # Add final response
        st.session_state.messages.append(
            ModelResponse(parts=[TextPart(content=partial_text)])
        )

# ... (main function is unchanged) ...
async def main():
    st.title("Google ADK Agentic RAG")
    st.write("Ask any question about Google ADK Documentation.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        for part in getattr(msg, 'parts', []):
            display_message_part(part)

    user_input = st.chat_input("What questions do you have about Google ADK?")

    if user_input:
        st.session_state.messages.append(ModelRequest(parts=[UserPromptPart(content=user_input)]))
        with st.chat_message("user"): st.markdown(user_input)
        with st.chat_message("assistant"):
            await run_agent_with_streaming(user_input)

if __name__ == "__main__":
    asyncio.run(main())