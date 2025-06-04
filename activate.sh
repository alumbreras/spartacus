#!/bin/bash

# Spartacus Desktop - Development Environment Activation

echo "🚀 Activating Spartacus Development Environment..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Creating .venv..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Check if requirements are installed
if ! pip list | grep -q "fastapi"; then
    echo "📦 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

echo "✅ Spartacus environment activated!"
echo ""
echo "📋 Available commands:"
echo "  python test_standalone.py     - Test the agentic_lib"
echo "  pip install -r requirements.txt - Install/update dependencies"
echo "  deactivate                    - Exit virtual environment"
echo ""
echo "📁 Project structure:"
echo "  agentic_lib/         - Your agent library"
echo "  llm_clients/         - LLM clients (Azure OpenAI)"
echo "  spartacus_services/  - Standalone services"
echo "  doc_agent/          - Development plans"
echo ""
echo "💡 Next steps: Start working on Phase 2 (FastAPI Backend)"
echo ""

# Show Python environment info
echo "🐍 Python environment:"
echo "  Python: $(python --version)"
echo "  Virtual env: $VIRTUAL_ENV"
echo "  Working dir: $(pwd)"
echo ""

# Show if credentials are configured
if [ -z "$AZURE_OPENAI_API_KEY" ]; then
    echo "⚠️  Azure OpenAI credentials not configured"
    echo "   Set AZURE_OPENAI_API_KEY environment variable for full functionality"
else
    echo "🔑 Azure OpenAI credentials configured"
fi

echo ""
echo "🎯 Ready to build Spartacus! 🚀" 