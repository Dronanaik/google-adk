# Streamlit Code Generator Agent

An intelligent AI agent built with **Google ADK (Agent Development Kit)** that generates Streamlit application code based on natural language requirements. This agent can create complete Streamlit apps, add components, and provide code snippets for various features.

## 🌟 Features

- **Complete App Generation**: Create full Streamlit applications (dashboards, data explorers, forms, calculators, ML demos)
- **Component Library**: Generate code for charts, inputs, layouts, and data displays
- **Smart Code Generation**: Clean, well-documented, and runnable Python code
- **Interactive Development**: Chat with the agent to build your app iteratively
- **File Management**: Save generated code directly to files
- **Multiple Interfaces**: Use CLI, web UI, or API

## 📋 Prerequisites

- Python 3.9 or later
- pip for package management
- Google API key (from [Google AI Studio](https://aistudio.google.com/apikey))

## 🚀 Quick Start

### 1. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
# On Linux/Mac:
source .venv/bin/activate
# On Windows CMD:
.venv\Scripts\activate.bat
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

Edit the `.env` file in the `streamlit_code_generator` directory:

```bash
# Open the .env file
nano streamlit_code_generator/.env
```

Add your Google API key:

```env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_actual_api_key_here
```

Get your API key from: https://aistudio.google.com/apikey

### 4. Run the Agent

#### Option A: Web Interface (Recommended)

```bash
adk web
```

Then open http://localhost:8000 in your browser and select "streamlit_code_generator" from the dropdown.

#### Option B: Command Line Interface

```bash
adk run streamlit_code_generator
```

#### Option C: API Server

```bash
adk api_server
```

## 💡 Usage Examples

### Example 1: Create a Complete Dashboard

**You:** "Create a dashboard app with metrics and charts"

**Agent:** Will generate a complete dashboard with:

- Multiple metrics cards
- Line and pie charts
- Data tables
- Sidebar controls

### Example 2: Add Specific Components

**You:** "Add a file uploader and a bar chart"

**Agent:** Will provide code snippets for:

- File upload component
- Bar chart visualization
- Integration instructions

### Example 3: Build a Data Explorer

**You:** "I need a data explorer app that can load CSV files and show statistics"

**Agent:** Will create a complete app with:

- CSV file uploader
- Data preview
- Statistical summary
- Column analysis
- Interactive visualizations

### Example 4: Create a Form Application

**You:** "Generate a contact form with validation"

**Agent:** Will build a form with:

- Multiple input fields
- Validation logic
- Submit button
- Success/error messages

## 🛠️ Available Tools

The agent has access to these tools:

### 1. `generate_streamlit_boilerplate`

Creates a basic Streamlit app structure with title and description.

### 2. `add_data_visualization`

Generates code for charts:

- Line charts
- Bar charts
- Scatter plots
- Area charts
- Maps

### 3. `add_user_input_components`

Creates input components:

- Text input
- Number input
- Sliders
- Select boxes
- Multi-select
- Checkboxes
- Radio buttons
- Date/time pickers
- File uploaders
- Forms

### 4. `add_layout_components`

Generates layout code:

- Sidebars
- Columns
- Tabs
- Expanders
- Containers

### 5. `add_data_display_components`

Creates data display elements:

- DataFrames
- Tables
- Metrics
- JSON viewers
- Code blocks

### 6. `create_complete_streamlit_app`

Generates complete applications:

- **Dashboard**: Metrics, charts, and data tables
- **Data Explorer**: CSV upload and analysis
- **Form App**: Multi-field forms with validation
- **Calculator**: Basic, BMI, and loan calculators
- **ML Demo**: Interactive machine learning demo

### 7. `save_streamlit_code`

Saves generated code to a file in the `generated_apps` directory.

## 📝 Sample Prompts

Try these prompts with the agent:

```
"Create a dashboard with revenue metrics and charts"

"I need a data visualization app with multiple chart types"

"Build a form for user registration with email and password"

"Generate a calculator app with basic operations"

"Create an ML demo app using the iris dataset"

"Add a sidebar with filters and a main area with a dataframe"

"I want a file uploader that displays CSV data in a table"

"Create a multi-tab layout with different content in each tab"

"Generate a metrics dashboard with KPIs"

"Build a data explorer that shows statistics and visualizations"
```

## 🎯 Generated App Types

### Dashboard App

- Multiple KPI metrics
- Interactive charts (line, pie, bar)
- Data tables
- Sidebar controls
- Real-time updates

### Data Explorer App

- CSV file upload
- Data preview and statistics
- Column analysis
- Interactive filtering
- Visualizations

### Form Application

- Multiple input types
- Validation logic
- Submit handling
- Success/error messages
- Data display

### Calculator App

- Basic calculator
- BMI calculator
- Loan calculator
- Custom calculations

### ML Demo App

- Dataset loading
- Model training
- Feature importance
- Interactive predictions
- Visualization

## 🧪 Testing Generated Apps

After generating code, you can test it:

1. **Save the code** (agent can do this automatically)
2. **Navigate to the generated_apps directory**:
   ```bash
   cd generated_apps
   ```
3. **Run the Streamlit app**:
   ```bash
   streamlit run your_app.py
   ```

## 📁 Project Structure

```
Docker/
├── streamlit_code_generator/
│   ├── __init__.py
│   ├── agent.py          # Main agent code with tools
│   └── .env              # API configuration
├── generated_apps/        # Generated Streamlit apps saved here
├── requirements.txt       # Python dependencies
└── README_STREAMLIT_AGENT.md
```

## 🔧 Configuration Options

### Using Google AI Studio (Default)

```env
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_api_key
```

### Using Google Cloud Vertex AI

```env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_LOCATION=us-central1
```

### Using Vertex AI Express Mode (Free Tier)

```env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_API_KEY=your_express_mode_api_key
```

## 🐳 Docker Support

### Build Docker Image

```bash
docker build -t streamlit-code-generator -f Dockerfile.streamlit .
```

### Run in Docker

```bash
docker run -it -p 8000:8000 \
  -e GOOGLE_API_KEY=your_api_key \
  streamlit-code-generator
```

## 🎨 Web UI Features

When using `adk web`, you get:

- **Chat Interface**: Natural conversation with the agent
- **Events Tab**: See all function calls and responses
- **Trace View**: Inspect latency and performance
- **Agent Selection**: Switch between different agents
- **Voice Input**: Talk to your agent (with supported models)

## 🔍 Troubleshooting

### Agent not found in dropdown

- Make sure you're running `adk web` from the parent directory of `streamlit_code_generator`
- Check that `__init__.py` exists and imports the agent

### API Key errors

- Verify your API key is correct in the `.env` file
- Check that the `.env` file is in the correct location
- Ensure no extra spaces or quotes around the API key

### Import errors

- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- Activate your virtual environment if you created one

### Generated app doesn't run

- Check that all required imports are included
- Install missing packages: `pip install streamlit pandas numpy plotly`
- Look for syntax errors in the generated code

## 📚 Learn More

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API](https://ai.google.dev/)

## 🤝 Contributing

Feel free to extend the agent with more tools and capabilities:

1. Add new tools in `agent.py`
2. Update the agent's instruction to include new capabilities
3. Test with various prompts
4. Share your improvements!

## 📄 License

This project is provided as-is for educational and development purposes.

## 🎉 Example Workflow

```bash
# 1. Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure
nano streamlit_code_generator/.env
# Add your API key

# 3. Run
adk web

# 4. Chat with agent
# "Create a dashboard app with charts and metrics"

# 5. Test generated app
cd generated_apps
streamlit run dashboard_app.py
```

## 💬 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review the [ADK documentation](https://google.github.io/adk-docs/)
3. Verify your API key and configuration
4. Check that all dependencies are installed

---
## Demo 

**Happy Coding! 🚀**

Built with ❤️ using Google ADK and Streamlit
