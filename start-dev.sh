#!/bin/bash

# Bolna Calling Agent - Development Startup Script (Linux/Mac)
# This script starts ngrok, Flask backend, and Next.js frontend
# Use this script after initial setup (dependencies already installed)

echo "🚀 Starting Bolna Calling Agent (Development Mode)..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    exit 1
fi

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed or not in PATH"
    echo "Install from: https://ngrok.com/download"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./start.sh first to set up the project"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Node modules not found!"
    echo "Please run ./start.sh first to set up the project"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your BOLNA_API_KEY"
    echo ""
fi

echo "============================================================"
echo "Starting Development Servers..."
echo "============================================================"
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $NGROK_PID 2>/dev/null
    kill $FLASK_PID 2>/dev/null
    kill $NEXTJS_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start ngrok in background
echo "🌐 Starting ngrok tunnel on port 5000..."
ngrok http 5000 > /dev/null 2>&1 &
NGROK_PID=$!

# Wait for ngrok to initialize
echo "   Waiting for ngrok to initialize..."
sleep 5

# Get ngrok URL
NGROK_URL=""
if command -v curl &> /dev/null; then
    NGROK_RESPONSE=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null)
    if [ ! -z "$NGROK_RESPONSE" ]; then
        # Try to extract HTTPS URL (jq preferred, but fallback to grep/sed)
        if command -v jq &> /dev/null; then
            NGROK_URL=$(echo "$NGROK_RESPONSE" | jq -r '.tunnels[] | select(.proto=="https") | .public_url' | head -1)
            if [ -z "$NGROK_URL" ]; then
                NGROK_URL=$(echo "$NGROK_RESPONSE" | jq -r '.tunnels[0].public_url' 2>/dev/null)
            fi
        else
            # Fallback: try to extract URL with grep/sed
            NGROK_URL=$(echo "$NGROK_RESPONSE" | grep -o '"public_url":"https://[^"]*' | head -1 | sed 's/"public_url":"//')
        fi
    fi
fi

if [ ! -z "$NGROK_URL" ]; then
    echo "   ✅ ngrok URL: $NGROK_URL"
    echo "   📋 Webhook URL: $NGROK_URL/api/webhook"
    echo ""
else
    echo "   ⚠️  ngrok started but URL not yet available"
    echo "   Check ngrok at: http://localhost:4040"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Start Flask API server in background
echo "🔧 Starting Flask API server on http://localhost:5000..."
python api_server.py &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 3

# Start Next.js frontend in background
echo "🌐 Starting Next.js frontend on http://localhost:3000..."
npm run dev &
NEXTJS_PID=$!

echo ""
echo "✅ All servers are starting!"
echo ""
echo "📍 Access Points:"
echo "   - Frontend: http://localhost:3000"
echo "   - API Server: http://localhost:5000"
if [ ! -z "$NGROK_URL" ]; then
    echo "   - Public URL (ngrok): $NGROK_URL"
    echo "   - Webhook URL: $NGROK_URL/api/webhook"
else
    echo "   - ngrok Dashboard: http://localhost:4040"
fi
echo ""
echo "📝 Logs:"
echo "   - All servers are running in the background"
echo "   - Check ngrok dashboard: http://localhost:4040"
echo "   - Press Ctrl+C to stop all servers"
echo ""

# Wait for user interrupt
wait

