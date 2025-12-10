# Quick Start Commands

This guide provides individual commands to start each component of the Bolna Calling Agent project.

## Prerequisites

Make sure you have:
- ✅ Python 3.8+ installed
- ✅ Node.js 18+ installed
- ✅ ngrok installed ([download here](https://ngrok.com/download))
- ✅ Virtual environment created (`.\start.ps1` on Windows or `./start.sh` on Linux/Mac)

---

## Step-by-Step Startup Guide

### Step 1: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

---

### Step 2: Start ngrok Tunnel

Open a **new terminal window** and run:

```bash
ngrok http 5000
```

**What this does:**
- Creates a public URL that tunnels to your local Flask server (port 5000)
- You'll see a URL like: `https://xxxx-xxxx-xxxx.ngrok-free.app`
- Copy the **HTTPS URL** (not HTTP)
- Your webhook URL will be: `https://xxxx-xxxx-xxxx.ngrok-free.app/api/webhook`

**Keep this terminal window open!**

---

### Step 3: Start Flask Backend (API Server)

Open a **new terminal window**, navigate to the project directory, and run:

**Windows (PowerShell):**
```powershell
# Navigate to project directory
cd "C:\Users\sharm\Desktop\Bolna Calling Agent"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start Flask server
python api_server.py
```

**Linux/Mac:**
```bash
# Navigate to project directory
cd "/path/to/Bolna Calling Agent"

# Activate virtual environment
source venv/bin/activate

# Start Flask server
python api_server.py
```

**What this does:**
- Starts the Flask API server on `http://localhost:5000`
- Handles API requests from the frontend
- Receives webhooks from Bolna AI

**Keep this terminal window open!**

---

### Step 4: Start Next.js Frontend

Open a **new terminal window**, navigate to the project directory, and run:

**Windows (PowerShell):**
```powershell
# Navigate to project directory
cd "C:\Users\sharm\Desktop\Bolna Calling Agent"

# Start Next.js development server
npm run dev
```

**Linux/Mac:**
```bash
# Navigate to project directory
cd "/path/to/Bolna Calling Agent"

# Start Next.js development server
npm run dev
```

**What this does:**
- Starts the Next.js frontend on `http://localhost:3000`
- Opens the web interface for managing candidates and calls

**Keep this terminal window open!**

---

## Access Points

Once all servers are running, you can access:

- 🌐 **Frontend UI**: http://localhost:3000
- 🔧 **API Server**: http://localhost:5000
- 📡 **ngrok Dashboard**: http://localhost:4040
- 🔗 **Public Webhook URL**: `https://xxxx-xxxx-xxxx.ngrok-free.app/api/webhook` (from ngrok window)

---

## Configure Webhook in Bolna AI Dashboard

1. Go to [Bolna AI Platform](https://platform.bolna.ai/)
2. Navigate to your agent settings
3. Find the "Webhook URL" or "Push all execution data to webhook" section
4. Paste your ngrok webhook URL: `https://xxxx-xxxx-xxxx.ngrok-free.app/api/webhook`
5. Save the configuration

---

## Stopping the Servers

To stop all servers:

1. Go to each terminal window
2. Press `Ctrl+C` in each window
3. Close the terminal windows

**Order doesn't matter** - you can stop them in any order.

---

## Quick Reference: All Commands in One Place

### Terminal 1: ngrok
```bash
ngrok http 5000
```

### Terminal 2: Flask Backend
**Windows:**
```powershell
cd "C:\Users\sharm\Desktop\Bolna Calling Agent"
.\venv\Scripts\Activate.ps1
python api_server.py
```

**Linux/Mac:**
```bash
cd "/path/to/Bolna Calling Agent"
source venv/bin/activate
python api_server.py
```

### Terminal 3: Next.js Frontend
**Windows:**
```powershell
cd "C:\Users\sharm\Desktop\Bolna Calling Agent"
npm run dev
```

**Linux/Mac:**
```bash
cd "/path/to/Bolna Calling Agent"
npm run dev
```

---

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

**Check what's using the port:**
- **Windows:** `netstat -ano | findstr :5000` or `netstat -ano | findstr :3000`
- **Linux/Mac:** `lsof -i :5000` or `lsof -i :3000`

**Kill the process:**
- **Windows:** `taskkill /PID <process_id> /F`
- **Linux/Mac:** `kill -9 <process_id>`

### ngrok Not Found

If ngrok command is not found:
- Make sure ngrok is installed and added to your PATH
- Try using the full path: `C:\path\to\ngrok.exe http 5000` (Windows) or `/path/to/ngrok http 5000` (Linux/Mac)

### Virtual Environment Not Activated

If you get "python: command not found" or module import errors:
- Make sure you activated the virtual environment
- You should see `(venv)` in your terminal prompt

---

## Notes

- Keep all three terminal windows open while working
- The ngrok URL changes each time you restart ngrok (unless you have a paid plan with a static URL)
- If ngrok URL changes, update it in the Bolna AI dashboard
- Flask server must be running before ngrok can tunnel to it
- Frontend can be started in any order relative to the backend

