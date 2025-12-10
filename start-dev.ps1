# Bolna Calling Agent - Development Startup Script (Windows PowerShell)
# This script starts ngrok, Flask backend, and Next.js frontend
# Use this script after initial setup (dependencies already installed)

Write-Host "🚀 Starting Bolna Calling Agent (Development Mode)..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if ngrok is installed
if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ngrok is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Install from: https://ngrok.com/download" -ForegroundColor Yellow
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run .\start.ps1 first to set up the project" -ForegroundColor Yellow
    exit 1
}

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "❌ Node modules not found!" -ForegroundColor Red
    Write-Host "Please run .\start.ps1 first to set up the project" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please create a .env file with your BOLNA_API_KEY" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Development Servers..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Start ngrok in a new window
Write-Host "🌐 Starting ngrok tunnel on port 5000..." -ForegroundColor Cyan
$ngrokCmd = "Write-Host '🌐 ngrok Tunnel (Port 5000)' -ForegroundColor Cyan; Write-Host ''; ngrok http 5000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $ngrokCmd

# Wait a moment for ngrok to initialize
Write-Host "   Waiting for ngrok to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Get ngrok URL
$ngrokUrl = $null
try {
    $response = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -TimeoutSec 3 -ErrorAction SilentlyContinue
    if ($response.tunnels) {
        $httpsTunnel = $response.tunnels | Where-Object { $_.proto -eq "https" }
        if ($httpsTunnel) {
            $ngrokUrl = $httpsTunnel.public_url
        } elseif ($response.tunnels[0]) {
            $ngrokUrl = $response.tunnels[0].public_url
        }
    }
} catch {
    Write-Host "   ⚠️  Could not fetch ngrok URL automatically" -ForegroundColor Yellow
}

if ($ngrokUrl) {
    Write-Host "   ✅ ngrok URL: $ngrokUrl" -ForegroundColor Green
    Write-Host "   📋 Webhook URL: $ngrokUrl/api/webhook" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "   ⚠️  ngrok started but URL not yet available" -ForegroundColor Yellow
    Write-Host "   Check ngrok window or visit: http://localhost:4040" -ForegroundColor Gray
    Write-Host ""
}

# Start Flask API server in a new window
Write-Host "🔧 Starting Flask API server on http://localhost:5000..." -ForegroundColor Cyan
$flaskCmd = "cd '$PWD'; .\venv\Scripts\Activate.ps1; Write-Host '🔧 Flask API Server (Port 5000)' -ForegroundColor Cyan; Write-Host ''; python api_server.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $flaskCmd

# Wait a moment for Flask to start
Write-Host "   Waiting for Flask to start..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Start Next.js frontend in a new window
Write-Host "🌐 Starting Next.js frontend on http://localhost:3000..." -ForegroundColor Cyan
$nextjsCmd = "cd '$PWD'; Write-Host '🌐 Next.js Frontend (Port 3000)' -ForegroundColor Cyan; Write-Host ''; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $nextjsCmd

Write-Host ""
Write-Host "✅ All servers are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access Points:" -ForegroundColor Yellow
Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   - API Server: http://localhost:5000" -ForegroundColor White
if ($ngrokUrl) {
    Write-Host "   - Public URL (ngrok): $ngrokUrl" -ForegroundColor White
    Write-Host "   - Webhook URL: $ngrokUrl/api/webhook" -ForegroundColor White
} else {
    Write-Host "   - ngrok Dashboard: http://localhost:4040" -ForegroundColor White
}
Write-Host ""
Write-Host "📝 Logs:" -ForegroundColor Yellow
Write-Host "   - ngrok logs: First window" -ForegroundColor White
Write-Host "   - Flask API logs: Second window" -ForegroundColor White
Write-Host "   - Next.js logs: Third window" -ForegroundColor White
Write-Host ""
Write-Host "⏹️  To stop servers:" -ForegroundColor Yellow
Write-Host "   - Press Ctrl+C in each window, then close all windows" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

