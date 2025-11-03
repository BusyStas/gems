#!/bin/bash

# Quick start script for Gems Hub development

echo "🚀 Starting Gems Hub Development Server"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists, if not copy from example
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Run the application
echo "✨ Starting Flask application..."
echo "🌐 Open http://localhost:8080 in your browser"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
