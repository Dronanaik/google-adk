# Agentic RAG with Crawl4ai, Embeddings, and Supabase

This project implements an Agentic Retrieval-Augmented Generation (RAG) system. It leverages `crawl4ai` to scrape documentation, converts the content into vector embeddings, and stores them in a Supabase PostgreSQL database using the `pgvector` extension. An AI agent then uses this indexed knowledge to answer queries.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project demonstrates the power of combining a web crawler, a vector database, and a large language model (LLM) to create a knowledgeable AI agent. Traditional RAG models enhance LLMs with external data. [3] Agentic RAG takes this a step further by introducing an autonomous agent that can reason, orchestrate tools, and dynamically retrieve information to provide more accurate and context-aware answers. [1, 5]

In this implementation:
- **`crawl4ai`** is used to efficiently crawl and extract clean, LLM-friendly markdown from documentation websites. [8, 12]
- An **Embedding Model** transforms the crawled text into numerical vector representations.
- **Supabase** acts as a scalable and secure backend, storing the vector embeddings and enabling efficient similarity searches. [11]

## Architecture

The system follows a multi-step process orchestrated by the AI agent:

1.  **Data Ingestion (Crawling):** The `crawl4ai` library is used to crawl specified documentation URLs. [15] It processes the HTML content and converts it into clean markdown, suitable for embedding. [16]
2.  **Embedding:** The extracted markdown is chunked into smaller segments. Each chunk is then passed to an embedding model (e.g., OpenAI's `text-embedding-ada-002`, or open-source models like `nomic-embed-text`) to create a vector embedding. [9, 14] These embeddings capture the semantic meaning of the text. [7]
3.  **Storage:** The text chunks and their corresponding vector embeddings are stored in a PostgreSQL database hosted on Supabase. The `pgvector` extension is used to enable efficient vector similarity searches. [10, 18]
4.  **Agentic Retrieval:** When a user poses a query, the AI agent first analyzes the query's intent. [6] It then converts the query into an embedding.
5.  **Similarity Search:** The agent queries the Supabase database to find the most relevant text chunks by performing a similarity search on the vector embeddings.
6.  **Augmented Generation:** The retrieved text chunks are then passed to an LLM as context, along with the original query. The LLM uses this context to generate a comprehensive and accurate answer.

## Features

-   **Automated Content Ingestion:** Leverages `crawl4ai` to keep the knowledge base up-to-date with the latest documentation.
-   **High-Quality Data Preparation:** Generates clean markdown from web pages, perfect for RAG pipelines. [15]
-   **Efficient Vector Storage & Retrieval:** Uses Supabase and `pgvector` for a scalable and fast vector database. [19]
-   **Intelligent Agent-driven Responses:** Employs an agentic approach to analyze queries and retrieve the most relevant context. [2]
-   **Reduced Hallucinations:** By grounding the LLM with relevant, retrieved documents, the system produces more factual and reliable answers. [19]

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

-   Python 3.8+
-   A Supabase account with a new project created.
-   API keys for your chosen Embedding Model (e.g., OpenAI,AzureOpenAI).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Dronanaik/google-adk.git
    cd crawl4AI-agent
    ```

2.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```
    Your `requirements.txt` should include:
    ```
    crawl4ai
    supabase
    openai
    python-dotenv
    # Add other necessary libraries
    ```

3.  **Set up `crawl4ai`:**
    This command installs the necessary browser binaries for Playwright. [17]
    ```bash
    crawl4ai-setup
    ```

### Configuration

1.  **Set up Supabase:**
    -   In your Supabase project's SQL Editor, enable the `vector` extension. [20]
        ```sql
        create extension if not exists vector;

        -- Create the documentation chunks table
        create table site_pages (
            id bigserial primary key,
            url varchar not null,
            chunk_number integer not null,
            title varchar not null,
            summary varchar not null,
            content text not null,  -- Added content column
            metadata jsonb not null default '{}'::jsonb,  -- Added metadata column
            embedding vector(1536),  -- OpenAI embeddings are 1536 dimensions
            created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    
        -- Add a unique constraint to prevent duplicate chunks for the same URL
            unique(url, chunk_number)
            );
        ```

2.  **Environment Variables:**
    Create a `.env` file in the root of your project and add the following:
    ```
    # Supabase credentials
    SUPABASE_URL="YOUR_SUPABASE_URL"
    SUPABASE_KEY="YOUR_SUPABASE_ANON_KEY"

    # Embedding Model API Key
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

    # Azure model for chat 
    LLM_MODEL=gpt-4o

    CHAT_AZURE_OPENAI_ENDPOINT="YOUR_ENDPOINT_URL" (e.g https://your-model.openai.azure.com)
    CHAT_AZURE_OPENAI_API_KEY="YOUR_API_KEY"
    CHAT_AZURE_OPENAI_API_VERSION="VERSION"
    MODEL_DEPLOYMENT_NAME="YOUR MODEL" (e.g gpt-4o ,gpt-5)

    # If you are using seperate embedding model
    MBEDDING_AZURE_OPENAI_ENDPOINT="https://your-model.azure.com/"
    EMBEDDING_AZURE_OPENAI_API_KEY="YOUR_API_KEY"
    EMBEDDING_AZURE_OPENAI_API_VERSION="VERSION"
    EMBEDDING_DEPLOYMENT_NAME="YOUR_EMBEDDING" (e.g text-embedding-3-small)

    ```

## Usage

You can run the agent by executing the main Python script. The script should orchestrate the crawling, embedding, and querying process.

**1. Data Ingestion Script (`ai_expert.py`):**

```python
import os
from dotenv import load_dotenv
from crawl4ai import AsyncWebCrawler
from supabase import create_client, Client
from openai import OpenAI, AsyncAzureOpenAI

load_dotenv()

# Initialize clients
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def crawl_and_embed(url: str):
    """Crawls a URL, chunks the content, and stores embeddings in Supabase."""
    crawler = AsyncWebCrawler()
    result = await crawler.arun(url=url)

    # Simple chunking strategy (can be improved)
    chunks = [result.markdown[i:i+1000] for i in range(0, len(result.markdown), 1000)]

    for chunk in chunks:
        # Create embedding
        response = openai_client.embeddings.create(
            input=chunk,
            model="text-embedding-3-small" # Or your chosen model
        )
        embedding = response.data.embedding

        # Store in Supabase
        supabase.table("document_chunks").insert({
            "content": chunk,
            "embedding": embedding
        }).execute()
    print(f"Successfully crawled and embedded content from {url}")

# Example usage
# import asyncio
# asyncio.run(crawl_and_embed("https://crawl4ai.com/"))