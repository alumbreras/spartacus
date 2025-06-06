#!/bin/bash

# Spartacus Main Startup Script
# Orchestrates both backend and frontend

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# PID files to track processes
SPARTACUS_BACKEND_PID_FILE="$PROJECT_ROOT/.spartacus_backend.pid"
SPARTACUS_FRONTEND_PID_FILE="$PROJECT_ROOT/.spartacus_frontend.pid"

echo -e "${BLUE}=================================================="
echo "🏛️  SPARTACUS DESKTOP LAUNCHER"
echo "   Claude Desktop Alternative"
echo -e "==================================================${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down Spartacus Desktop...${NC}"
    
    # Kill backend if running
    if [ -f ".spartacus_backend_pid" ]; then
        BACKEND_PID=$(cat .spartacus_backend_pid 2>/dev/null || echo "")
        if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo -e "   Stopping backend (PID: $BACKEND_PID)..."
            kill "$BACKEND_PID" 2>/dev/null || true
        fi
        rm -f .spartacus_backend_pid
    fi
    
    # Kill frontend if running
    if [ -f ".spartacus_frontend_pid" ]; then
        FRONTEND_PID=$(cat .spartacus_frontend_pid 2>/dev/null || echo "")
        if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
            echo -e "   Stopping frontend (PID: $FRONTEND_PID)..."
            kill "$FRONTEND_PID" 2>/dev/null || true
        fi
        rm -f .spartacus_frontend_pid
    fi
    
    # Clean up port file
    rm -f .spartacus_backend_port
    
    echo -e "${GREEN}✅ Spartacus Desktop stopped${NC}"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Start backend in background
echo -e "${BLUE}🚀 Starting Backend...${NC}"
./start_backend.sh > backend.log 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > .spartacus_backend_pid
echo -e "   Backend PID: $BACKEND_PID"

# Wait for backend to be ready
echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
ATTEMPTS=0
MAX_ATTEMPTS=30

while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
    if [ -f ".spartacus_backend_port" ] && curl -s "http://127.0.0.1:$(cat .spartacus_backend_port)/health" > /dev/null 2>&1; then
        PORT=$(cat .spartacus_backend_port)
        echo -e "${GREEN}✅ Backend ready at http://127.0.0.1:$PORT${NC}"
        break
    fi
    
    ATTEMPTS=$((ATTEMPTS + 1))
    echo -e "   Attempt $ATTEMPTS/$MAX_ATTEMPTS..."
    sleep 2
done

if [ $ATTEMPTS -eq $MAX_ATTEMPTS ]; then
    echo -e "${RED}❌ Backend failed to start within timeout${NC}"
    exit 1
fi

# Start frontend in background
echo -e "${BLUE}🎨 Starting Frontend...${NC}"
./start_frontend.sh > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > .spartacus_frontend_pid
echo -e "   Frontend PID: $FRONTEND_PID"

# Show status
PORT=$(cat .spartacus_backend_port)
echo -e "\n${GREEN}🎉 Spartacus Desktop is running!${NC}"
echo -e "${GREEN}   Backend:  http://127.0.0.1:$PORT${NC}"
echo -e "${GREEN}   Frontend: Electron app launched${NC}"
echo -e "${GREEN}   Docs:     http://127.0.0.1:$PORT/docs${NC}"
echo -e "\n${YELLOW}💡 Press Ctrl+C to stop${NC}"

# Monitor processes
while true; do
    # Check if backend is still running
    if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo -e "${RED}❌ Backend process died (PID: $BACKEND_PID)${NC}"
        break
    fi
    
    # Check if frontend is still running
    if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo -e "${YELLOW}ℹ️  Frontend closed (backend still running)${NC}"
        echo -e "${YELLOW}💡 Run './start_frontend.sh' to reopen the frontend${NC}"
        
        # Remove frontend PID file since it's not running
        rm -f .spartacus_frontend_pid
        
        # Wait for backend or user interrupt
        wait "$BACKEND_PID" 2>/dev/null || true
        break
    fi
    
    sleep 2
done 