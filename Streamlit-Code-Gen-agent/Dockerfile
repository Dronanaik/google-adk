# Dockerfile for Streamlit Code Generator Agent
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY streamlit_code_generator/ ./streamlit_code_generator/

# Create directory for generated apps
RUN mkdir -p generated_apps

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port for web interface
EXPOSE 8000

# Default command - run web interface
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8000"]