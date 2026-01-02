# 📊 Data Analysis Agent

A powerful AI-driven agent capable of connecting to your databases, understanding your data schema, and answering natural language questions by generating and executing SQL queries. Built with [Google Agent Development Kit (ADK)](https://github.com/google/adk) and [Streamlit](https://streamlit.io/).

![Demo Video](assets/demo.webm)

## ✨ Features

*   **Natural Language to SQL:** Translate plain English questions into valid SQL queries.
*   **Multi-Database Support:** Connects to PostgreSQL, MySQL, and Google BigQuery.
*   **Schema Awareness:** Automatically inspects database tables and schemas to understand your data structure.
*   **Interactive UI:** User-friendly chat interface built with Streamlit.
*   **Read-Only Safety:** Designed to execute only read-only queries (SELECT) to protect your data.
*   **Data Visualization:** (Coming Soon) Automatically generate charts and graphs from query results.

## 🚀 Getting Started

### Prerequisites

*   **Python 3.10+**
*   **Google Cloud Project** (for BigQuery or Vertex AI)
*   **Google AI Studio API Key** (for Gemini models)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd data_analysis_agent
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 🏃‍♂️ Running the Application

1.  **Start the Streamlit app:**
    ```bash
    streamlit run ui/app.py
    ```

2.  **Configure the Agent:**
    *   Open the app in your browser (usually `http://localhost:8501`).
    *   In the sidebar, enter your **Google API Key**.
    *   Select your **Database Type** (PostgreSQL, MySQL, or BigQuery).
    *   Enter your database connection details (Host, Port, User, Password, Database Name).
    *   Click **Connect**.

3.  **Ask Questions:**
    *   Once connected, simply type your question in the chat box.
    *   *Example:* "Show me the top 5 customers by total sales."
    *   *Example:* "Count the number of orders placed last month."

## 📂 Project Structure

```
data_analysis_agent/
├── agent/
│   └── agent.py            # Core agent logic and ADK integration
├── ui/
│   └── app.py              # Streamlit user interface
├── utils/
│   ├── db_connector.py     # Database connection handler
│   └── schema_inspector.py # Schema introspection tools
├── assets/
│   └── demo.webm           # Demo video
├── requirements.txt        # Python dependencies
└── verify_setup.py         # Setup verification script
```

## 🛠️ Technologies Used

*   **Google ADK:** Framework for building agentic applications.
*   **Google Gemini:** Large Language Model for reasoning and SQL generation.
*   **Streamlit:** Rapid UI development for data apps.
*   **SQLAlchemy:** Database toolkit and ORM.
*   **Pandas:** Data manipulation and analysis.

## 🛡️ Security Note

This agent is designed to be a helpful assistant. While it includes basic safeguards against destructive queries, always ensure you are connecting to a database with appropriate permissions (preferably a read-only user) when using it in a production environment.
