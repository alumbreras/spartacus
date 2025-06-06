#!/bin/bash

# Spartacus Backend Startup Script

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/spartacus_backend"
VENV_PATH="$PROJECT_ROOT/.venv"
LOGS_DIR="$PROJECT_ROOT/logs"
SPARTACUS_PORT_FILE="$PROJECT_ROOT/.spartacus_backend_port"
START_PORT=8000
MAX_PORT=8020

echo "🚀 Starting Spartacus Backend..."

# Create logs directory
mkdir -p "$LOGS_DIR"

# Activate virtual environment if it exists
if [[ -d "$VENV_PATH" ]]; then
    echo "✅ Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
else
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Recommended: source .venv/bin/activate"
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to find free port
find_free_port() {
    for ((port=$START_PORT; port<=$MAX_PORT; port++)); do
        if ! check_port $port; then
            echo $port
            return 0
        fi
    done
    echo "❌ No free ports found between $START_PORT and $MAX_PORT"
    exit 1
}

# Find available port
PORT=$(find_free_port)
echo "✅ Found free port: $PORT"

# Save port info for frontend
echo "$PORT" > "$SPARTACUS_PORT_FILE"
echo "📝 Backend port saved to $SPARTACUS_PORT_FILE"

# Navigate to backend directory
cd "$BACKEND_DIR"

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

echo "📂 Working directory: $(pwd)"
echo "🔧 PYTHONPATH: $PYTHONPATH"

# Start the backend
echo "⏳ Starting FastAPI server on port $PORT..."
echo "🌐 Backend will be available at: http://127.0.0.1:$PORT"

exec python3 -m uvicorn main:app --reload --host 127.0.0.1 --port $PORT 