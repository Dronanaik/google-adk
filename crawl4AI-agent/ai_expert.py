# pyright: reportMissingImports=false
from __future__ import annotations as _annotations
from dataclasses import dataclass
from dotenv import load_dotenv
import logfire
import httpx
import os
from typing import List

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncAzureOpenAI # We need this to create our client
from supabase import Client

load_dotenv()

# --- Azure OpenAI Configuration ---
CHAT_AZURE_OPENAI_ENDPOINT = os.getenv("CHAT_AZURE_OPENAI_ENDPOINT")
CHAT_AZURE_OPENAI_API_KEY = os.getenv("CHAT_AZURE_OPENAI_API_KEY")
CHAT_AZURE_OPENAI_API_VERSION = os.getenv("CHAT_AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME")


EMBEDDING_DEPLOYMENT_NAME = os.getenv("EMBEDDING_DEPLOYMENT_NAME")

# 1. Create the Azure client manually. This client is guaranteed to be configured correctly.
azure_client = AsyncAzureOpenAI(
    azure_endpoint=CHAT_AZURE_OPENAI_ENDPOINT,
    api_key=CHAT_AZURE_OPENAI_API_KEY,
    api_version=CHAT_AZURE_OPENAI_API_VERSION,
    http_client=httpx.AsyncClient(verify=False), # From your original code
)

# 2. Instantiate the OpenAIModel with just the deployment name.
# It will create a default, incorrect client internally.
model = OpenAIModel(MODEL_DEPLOYMENT_NAME)

# 3. Forcefully replace (monkey-patch) the model's internal client with our correct Azure client.
# Now, any time 'model' is used, it will use our 'azure_client'.
model.client = azure_client

# --- END OF CORRECTION ---
#

logfire.configure(send_to_logfire='if-token-present')

# Dependencies are simplified as the client is now part of the context
@dataclass
class PydanticAIDeps:
    supabase: Client

system_prompt = """
You are an expert at Google ADK - a Google ADK agent framework. Your job is to assist with questions about it.
You must use the provided tools to look at the documentation before answering. Always start with RAG.
"""

pydantic_ai_expert = Agent(
    model=model,
    system_prompt=system_prompt,
    deps_type=PydanticAIDeps,
    retries=2
)

# The tool correctly uses ctx.client, which will now be our azure_client
@pydantic_ai_expert.tool
async def retrieve_relevant_documentation(ctx: RunContext[PydanticAIDeps], user_query: str) -> str:
    """
    Retrieve relevant documentation chunks based on the query with RAG.
    """
    try:
        embedding_response = await ctx.client.embeddings.create(
            model=EMBEDDING_DEPLOYMENT_NAME,
            input=user_query
        )
        query_embedding = embedding_response.data[0].embedding
        
        result = ctx.deps.supabase.rpc(
            'match_site_pages',
            {
                'query_embedding': query_embedding,
                'match_count': 5,
                'filter': {'source': 'pydantic_ai_docs'}
            }
        ).execute()
        
        if not result.data:
            return "No relevant documentation found."
            
        formatted_chunks = [f"# {doc['title']}\n\n{doc['content']}" for doc in result.data]
        return "\n\n---\n\n".join(formatted_chunks)
        
    except Exception as e:
        print(f"Error retrieving documentation: {e}")
        return f"Error retrieving documentation: {str(e)}"

# ... (The rest of the tools are unchanged and correct) ...

@pydantic_ai_expert.tool
async def list_documentation_pages(ctx: RunContext[PydanticAIDeps]) -> List[str]:
    try:
        result = ctx.deps.supabase.from_('site_pages').select('url').eq('metadata->>source', 'pydantic_ai_docs').execute()
        if not result.data: return []
        return sorted(set(doc['url'] for doc in result.data))
    except Exception as e:
        print(f"Error listing pages: {e}")
        return []

@pydantic_ai_expert.tool
async def get_page_content(ctx: RunContext[PydanticAIDeps], url: str) -> str:
    try:
        result = ctx.deps.supabase.from_('site_pages').select('title, content, chunk_number').eq('url', url).eq('metadata->>source', 'pydantic_ai_docs').order('chunk_number').execute()
        if not result.data: return f"No content found for URL: {url}"
        page_title = result.data[0]['title'].split(' - ')[0]
        content = "\n\n".join(chunk['content'] for chunk in result.data)
        return f"# {page_title}\n\n{content}"
    except Exception as e:
        print(f"Error getting page content: {e}")
        return f"Error: {str(e)}"