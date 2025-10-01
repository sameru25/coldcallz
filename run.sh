#!/bin/bash

# Cold Calling Assistant Startup Script

echo "🚀 Starting Cold Calling Assistant..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📋 Installing dependencies..."
pip install --upgrade pip
pip install numpy==1.25.2  # Install compatible numpy first
pip install -r requirements.txt

# Start Streamlit app
echo "🎯 Launching application..."
streamlit run streamlit_app.py

echo "✅ Application ready! Open your browser to the URL shown above." 