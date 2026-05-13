#!/bin/bash

echo "Consulting Agent AI - Setup"
echo "=========================="
echo ""

PYTHON=$(command -v python3)
if [ -z "$PYTHON" ]; then
    echo "Error: Python 3 not found."
    exit 1
fi

echo "Python found: $($PYTHON --version)"

echo ""
echo "Installing dependencies..."
pip3 install -r "$(dirname "$0")/requirements.txt" 2>&1 | tail -3

echo ""
ENV_FILE="$(dirname "$0")/.env"
if [ ! -f "$ENV_FILE" ]; then
    cp "$(dirname "$0")/.env.example" "$ENV_FILE"
fi

if grep -q "AIza" "$ENV_FILE" 2>/dev/null; then
    echo "Gemini API key already configured."
else
    echo "Gemini API Key Setup"
    echo "-------------------"
    echo "Get a free key at: https://aistudio.google.com/apikey"
    read -p "Enter your Gemini API key: " KEY
    if [ -n "$KEY" ]; then
        echo "GEMINI_API_KEY=$KEY" > "$ENV_FILE"
        echo "Key saved."
    else
        echo "Edit .env manually later."
    fi
fi

echo ""
echo "Done. Run:"
echo "  python3 $(dirname "$0")/consulting_agent.py --company \"Nvidia\" --question \"Growth strategy\" --ticker NVDA"
