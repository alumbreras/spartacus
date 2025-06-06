#!/bin/bash

# Spartacus Frontend Startup Script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎨 Starting Spartacus Frontend...${NC}"

# Check if backend is running by reading the port file
if [ ! -f ".spartacus_backend_port" ]; then
    echo -e "${RED}❌ Backend not running. Start backend first with: ./start_backend.sh${NC}"
    exit 1
fi

BACKEND_PORT=$(cat .spartacus_backend_port)
BACKEND_URL="http://127.0.0.1:$BACKEND_PORT"

# Test backend connection
echo -e "${BLUE}🔗 Checking backend connection...${NC}"
if ! curl -s "$BACKEND_URL/health" > /dev/null; then
    echo -e "${RED}❌ Backend not responding at $BACKEND_URL${NC}"
    echo -e "   Start backend first with: ./start_backend.sh"
    exit 1
fi

echo -e "${GREEN}✅ Backend is running at $BACKEND_URL${NC}"

# Navigate to frontend directory
cd spartacus_frontend

# Set the API URL as environment variable for Vite
export VITE_SPARTACUS_API_URL="$BACKEND_URL"

echo -e "${BLUE}🔧 API URL: $VITE_SPARTACUS_API_URL${NC}"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  Installing frontend dependencies...${NC}"
    npm install
fi

# Start the frontend
echo -e "${BLUE}⏳ Starting React + Electron app...${NC}"
npm run dev 