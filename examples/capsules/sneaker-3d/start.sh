#!/bin/bash
# Start the Nike 3D Experience Server

echo "🚀 Starting Nike 3D Experience..."
echo ""

# Check if Python 3 is installed
if command -v python3 &> /dev/null; then
    python3 serve.py
elif command -v python &> /dev/null; then
    python serve.py
else
    echo "❌ Python is not installed. Please install Python 3."
    echo "   Visit: https://www.python.org/downloads/"
    exit 1
fi
