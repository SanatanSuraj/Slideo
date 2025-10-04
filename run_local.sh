#!/bin/bash

# Presenton Local Development Runner
# Runs FastAPI backend and Next.js frontend locally without Docker
#
# Usage:
#   chmod +x run_local.sh
#   ./run_local.sh
#
# Features:
#   - Automatically kills existing processes on ports 3000 and 8000
#   - Starts FastAPI backend on port 8000 with hot reload
#   - Starts Next.js frontend on port 3000 with hot reload
#   - Graceful shutdown with Ctrl+C
#   - Colorful status output
#   - Environment variable loading from .env file
#
# Requirements:
#   - Node.js 20+
#   - Python 3.11+
#   - Dependencies installed (run setup.sh first)

echo "🚀 Starting Presenton Local Development Environment"
echo "📋 This script runs FastAPI backend and Next.js frontend locally"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local service_name=$2
    if check_port $port; then
        print_status $YELLOW "🔄 Killing existing $service_name on port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 1
        if check_port $port; then
            print_status $RED "❌ Failed to kill $service_name on port $port"
            return 1
        else
            print_status $GREEN "✅ Successfully killed $service_name on port $port"
        fi
    else
        print_status $GREEN "✅ Port $port is available for $service_name"
    fi
}

# Function to cleanup on exit
cleanup() {
    print_status $YELLOW "🛑 Shutting down Presenton..."
    
    # Kill FastAPI server
    if [ ! -z "$FASTAPI_PID" ]; then
        print_status $YELLOW "🔄 Stopping FastAPI server (PID: $FASTAPI_PID)..."
        kill $FASTAPI_PID 2>/dev/null || true
    fi
    
    # Kill Next.js server
    if [ ! -z "$NEXTJS_PID" ]; then
        print_status $YELLOW "🔄 Stopping Next.js server (PID: $NEXTJS_PID)..."
        kill $NEXTJS_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes on our ports
    kill_port 8000 "FastAPI"
    kill_port 3000 "Next.js"
    
    print_status $GREEN "✅ Presenton stopped successfully"
    exit 0
}

# Set up signal handlers for graceful shutdown
trap cleanup SIGINT SIGTERM EXIT

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_status $RED "❌ Node.js is not installed. Please install Node.js 20+ from https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    print_status $RED "❌ Node.js version 20+ is required. Current version: $(node -v)"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_status $RED "❌ Python 3.11+ is not installed. Please install Python 3.11+ from https://python.org/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    print_status $RED "❌ Python 3.11+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

print_status $GREEN "✅ Node.js $(node -v) detected"
print_status $GREEN "✅ Python $PYTHON_VERSION detected"
echo ""

# Load environment variables from .env if it exists
if [ -f .env ]; then
    print_status $BLUE "📝 Loading environment variables from .env..."
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    print_status $GREEN "✅ Environment variables loaded"
else
    print_status $YELLOW "⚠️  No .env file found. Using system environment variables."
fi
echo ""

# Check and kill existing processes
print_status $BLUE "🔍 Checking for existing processes..."
kill_port 8000 "FastAPI"
kill_port 3000 "Next.js"
echo ""

# Check if required directories exist
if [ ! -d "servers/fastapi" ]; then
    print_status $RED "❌ FastAPI directory not found: servers/fastapi"
    exit 1
fi

if [ ! -d "servers/nextjs" ]; then
    print_status $RED "❌ Next.js directory not found: servers/nextjs"
    exit 1
fi

# Check if required files exist
if [ ! -f "servers/fastapi/server.py" ]; then
    print_status $RED "❌ FastAPI server file not found: servers/fastapi/server.py"
    exit 1
fi

if [ ! -f "servers/nextjs/package.json" ]; then
    print_status $RED "❌ Next.js package.json not found: servers/nextjs/package.json"
    exit 1
fi

# Start FastAPI server
print_status $BLUE "🚀 Starting FastAPI server on port 8000..."
cd servers/fastapi

# Start FastAPI server in background
python3 server.py --port 8000 --reload true &
FASTAPI_PID=$!

# Wait a moment for the server to start
sleep 2

# Check if FastAPI server started successfully
if ! kill -0 $FASTAPI_PID 2>/dev/null; then
    print_status $RED "❌ Failed to start FastAPI server"
    exit 1
fi

print_status $GREEN "✅ FastAPI server started (PID: $FASTAPI_PID)"
cd ../..

# Start Next.js server
print_status $BLUE "🚀 Starting Next.js development server on port 3000..."
cd servers/nextjs

# Start Next.js server in background
npm run dev &
NEXTJS_PID=$!

# Wait a moment for the server to start
sleep 3

# Check if Next.js server started successfully
if ! kill -0 $NEXTJS_PID 2>/dev/null; then
    print_status $RED "❌ Failed to start Next.js server"
    cleanup
    exit 1
fi

print_status $GREEN "✅ Next.js server started (PID: $NEXTJS_PID)"
cd ../..

echo ""
print_status $GREEN "🎉 Presenton is now running!"
echo ""
print_status $CYAN "📱 Access URLs:"
print_status $CYAN "   Frontend: http://localhost:3000"
print_status $CYAN "   Backend:  http://localhost:8000"
print_status $CYAN "   API Docs: http://localhost:8000/docs"
print_status $CYAN "   MCP Server: http://localhost:8001"
echo ""
print_status $YELLOW "💡 Press Ctrl+C to stop all servers"
echo ""

# Wait for user to stop the servers
print_status $BLUE "🔄 Monitoring servers... (Press Ctrl+C to stop)"
while true; do
    # Check if FastAPI server is still running
    if ! kill -0 $FASTAPI_PID 2>/dev/null; then
        print_status $RED "❌ FastAPI server stopped unexpectedly"
        cleanup
        exit 1
    fi
    
    # Check if Next.js server is still running
    if ! kill -0 $NEXTJS_PID 2>/dev/null; then
        print_status $RED "❌ Next.js server stopped unexpectedly"
        cleanup
        exit 1
    fi
    
    sleep 5
done
