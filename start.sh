#!/bin/bash

# Jarvis - Complete Startup Script for macOS
# This script starts all 4 components needed to run the system

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Jarvis - Personal AI Assistant Startup Script          ║"
echo "║                   for macOS                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to check if port is in use
is_port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null
    return $?
}

# Function to create a new terminal window and run a command
run_in_new_terminal() {
    local title=$1
    local command=$2
    
    osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$SCRIPT_DIR' && $command"
end tell
EOF
}

# Function to open URL in default browser
open_url() {
    sleep 3
    open "$1"
}

echo -e "${YELLOW}[1/5]${NC} Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠ Ollama not found. Download from: https://ollama.ai${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check .env file
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from template...${NC}"
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo -e "${YELLOW}  → Edit .env and add your PINECONE_API_KEY${NC}"
fi

echo -e "${GREEN}✓ Prerequisites checked${NC}"

echo -e "\n${YELLOW}[2/5]${NC} Setting up Python environment..."

# Check for virtual environment
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install dependencies
echo -e "\n${YELLOW}[3/5]${NC} Installing dependencies..."
pip install -q -r "$SCRIPT_DIR/requirements.txt"
echo -e "${GREEN}✓ Dependencies installed${NC}"

echo -e "\n${YELLOW}[4/5]${NC} Starting services..."

# Check ports
if is_port_in_use 11434; then
    echo -e "${GREEN}✓ Ollama already running on port 11434${NC}"
else
    echo "Starting Ollama..."
    # Try to start Ollama if it's not running
    if command -v ollama &> /dev/null; then
        run_in_new_terminal "Ollama" "ollama serve"
        sleep 2
        echo -e "${GREEN}✓ Ollama started (new Terminal window)${NC}"
    fi
fi

# Check FastAPI backend port
if is_port_in_use 8000; then
    echo -e "${YELLOW}⚠ Port 8000 already in use${NC}"
else
    echo "Starting FastAPI backend..."
    run_in_new_terminal "Jarvis Backend" "source venv/bin/activate && cd backend && python main.py"
    sleep 3
    echo -e "${GREEN}✓ Backend started (new Terminal window)${NC}"
fi

# Check Streamlit port
if is_port_in_use 8501; then
    echo -e "${YELLOW}⚠ Port 8501 already in use${NC}"
else
    echo "Starting Streamlit frontend..."
    run_in_new_terminal "Jarvis Frontend" "source venv/bin/activate && cd frontend && streamlit run app.py"
    sleep 2
    echo -e "${GREEN}✓ Frontend started (new Terminal window)${NC}"
fi

echo -e "\n${YELLOW}[5/5]${NC} Indexing sample documents..."
sleep 2

# Index documents
python3 "$SCRIPT_DIR/data/init_data.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Sample documents indexed${NC}"
else
    echo -e "${YELLOW}⚠ Could not index documents (make sure backend is running)${NC}"
fi

echo -e "\n${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    ✨ All Set! ✨                          ║"
echo "║                                                            ║"
echo "║  Opening Jarvis in your default browser...                 ║"
echo "║  → http://localhost:8501                                   ║"
echo "║                                                            ║"
echo "║  3 new Terminal windows have been opened:                  ║"
echo "║  1. Ollama server                                          ║"
echo "║  2. FastAPI backend                                        ║"
echo "║  3. Streamlit frontend                                     ║"
echo "║                                                            ║"
echo "║  To stop everything: CMD+Q in each Terminal               ║"
echo "║                                                            ║"
echo "║  Documentation: README.md, QUICKREF.md, ARCHITECTURE.md    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Open browser
open_url "http://localhost:8501"
