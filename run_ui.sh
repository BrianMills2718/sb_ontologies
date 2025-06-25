#!/bin/bash

# Schema Analysis UI Startup Script

echo "🔬 Starting Schema Analysis Pipeline UI..."

# Check if virtual environment exists
if [ ! -d "venv_ui" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv_ui
fi

# Activate virtual environment
source venv_ui/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements_ui.txt

# Run Streamlit app
echo "🚀 Launching UI at http://localhost:8501"
streamlit run schema_analysis_ui.py --server.port 8501 --server.address localhost