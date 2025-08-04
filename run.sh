#!/bin/bash

# Interactive Facts Map - Run Script
echo "🗺️  Starting Interactive Facts Map..."
echo "📍 Open your browser to http://localhost:8501 when ready"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Run the Streamlit app
streamlit run main.py
