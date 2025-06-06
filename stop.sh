#!/bin/bash

# Spartacus Stop Script
# Gracefully stops all running processes

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# PID files
BACKEND_PID_FILE="$PROJECT_ROOT/.spartacus_backend_pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.spartacus_frontend_pid"

echo -e "${BLUE}🛑 Stopping Spartacus Desktop...${NC}"

# Function to stop a process by PID file
stop_process() {
    local pid_file=$1
    local process_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file" 2>/dev/null || echo "")
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}   Stopping $process_name (PID: $pid)...${NC}"
            kill "$pid" 2>/dev/null || true
            
            # Wait for graceful shutdown
            local count=0
            while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${YELLOW}   Force stopping $process_name...${NC}"
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
        rm -f "$pid_file"
    fi
}

# Stop frontend first
stop_process "$FRONTEND_PID_FILE" "Frontend"

# Stop backend
stop_process "$BACKEND_PID_FILE" "Backend"

# Clean up port file
rm -f .spartacus_backend_port

# Also kill any remaining processes on common ports
for port in 8000 8001 8002 8003 8004 8005 3000; do
    PID=$(lsof -ti :$port 2>/dev/null || echo "")
    if [ -n "$PID" ]; then
        echo -e "${YELLOW}   Killing process on port $port (PID: $PID)...${NC}"
        kill "$PID" 2>/dev/null || true
    fi
done

echo -e "${GREEN}✅ Spartacus Desktop stopped${NC}" 