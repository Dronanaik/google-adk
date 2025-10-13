# Quick Start Guide - Streamlit Code Generator Agent

Get up and running in 5 minutes! ⚡

## Step 1: Get Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy your API key

## Step 2: Run Setup

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

The setup script will:

- Check Python version
- Create virtual environment
- Install dependencies
- Help you configure your API key

## Step 3: Start the Agent

### Option A: Web Interface (Recommended)

```bash
# Activate virtual environment
source .venv/bin/activate

# Start web interface
adk web
```

Then open http://localhost:8000 in your browser.

### Option B: Command Line

```bash
# Activate virtual environment
source .venv/bin/activate

# Start CLI
adk run streamlit_code_generator
```

## Step 4: Chat with Your Agent

Try these example prompts:

```
"Create a dashboard app with metrics and charts"

"Generate a data explorer that can load CSV files"

"Build a form application with validation"

"I need a calculator app"

"Create an ML demo with the iris dataset"
```

## Step 5: Test Generated Apps

```bash
# Navigate to generated apps
cd generated_apps

# Run a generated app
streamlit run dashboard_app.py
```

## 🎯 Common Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run web interface
adk web

# Run CLI interface
adk run streamlit_code_generator

# Run API server
adk api_server

# Deactivate virtual environment
deactivate
```

## 🐳 Using Docker

```bash
# Build image
docker build -t streamlit-agent -f Dockerfile.streamlit .

# Run container
docker run -it -p 8000:8000 \
  -e GOOGLE_API_KEY=your_api_key \
  streamlit-agent
```

## 🆘 Troubleshooting

### "Agent not found in dropdown"

- Make sure you're in the parent directory when running `adk web`
- Check that `streamlit_code_generator/__init__.py` exists

### "API key error"

- Verify your API key in `streamlit_code_generator/.env`
- Make sure there are no extra spaces or quotes

### "Module not found"

- Activate virtual environment: `source .venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## 📚 Next Steps

- Read the full [README_STREAMLIT_AGENT.md](README_STREAMLIT_AGENT.md)
- Check out [Google ADK Documentation](https://google.github.io/adk-docs/)
- Explore [Streamlit Documentation](https://docs.streamlit.io/)

---

**Need help?** Check the troubleshooting section in README_STREAMLIT_AGENT.md
