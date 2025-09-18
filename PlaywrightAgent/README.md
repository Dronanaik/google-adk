## PlaywrightAgent (Google ADK)

An end-to-end, browser-automation AI agent built with `google.adk` that uses Playwright's MCP server to browse, extract data, and interact with websites.

The agent is defined in `PlaywrightAgent/agent.py` as an `LlmAgent` named `root_agent` configured with the `MCPToolset` to launch `@playwright/mcp` via `npx`.

### Features
- **Gemini model**: Uses `gemini-2.5-pro` via Google AI.
- **Playwright MCP tools**: Navigate to URLs, read page content, and interact through the MCP toolset.
- **Reasoning-first prompts**: Step-by-step instructions for reliable web automation.

---

## Prerequisites

- Python 3.10+
- Node.js 18+ and `npx`
- Google AI API key with access to Gemini models
  - Get one from Google AI Studio. Set `GOOGLE_API_KEY` in your environment.

Optional but recommended:
- A Python virtual environment

---

## Install

1) Clone the repository and enter the project folder:

```bash
git clone <your-fork-or-origin>
cd Miniprojects/Google_ADK/PlaywrightAgent
```

2) Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

3) Install Python dependencies:

```bash
pip install --upgrade pip
# Install from requirements file
pip install -r requirements.txt
# Optional: ADK Web UI
# pip install "google-adk[web]"
```

4) Ensure Node and Playwright MCP are available (installed on first run via `npx`):

```bash
node -v
npm -v
```

If Node is missing, install it from your package manager or `nodejs.org`.

5) Install Playwright browsers (helpful for local runs):

```bash
npx playwright install
```

---

## Configure credentials

Export your Google AI key in the shell before running the agent:

```bash
export GOOGLE_API_KEY="<your_key_here>"
```

If your environment uses a different variable name (e.g., `GEMINI_API_KEY`), set that as well.

---

## Project layout

```text
PlaywrightAgent/
  ├─ __init__.py
  ├─ agent.py          # Defines `root_agent` (LlmAgent) configured with Playwright MCP
  └─ README.md         # This file
```

The agent launches the MCP server via:

```text
npx @playwright/mcp@latest
```

with a 60s MCP I/O timeout and a 120s server start timeout.

---

## How to run

The code declares an `LlmAgent` instance named `root_agent` in `agent.py`. Depending on your setup of `google.adk`, you can run the agent in one of the following ways.

### A) Minimal runner script (recommended)

Create a `runner.py` next to `agent.py` with:

```python
from PlaywrightAgent.agent import root_agent

# Start an interactive loop in the terminal
root_agent.run()
```

Run it:

```bash
python -m PlaywrightAgent.runner
```

If you prefer to avoid creating a file, you can also use a one-liner:

```bash
python -c "from PlaywrightAgent.agent import root_agent; root_agent.run()"
```

### B) Using an ADK CLI (if available in your environment)

Some `google.adk` distributions include a CLI runner. If present, you can run something like:

```bash
python -m google.adk.cli run PlaywrightAgent.agent:root_agent
```

If the CLI is not available, use option A.

### C) Run with ADK Web UI

Launch a local web UI that connects to this agent.

Install the web extra if you haven't:

```bash
pip install "google-adk[web]"
```

Start the web app (one of these variants depending on your ADK installation):

```bash
# Canonical (per docs): run from the PARENT of your agent folder
# Example for this repo:
cd /home/drona/Documents/GitHub/Miniprojects/Google_ADK
adk web

# Alternative: explicitly specify the agent path (works in many envs)
adk web --agent PlaywrightAgent.agent:root_agent --host 0.0.0.0 --port 8000
python -m google.adk.web --agent PlaywrightAgent.agent:root_agent --host 0.0.0.0 --port 8000
python -m google.adk.cli web PlaywrightAgent.agent:root_agent --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000` in your browser. In the top-left agent dropdown, select `PlaywrightAgent` (your agent package). If it doesn't appear, ensure you ran `adk web` from the parent directory of `PlaywrightAgent`.

Reference: ADK Quickstart — Set up, run in Dev UI: [google.github.io/adk-docs Quickstart](https://google.github.io/adk-docs/get-started/quickstart/#set-up-environment-install-adk).

---

## Example session

After starting the agent, try prompts like:

- "Go to https://example.com and tell me the main heading."
- "Open https://news.ycombinator.com and list the top 5 story titles."

The agent will:
1. Navigate using the Playwright MCP tool
2. Inspect the page content
3. Respond with extracted information

---

## Troubleshooting

- Missing Node or `npx`:
  - Install Node 18+ and ensure `npx` is on your PATH.
- Playwright browsers not installed:
  - Run `npx playwright install`.
- Timeouts when starting MCP:
  - The project sets a 120s server start timeout and 60s I/O timeout.
  - On slow networks, re-run after the first `npx @playwright/mcp@latest` download completes.
- Authentication errors with Gemini:
  - Ensure `GOOGLE_API_KEY` is exported and valid for `gemini-2.5-pro`.
- Headful browser on Linux:
  - Ensure required libs are installed (e.g., `libX11`, `libXcomposite`, `libnss3`). `npx playwright install-deps` can help.

---

## Development notes

- The agent prompt guides the tool usage: navigate, interact/extract, respond clearly.
- The MCP server command is configured in `agent.py` via `StdioServerParameters`.
- Adjust model or timeouts in `agent.py` as needed.

---

## License

All rights reserved @ Dronanaik

