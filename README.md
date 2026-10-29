# ⚡ Google ADK Agents Collection

A comprehensive collection of **11 intelligent AI agents** built using the [**Google Agent Development Kit (ADK)**](https://github.com/google/adk) and **Gemini** models. This repository showcases practical, production-style agent architectures—ranging from **real-time bidirectional voice agents** with deterministic policy guardrails to **multi-agent systems**, **Model Context Protocol (MCP)** integrations, **browser automation**, **database analytics**, and **Agentic RAG**.

[**🌐 View Interactive Agent Portfolio (`index.html`)**](index.html) · [**📖 Official Google ADK Documentation**](https://google.github.io/adk-docs/)

---

## 📑 Table of Contents

- [🤖 Agent Directory (Quick Reference)](#-agent-directory-quick-reference)
- [🧩 ADK Patterns & Capabilities Matrix](#-adk-patterns--capabilities-matrix)
- [📂 Repository Structure](#-repository-structure)
- [🔍 Detailed Agent Reference](#-detailed-agent-reference)
  - [1. CSM Voice Agent (`csm-voice-agent`)](#1-csm-voice-agent-csm-voice-agent)
  - [2. Data Analysis Agent (`data_analysis_agent`)](#2-data-analysis-agent-data_analysis_agent)
  - [3. Streamlit Code Generator (`Streamlit-Code-Gen-agent`)](#3-streamlit-code-generator-streamlit-code-gen-agent)
  - [4. Playwright Agent (`PlaywrightAgent`)](#4-playwright-agent-playwrightagent)
  - [5. Job Search Agent (`job_search_agent`)](#5-job-search-agent-job_search_agent)
  - [6. Crawl4AI Agent (`crawl4AI-agent`)](#6-crawl4ai-agent-crawl4ai-agent)
  - [7. Financial MCP Agent (`financial-mcp-agent`)](#7-financial-mcp-agent-financial-mcp-agent)
  - [8. Test Data Generator (`test_data_generator`)](#8-test-data-generator-test_data_generator)
  - [9. Memory Agent CLI (`MemoryAgentCLI`)](#9-memory-agent-cli-memoryagentcli)
  - [10. MCP Agent ADK (`mcp-agent-adk`)](#10-mcp-agent-adk-mcp-agent-adk)
  - [11. XrayAgent (`XrayAgent`)](#11-xrayagent-xrayagent)
- [🚀 Getting Started](#-getting-started)
- [📈 Learning Progress](#-learning-progress)
- [📚 Resources](#-resources)

---

## 🤖 Agent Directory (Quick Reference)

| # | Agent | Category | ADK Architecture & Key Primitives | Default Model | Description |
|:-:|:------|:---------|:----------------------------------|:--------------|:------------|
| 1 | [**CSM Voice Agent**](csm-voice-agent/) | 🎙️ Live Voice & Customer Support | `Agent` + `LiveRequestQueue` + `runner.run_live()` + `before_tool_callback` | `gemini-3.1-flash-live-preview` | Real-time bidirectional e-commerce customer service voice agent with barge-in, live order/account inspector, and deterministic policy gate (`csm_policy_gate`). |
| 2 | [**Data Analysis Agent**](data_analysis_agent/) | 📊 SQL & Data Analytics | `Agent` + `InMemorySessionService` + Custom DB Tools + Streamlit UI | `gemini-2.5-flash` | Connects to PostgreSQL, MySQL, and BigQuery, inspects schemas, and answers natural language questions by executing read-only SQL queries. |
| 3 | [**Streamlit Code Generator**](Streamlit-Code-Gen-agent/) | 💻 Code Generation | `Agent` + 7 Specialized App/Component Function Tools | `gemini-2.0-flash` | Generates complete, runnable Streamlit applications (dashboards, data explorers, forms, calculators, ML demos) from natural language prompts. |
| 4 | [**Playwright Agent**](PlaywrightAgent/) | 🌐 Browser Automation | `LlmAgent` + `MCPToolset` (`StdioConnectionParams` / `@playwright/mcp`) | `gemini-2.0-flash` | End-to-end browser automation agent that navigates websites, inspects live DOM state, and extracts information via Playwright MCP. |
| 5 | [**Job Search Agent**](job_search_agent/) | 💼 Productivity & Career | `LlmAgent` + Resume Parser Tools + Playwright `MCPToolset` | `gemini-2.0-flash` | Ingests PDF/DOCX resumes, extracts candidate profiles, and browses Naukri, LinkedIn, and Wellfound to return structured JSON job matches. |
| 6 | [**Crawl4AI Agent**](crawl4AI-agent/) | 🔍 Agentic RAG & Search | `AsyncWebCrawler` + Vector Embeddings + Supabase (`pgvector`) | Configurable LLM | Scrapes technical documentation into clean Markdown, stores vector embeddings in Supabase, and answers queries with grounded RAG context. |
| 7 | [**Financial MCP Agent**](financial-mcp-agent/) | 📈 Finance & Market Data | `LlmAgent` + `MCPToolset` (`StreamableHTTPConnectionParams`) | `gemini-2.5-pro` | Connects to the remote Financial Datasets MCP server over HTTP streaming to fetch real-time financial data and answer market queries. |
| 8 | [**Test Data Generator**](test_data_generator/) | 🛠️ Developer Tooling | `Agent` + 18 Modular Faker & Regex/Schema Tools | `gemini-2.0-flash-exp` | Generates realistic personal profiles, business/invoice data, numeric/temporal series, regex patterns, and structured JSON/CSV files. |
| 9 | [**Memory Agent CLI**](MemoryAgentCLI/) | ✍️ Creative Writing & Memory | Multi-Agent (`root_agent` → `story_agent`) + `DatabaseSessionService` | `gemini-2.5-flash` | Interactive Rich CLI storytelling app with SQLite session persistence (`agentmemo.db`) and configurable HTTP retry policies. |
| 10 | [**MCP Agent ADK**](mcp-agent-adk/) | 🔌 MCP Integration | `LlmAgent` + Remote `MCPToolset` (deployed on Alpic.ai) | `gemini-2.0-flash` | Reference blueprint demonstrating how to connect custom remote Model Context Protocol (MCP) servers to Google ADK. |
| 11 | [**XrayAgent**](XrayAgent/) | 🧪 QA & Test Automation | Hierarchical Multi-Agent (`XrayAgent` → `jira_agent`, `xray_agent`) | `gemini-2.0-flash-exp` | Multi-agent system for automated test case generation from Jira user stories and bulk import into Xray Cloud using 73+ Jira REST API v3 tools. |

---

## 🧩 ADK Patterns & Capabilities Matrix

Use this table to quickly find reference implementations for specific Google ADK features:

| ADK Capability / Pattern | Reference Agent(s) | Key Implementation Files |
|:-------------------------|:-------------------|:-------------------------|
| **Gemini Live API (Bidirectional Voice + Barge-In)** | [**CSM Voice Agent**](csm-voice-agent/) | [`csm_agent/agent.py`](csm-voice-agent/csm_agent/agent.py), [`csm_agent/server.py`](csm-voice-agent/csm_agent/server.py) |
| **Deterministic Tool Guardrails (`before_tool_callback`)** | [**CSM Voice Agent**](csm-voice-agent/) | [`csm_agent/policy.py`](csm-voice-agent/csm_agent/policy.py) |
| **Multi-Agent Hierarchy & Subagents (`sub_agents`)** | [**XrayAgent**](XrayAgent/), [**Memory Agent CLI**](MemoryAgentCLI/) | [`XrayAgent/agent.py`](XrayAgent/agent.py), [`MemoryAgentCLI/agent.py`](MemoryAgentCLI/agent.py) |
| **Local MCP Integration via Stdio (`StdioConnectionParams`)** | [**Playwright Agent**](PlaywrightAgent/), [**Job Search Agent**](job_search_agent/) | [`PlaywrightAgent/agent.py`](PlaywrightAgent/agent.py), [`job_search_agent/agent.py`](job_search_agent/agent.py) |
| **Remote MCP Integration via HTTP (`StreamableHTTPConnectionParams`)** | [**Financial MCP Agent**](financial-mcp-agent/), [**MCP Agent ADK**](mcp-agent-adk/) | [`financial-mcp-agent/agent.py`](financial-mcp-agent/agent.py), [`mcp-agent-adk/agent.py`](mcp-agent-adk/agent.py) |
| **Persistent SQLite Session Storage (`DatabaseSessionService`)** | [**Memory Agent CLI**](MemoryAgentCLI/) | [`MemoryAgentCLI/agent.py`](MemoryAgentCLI/agent.py) |
| **In-Memory Session Runner (`InMemorySessionService` + `Runner`)** | [**Data Analysis Agent**](data_analysis_agent/), [**CSM Voice Agent**](csm-voice-agent/), [**Test Data Generator**](test_data_generator/) | [`data_analysis_agent/agent/agent.py`](data_analysis_agent/agent/agent.py), [`csm_agent/server.py`](csm-voice-agent/csm_agent/server.py) |
| **Custom Python Function Tools** | [**CSM Voice Agent**](csm-voice-agent/), [**Streamlit Code Generator**](Streamlit-Code-Gen-agent/), [**Test Data Generator**](test_data_generator/), [**XrayAgent**](XrayAgent/) | [`csm_agent/tools.py`](csm-voice-agent/csm_agent/tools.py), [`test_data_generator/tools/`](test_data_generator/tools/), [`XrayAgent/tools.py`](XrayAgent/tools.py) |
| **Agentic RAG with Vector Store (`pgvector`)** | [**Crawl4AI Agent**](crawl4AI-agent/) | [`crawl4AI-agent/ai_expert.py`](crawl4AI-agent/ai_expert.py), [`crawl4AI-agent/scrap_embed_docs.py`](crawl4AI-agent/scrap_embed_docs.py) |

---

## 📂 Repository Structure

```text
google-adk/
├── csm-voice-agent/             # 1. Live Voice Customer Service Agent + Policy Gate + FastAPI/WS UI
│   ├── assets/                  #    Persona prompt & sample NovaMart store data (JSON)
│   ├── csm_agent/               #    Agent, async tools, before_tool_callback policy, server, frontend
│   ├── pyproject.toml           #    uv project metadata & dependencies
│   └── README.md
├── data_analysis_agent/         # 2. Natural Language to SQL Agent (PostgreSQL, MySQL, BigQuery)
│   ├── agent/                   #    ADK agent & Runner integration
│   ├── ui/                      #    Streamlit chat interface
│   ├── utils/                   #    DB connector & schema inspector
│   └── README.md
├── Streamlit-Code-Gen-agent/    # 3. Natural Language to Full Streamlit App Generator
│   ├── streamlit_code_generator/#    ADK agent & 7 code-generation tools
│   ├── Dockerfile               #    Containerized setup
│   └── README.md
├── PlaywrightAgent/             # 4. Browser Automation Agent via @playwright/mcp
│   ├── agent.py                 #    LlmAgent with Stdio MCPToolset
│   └── README.md
├── job_search_agent/            # 5. Resume Parser & Multi-Board Job Search Agent
│   ├── tools/                   #    Resume ingest, profile extraction, job search & schema formatting
│   ├── agent.py                 #    LlmAgent combining custom tools + Playwright MCP
│   └── README.md
├── crawl4AI-agent/              # 6. Agentic RAG with Crawl4ai & Supabase pgvector
│   ├── ai_expert.py             #    RAG agent with vector similarity search
│   ├── scrap_embed_docs.py      #    Documentation crawler & embedding pipeline
│   ├── streamlit_ui.py          #    Interactive Streamlit frontend
│   └── README.md
├── financial-mcp-agent/         # 7. Financial Datasets Remote MCP Agent
│   ├── agent.py                 #    LlmAgent with StreamableHTTPConnectionParams
│   └── README.md
├── test_data_generator/         # 8. Synthetic Test Data Generator Agent
│   ├── tools/                   #    Personal, business, numeric & regex/schema generators
│   ├── agent.py                 #    Root agent with 18 data generation tools
│   └── README.md
├── MemoryAgentCLI/              # 9. Persistent Memory Storytelling CLI Agent
│   ├── agent.py                 #    Multi-agent runner with DatabaseSessionService (SQLite)
│   └── README.md
├── mcp-agent-adk/               # 10. Custom Remote MCP Server Integration Demo (Alpic.ai)
│   ├── agent.py                 #     LlmAgent connected to remote MCP endpoint
│   └── README.md
├── XrayAgent/                   # 11. Multi-Agent Jira & Xray Test Management System
│   ├── subagents/               #     jira_agent (73+ Jira REST v3 tools) & xray_agent
│   ├── agent.py                 #     Root orchestrator agent
│   ├── tools.py                 #     Xray Cloud API authentication & bulk test import tools
│   └── README.md
├── assets/                      # Portfolio card logos for all 11 agents
├── index.html                   # Interactive Agent Portfolio landing page (GitHub Pages)
└── README.md                    # Repository documentation (this file)
```

---

## 🔍 Detailed Agent Reference

### 1. CSM Voice Agent (`csm-voice-agent`)

> **Directory**: [`csm-voice-agent/`](csm-voice-agent/) · **Documentation**: [`csm-voice-agent/README.md`](csm-voice-agent/README.md) · **Asset**: [`assets/CSM_Voice_agent.png`](assets/CSM_Voice_agent.png)

A real-time, bidirectional **E-Commerce Customer Service Management (CSM) Voice Agent** ("Aria" / "Soumya" at **NovaMart**) built on **Google ADK** and the **Gemini Live API**. Users can speak naturally over a 16 kHz microphone stream (or click sample prompt chips), interrupt mid-sentence (client-side barge-in), inspect live customer/order state, and watch every tool call pass through a deterministic **Policy Gate** in real time.

- **Key Highlights**:
  - **Bidirectional Voice Streaming**: Uses `LiveRequestQueue` and `runner.run_live()` with `Gemini(speech_config=...)` (`Aoede` prebuilt voice) over FastAPI WebSockets (`/ws`).
  - **Deterministic Policy Gate (`before_tool_callback`)**: [`csm_policy_gate`](csm-voice-agent/csm_agent/policy.py) enforces business rules in code (e.g., blocking auto-refunds over \$100, blocking refunds past the 30-day window, blocking address changes once an order is `in_transit` or `delivered`, and optional `REQUIRE_PIN=1` verification) and streams `✓ allowed` / `⛔ blocked` verdicts to the UI Action Log.
  - **Live CSM Console UI**: Includes an animated Voice Orb, Customer & Order Inspector panel, Policy Gate Action Log, and live input/output audio transcriptions.
- **Tools**: `lookup_customer`, `lookup_order`, `verify_customer_pin`, `issue_refund`, `update_shipping_address`, `create_support_ticket`, `escalate_to_human`.
- **Quick Start**:
  ```bash
  cd csm-voice-agent
  uv sync
  cp .env.example .env   # Set GOOGLE_API_KEY
  uv run uvicorn csm_agent.server:app --port 8000
  # Or run offline unit & policy gate smoke tests:
  uv run python csm_agent/smoke_live.py --unit
  ```

---

### 2. Data Analysis Agent (`data_analysis_agent`)

> **Directory**: [`data_analysis_agent/`](data_analysis_agent/) · **Documentation**: [`data_analysis_agent/README.md`](data_analysis_agent/README.md) · **Asset**: [`assets/data_analysis_agent.png`](assets/data_analysis_agent.png)

An AI-powered SQL analyst that connects to relational and cloud databases, introspects schemas automatically, and answers natural language business questions by generating and running safe, read-only SQL queries.

- **Key Highlights**:
  - **Multi-Database Support**: Connects to PostgreSQL, MySQL, and Google BigQuery via SQLAlchemy.
  - **Read-Only Guardrails**: Prevents destructive SQL statements (`DROP`, `DELETE`, `UPDATE`) during query execution.
  - **Interactive Streamlit UI**: Sidebar configuration for database credentials and conversational query interface.
- **Tools**: `list_tables`, `get_schema`, `execute_sql`.
- **Quick Start**:
  ```bash
  cd data_analysis_agent
  pip install -r requirements.txt
  streamlit run ui/app.py
  ```

---

### 3. Streamlit Code Generator (`Streamlit-Code-Gen-agent`)

> **Directory**: [`Streamlit-Code-Gen-agent/`](Streamlit-Code-Gen-agent/) · **Documentation**: [`Streamlit-Code-Gen-agent/README.md`](Streamlit-Code-Gen-agent/README.md) · **Asset**: [`assets/streamlit_code_gen.png`](assets/streamlit_code_gen.png)

An ADK code-generation agent that turns natural language requirements into complete, well-documented, runnable Streamlit applications or modular UI components.

- **Key Highlights**:
  - **Full App Templates**: Generates complete Dashboards, CSV Data Explorers, Validated Forms, Calculators, and Interactive ML Demos.
  - **Granular Component Tools**: Adds charts, user inputs, multi-tab/column layouts, and dataframe displays on demand.
  - **Direct File Export**: Saves generated applications directly to `generated_apps/` for immediate execution.
- **Tools**: `generate_streamlit_boilerplate`, `add_data_visualization`, `add_user_input_components`, `add_layout_components`, `add_data_display_components`, `create_complete_streamlit_app`, `save_streamlit_code`.
- **Quick Start**:
  ```bash
  cd Streamlit-Code-Gen-agent
  pip install -r requirements.txt
  adk web
  ```

---

### 4. Playwright Agent (`PlaywrightAgent`)

> **Directory**: [`PlaywrightAgent/`](PlaywrightAgent/) · **Documentation**: [`PlaywrightAgent/README.md`](PlaywrightAgent/README.md) · **Asset**: [`assets/playwright_agent.png`](assets/playwright_agent.png)

An end-to-end browser automation agent that integrates the official `@playwright/mcp` server with Google ADK via `MCPToolset` and `StdioConnectionParams`.

- **Key Highlights**:
  - **Zero-Boilerplate Browser Control**: Spawns `npx @playwright/mcp@latest` with configurable startup (120s) and I/O (60s) timeouts.
  - **Reasoning-First Navigation**: Follows a structured *Navigate → Inspect & Interact → Extract & Respond* workflow.
- **Tools**: Playwright MCP toolset (`playwright.goto`, `playwright.page_content`, click/fill/snapshot actions).
- **Quick Start**:
  ```bash
  cd PlaywrightAgent
  pip install -r requirements.txt
  npx playwright install
  adk web
  ```

---

### 5. Job Search Agent (`job_search_agent`)

> **Directory**: [`job_search_agent/`](job_search_agent/) · **Documentation**: [`job_search_agent/README.md`](job_search_agent/README.md) · **Asset**: [`assets/job_search_agent.png`](assets/job_search_agent.png)

An automated career assistant that combines custom Python resume-parsing tools with Playwright MCP browser automation to match candidates with live job postings.

- **Key Highlights**:
  - **Multi-Format Resume Ingestion**: Parses PDF, DOCX, and plain-text resumes into structured candidate profiles (skills, experience, education, preferred roles).
  - **Autonomous Job Board Browsing**: Uses `@playwright/mcp` to search Naukri, LinkedIn, and Wellfound, with an internal aggregator fallback (`SerpAPI` / `JSearch`).
  - **Strict JSON Output**: Consolidates candidate profile metadata and matched roles into a clean JSON schema.
- **Tools**: `ingest_resume`, `extract_profile`, `MCPToolset` (`@playwright/mcp`), `search_jobs`, `format_results`.
- **Quick Start**:
  ```bash
  pip install google-adk pdfminer.six python-docx requests playwright
  adk web
  ```

---

### 6. Crawl4AI Agent (`crawl4AI-agent`)

> **Directory**: [`crawl4AI-agent/`](crawl4AI-agent/) · **Documentation**: [`crawl4AI-agent/README.md`](crawl4AI-agent/README.md) · **Asset**: [`assets/Crawl4ai_agent.png`](assets/Crawl4ai_agent.png)

An Agentic Retrieval-Augmented Generation (RAG) system that crawls documentation websites using `crawl4ai`, indexes vector embeddings in **Supabase (`pgvector`)**, and provides grounded answers via a Streamlit UI.

- **Key Highlights**:
  - **Automated Documentation Scraping**: Converts complex web documentation into clean, LLM-ready Markdown chunks.
  - **Vector Similarity Search**: Stores 1536-dimensional embeddings in PostgreSQL (`site_pages` table) with unique URL/chunk constraints.
  - **Grounded Q&A**: Dynamically retrieves relevant documentation pages, summaries, and chunks to minimize hallucinations.
- **Quick Start**:
  ```bash
  cd crawl4AI-agent
  pip install -r requirements.txt
  crawl4ai-setup
  streamlit run streamlit_ui.py
  ```

---

### 7. Financial MCP Agent (`financial-mcp-agent`)

> **Directory**: [`financial-mcp-agent/`](financial-mcp-agent/) · **Documentation**: [`financial-mcp-agent/README.md`](financial-mcp-agent/README.md) · **Asset**: [`assets/financial_agent.png`](assets/financial_agent.png)

A specialized financial research agent configured to query the remote **Financial Datasets MCP Server** over streamable HTTP.

- **Key Highlights**:
  - **Remote HTTP Streaming MCP**: Demonstrates `StreamableHTTPConnectionParams` with custom `X-API-KEY` header authentication against `https://mcp.financialdatasets.ai/api`.
  - **Powered by Gemini 2.5 Pro**: Ideal for complex financial analysis, balance sheet lookups, and market queries.
- **Quick Start**:
  ```bash
  export GOOGLE_API_KEY="your-google-api-key"
  export X_API_KEY="your-financial-datasets-api-key"
  adk web
  ```

---

### 8. Test Data Generator (`test_data_generator`)

> **Directory**: [`test_data_generator/`](test_data_generator/) · **Documentation**: [`test_data_generator/README.md`](test_data_generator/README.md) · **Asset**: [`assets/test_data_agent.png`](assets/test_data_agent.png)

A developer utility agent equipped with **18 specialized tools** for synthesizing realistic test data for software testing, database seeding, and API mocking.

- **Key Highlights**:
  - **4 Tool Categories**:
    - *Personal Data*: `generate_names`, `generate_emails`, `generate_phone_numbers`, `generate_addresses`, `generate_user_profiles`
    - *Business Data*: `generate_company_names`, `generate_product_names`, `generate_prices`, `generate_invoice_data`
    - *Numeric & Temporal*: `generate_integers`, `generate_floats`, `generate_dates`, `generate_timestamps`, `generate_uuids`
    - *Custom Patterns & Exports*: `generate_from_regex`, `generate_from_format`, `generate_json_data`, `generate_csv_data`
- **Quick Start**:
  ```bash
  cd test_data_generator
  pip install -r requirements.txt
  adk run
  ```

---

### 9. Memory Agent CLI (`MemoryAgentCLI`)

> **Directory**: [`MemoryAgentCLI/`](MemoryAgentCLI/) · **Documentation**: [`MemoryAgentCLI/README.md`](MemoryAgentCLI/README.md) · **Asset**: [`assets/memory_agent.png`](assets/memory_agent.png)

An interactive command-line storytelling application (`StoryApp`) demonstrating persistent session storage and multi-agent delegation in Google ADK.

- **Key Highlights**:
  - **SQLite Session Persistence**: Uses `DatabaseSessionService(db_url="sqlite:///./agentmemo.db")` so conversations and story context persist across turns.
  - **Subagent Delegation**: `root_agent` delegates creative requests to a dedicated `story_agent` configured with custom `HttpRetryOptions`.
  - **Rich Terminal Output**: Pretty-prints live ADK event streams and syntax-highlighted JSON payloads in the terminal.
- **Quick Start**:
  ```bash
  cd MemoryAgentCLI
  pip install google-adk google-genai rich python-dotenv
  python agent.py
  ```

---

### 10. MCP Agent ADK (`mcp-agent-adk`)

> **Directory**: [`mcp-agent-adk/`](mcp-agent-adk/) · **Documentation**: [`mcp-agent-adk/README.md`](mcp-agent-adk/README.md) · **Asset**: [`assets/mcp_agent.png`](assets/mcp_agent.png)

A clean, minimal starter template demonstrating how to build a custom MCP server from scratch, deploy it on [**Alpic.ai**](https://alpic.ai/), and consume its tools inside a Google ADK `LlmAgent`.

- **Key Highlights**:
  - Connects to a cloud-hosted MCP endpoint (`https://mcp-creation-06152dab.alpic.live/`) using `MCPToolset` and `StreamableHTTPConnectionParams`.
- **Quick Start**:
  ```bash
  pip install google-adk
  adk web
  ```

---

### 11. XrayAgent (`XrayAgent`)

> **Directory**: [`XrayAgent/`](XrayAgent/) · **Documentation**: [`XrayAgent/README.md`](XrayAgent/README.md) · **Asset**: [`assets/xray_agent.png`](assets/xray_agent.png)

An enterprise-grade hierarchical multi-agent system for automated QA test case generation and management in **Jira Cloud** using the **Xray** plugin.

- **Key Highlights**:
  - **Multi-Agent Architecture**: Orchestrates `XrayAgent` (root) alongside specialized `jira_agent` and `xray_agent` subagents.
  - **Comprehensive Jira REST API v3 Coverage**: Includes **73+ Jira API functions** across 9 API groups (Custom Fields, Field Contexts, Options, Issue Types, Schemes, and Configurations).
  - **Xray Cloud Bulk Import**: Authenticates via Bearer token (`get_xray_token`), imports manual test steps (`import_manual_tests_cloud`), and tracks asynchronous bulk job statuses (`get_import_job_status`).
- **Quick Start**:
  ```bash
  cd XrayAgent
  pip install -r requirements.txt
  adk web
  ```

---

## 🚀 Getting Started

### 1. Prerequisites

- **Python**: `3.10+` (or `uv` for projects like `csm-voice-agent`)
- **Node.js**: `18+` with `npx` (required only for Playwright MCP agents: `PlaywrightAgent` and `job_search_agent`)
- **Google Gemini API Key**: Get one from [Google AI Studio](https://aistudio.google.com/apikey)

### 2. Common Environment Setup

```bash
# Clone the repository
git clone https://github.com/Dronanaik/google-adk.git
cd google-adk

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Configure your API key
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY="your_google_ai_studio_api_key"
```

### 3. Running Any Agent

Most agents in this repository can be launched using the built-in **Google ADK Dev UI** or CLI from the repository root (or from the agent's directory):

```bash
# Launch the interactive ADK Web UI (http://localhost:8000)
adk web

# Run an agent in the terminal
adk run <agent_folder_name>

# Or start the ADK REST API server
adk api_server
```

> **Note**: Agents with custom full-stack interfaces—such as [**CSM Voice Agent**](csm-voice-agent/) (`uv run uvicorn csm_agent.server:app --port 8000`) and [**Data Analysis Agent**](data_analysis_agent/) (`streamlit run ui/app.py`)—also provide dedicated web consoles. Check each agent's `README.md` for details.

---

## 📈 Learning Progress

- [x] Set up Google ADK environment
- [x] Create basic agents with custom Python function tools (`Streamlit-Code-Gen-agent`, `test_data_generator`, `data_analysis_agent`)
- [x] Integrate local & remote MCP (Model Context Protocol) servers (`PlaywrightAgent`, `financial-mcp-agent`, `mcp-agent-adk`, `job_search_agent`)
- [x] Build persistent session memory and multi-agent hierarchies (`MemoryAgentCLI`, `XrayAgent`)
- [x] Build real-time bidirectional **Gemini Live Voice Agent** with `before_tool_callback` policy guardrails and barge-in (`csm-voice-agent`)
- [ ] Explore production deployment and cloud scaling (Cloud Run / Vertex AI Agent Engine)

---

## 📚 Resources

- **Official Documentation**: [Google ADK Quickstart & Docs](https://google.github.io/adk-docs/get-started/quickstart/#set-up-environment-install-adk)
- **Google ADK GitHub**: [google/adk-python](https://github.com/google/adk-python)
- **Interactive Portfolio**: [View Agent Cards (`index.html`)](index.html)
- **Author**: [Drona Naik (@Dronanaik)](https://github.com/Dronanaik)
