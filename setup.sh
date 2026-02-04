#!/bin/bash

# Jarvis Personal Assistant - Quick Setup Script
# This script sets up the development environment

echo "🚀 Jarvis - Personal AI Assistant Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file (fill in your Pinecone API key)..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your PINECONE_API_KEY"
fi

echo ""
echo "========================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your PINECONE_API_KEY"
echo "2. Start Ollama: ollama serve"
echo "3. Start backend: cd backend && python main.py"
echo "4. Start frontend: cd frontend && streamlit run app.py"
echo ""
echo "Then open: http://localhost:8501"
