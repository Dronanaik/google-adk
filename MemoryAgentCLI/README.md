# MemoryAgentCLI (StoryApp)

MemoryAgentCLI is a command-line interface (CLI) application designed to generate engaging and imaginative stories using Google's Generative AI (Gemini). It leverages the `google-adk` framework to manage agents and sessions, providing an interactive storytelling experience.

## Features

-   **Interactive CLI**: User-friendly command-line interface powered by `rich` for colorful and formatted output.
-   **AI-Powered Storytelling**: Uses Gemini models to generate creative stories based on user prompts.
-   **Agentic Architecture**: Utilizes a `root_agent` that delegates tasks to a specialized `story_agent`.
-   **Session Persistence**: Stores session data and interaction history in a local SQLite database (`agentmemo.db`).
-   **Asynchronous Execution**: Built with `asyncio` for efficient, non-blocking operations.

## Prerequisites

-   Python 3.8+
-   A Google Cloud Project with Vertex AI enabled or a Google AI Studio API Key.

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory:
    ```bash
    cd /path/to/MemoryAgentCLI
    ```

2.  **Install Dependencies**:
    Ensure you have the required Python packages installed. You can install them using `pip`:
    ```bash
    pip install google-genai rich python-dotenv
    ```
    *Note: This project also depends on `google-adk`. Ensure this package is available in your Python environment.*

## Configuration

1.  **Environment Variables**:
    The application uses a `.env` file for configuration. Ensure a `.env` file exists in the project root with the following variables:

    ```env
    GOOGLE_GENAI_USE_VERTEXAI=0  # Set to 1 if using Vertex AI, 0 for AI Studio
    GOOGLE_API_KEY=your_api_key_here
    MODEL_NAME=gemini-2.5-flash
    ```

## Usage

To start the application, run the `agent.py` script:

```bash
python agent.py
```

### Interacting with the Agent

-   **Start a Conversation**: Once the application starts, you will see a prompt `You:`. Type your request or story prompt here.
-   **Generate a Story**: Ask the agent to write a story about a specific topic (e.g., "Tell me a story about a brave knight").
-   **Exit**: Type `exit`, `quit`, or `:q` to terminate the session.

## Project Structure

-   `agent.py`: The main entry point of the application. Initializes the agents, session, and runs the CLI loop.
-   `.env`: Configuration file for API keys and model settings.
-   `agentmemo.db`: SQLite database file for storing session history.
-   `__init__.py`: Package initialization file.


