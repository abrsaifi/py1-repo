#!/bin/bash

# DocPro - Quick Setup & Run Guide

echo "================================================"
echo "DocPro - Document Management Suite"
echo "Quick Setup & Run Guide"
echo "================================================"
echo ""

# Check Python version
echo "✓ Checking Python installation..."
python --version

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
    echo "✓ Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Install requirements
echo "✓ Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "✓ Initializing database..."
python -c "from app.services.database import init_db; init_db(); print('Database initialized')"

# Setup logging
echo "✓ Setting up logging system..."
mkdir -p logs

# Start application
echo ""
echo "================================================"
echo "Starting DocPro Application..."
echo "================================================"
echo ""
echo "Server will be available at: http://localhost:5000"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python -m app.main
