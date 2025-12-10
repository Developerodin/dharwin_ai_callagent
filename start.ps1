# Bolna Calling Agent - Startup Script (Windows PowerShell)
# This script starts both the Flask backend and Next.js frontend

Write-Host "🚀 Starting Bolna Calling Agent..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    exit 1
}

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js 18+ and try again" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please create a .env file with your BOLNA_API_KEY" -ForegroundColor Yellow
    Write-Host ""
}

# Setup Python virtual environment
Write-Host "📦 Setting up Python environment..." -ForegroundColor Cyan
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install Python dependencies if requirements.txt exists
if (Test-Path "requirements.txt") {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    pip install -q -r requirements.txt
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
}

# Setup Node.js dependencies
Write-Host ""
Write-Host "📦 Setting up Node.js environment..." -ForegroundColor Cyan
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Node.js dependencies (this may take a while)..." -ForegroundColor Yellow
    npm install
    Write-Host "✅ Node.js dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✅ Node.js dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Starting servers..." -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Start Flask API server in a new window
Write-Host "🔧 Starting Flask API server on http://localhost:5000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python api_server.py"

# Wait a moment for Flask to start
Start-Sleep -Seconds 3

# Start Next.js frontend in a new window
Write-Host "🌐 Starting Next.js frontend on http://localhost:3000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev"

Write-Host ""
Write-Host "✅ Servers are starting in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access points:" -ForegroundColor Yellow
Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   - API Server: http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "📝 Logs:" -ForegroundColor Yellow
Write-Host "   - Flask API server logs will appear in one window" -ForegroundColor White
Write-Host "   - Next.js logs will appear in another window" -ForegroundColor White
Write-Host ""
Write-Host "⏹️  To stop servers:" -ForegroundColor Yellow
Write-Host "   - Press Ctrl+C in each server window, then close the windows" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

