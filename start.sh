#!/bin/bash

# Bolna Calling Agent - Startup Script (Linux/Mac)
# This script starts both the Flask backend and Next.js frontend

echo "🚀 Starting Bolna Calling Agent..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed or not in PATH"
    echo "Please install Node.js 18+ and try again"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your BOLNA_API_KEY"
    echo ""
fi

# Setup Python virtual environment
echo "📦 Setting up Python environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -q -r requirements.txt
    echo "✅ Python dependencies installed"
fi

# Setup Node.js dependencies
echo ""
echo "📦 Setting up Node.js environment..."
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies (this may take a while)..."
    npm install
    echo "✅ Node.js dependencies installed"
else
    echo "✅ Node.js dependencies already installed"
fi

echo ""
echo "============================================================"
echo "Starting servers..."
echo "============================================================"
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $FLASK_PID 2>/dev/null
    kill $NEXTJS_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

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
echo "✅ Servers are starting!"
echo ""
echo "📍 Access points:"
echo "   - Frontend: http://localhost:3000"
echo "   - API Server: http://localhost:5000"
echo ""
echo "📝 Logs:"
echo "   - Both servers are running in the background"
echo "   - Press Ctrl+C to stop all servers"
echo ""

# Wait for user interrupt
wait

