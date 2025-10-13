#!/bin/bash

# Streamlit Code Generator Agent - Setup Script

echo "=========================================="
echo "Streamlit Code Generator Agent Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if version is 3.9 or higher
required_version="3.9"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.9 or higher is required"
    exit 1
fi

echo "✓ Python version is compatible"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check if .env file exists
echo "Checking configuration..."
if [ -f "streamlit_code_generator/.env" ]; then
    # Check if API key is set
    if grep -q "YOUR_API_KEY_HERE" streamlit_code_generator/.env; then
        echo "⚠️  Warning: API key not configured"
        echo ""
        echo "Please edit streamlit_code_generator/.env and add your Google API key"
        echo "Get your API key from: https://aistudio.google.com/apikey"
        echo ""
        read -p "Press Enter to open the .env file in nano editor..."
        nano streamlit_code_generator/.env
    else
        echo "✓ Configuration file found"
    fi
else
    echo "❌ Error: .env file not found"
    exit 1
fi
echo ""

# Create generated_apps directory
echo "Creating output directory..."
mkdir -p generated_apps
echo "✓ Output directory created"
echo ""

echo "=========================================="
echo "Setup Complete! 🎉"
echo "=========================================="
echo ""
echo "To start using the agent:"
echo ""
echo "1. Activate the virtual environment (if not already active):"
echo "   source .venv/bin/activate"
echo ""
echo "2. Run the agent with web interface:"
echo "   adk web"
echo ""
echo "3. Or run with command line interface:"
echo "   adk run streamlit_code_generator"
echo ""
echo "4. Open http://localhost:8000 in your browser"
echo ""
echo "=========================================="