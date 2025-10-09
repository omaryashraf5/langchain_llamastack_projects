#!/bin/bash

echo "================================"
echo "Executive Dashboard Launcher"
echo "================================"
echo ""

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

echo "Python 3 found: $(python3 --version)"
echo ""

echo "Checking if dependencies are installed..."
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "Dependencies already installed."
fi

echo ""
echo "Starting Executive Dashboard..."
echo "The dashboard will open in your default browser."
echo "Press Ctrl+C to stop the server."
echo ""

streamlit run app.py
