# ngrok Webhook Setup Guide

This guide will help you expose your local Flask webhook endpoint using ngrok so Bolna AI can send call execution data to it.

## Quick Start

1. **Start Flask Server**
   ```bash
   python api_server.py
   ```
   Keep this terminal running!

2. **Start ngrok Tunnel** (in a NEW terminal)
   ```bash
   ngrok http 5000
   ```
   This will show you a public URL like: `https://abc123.ngrok-free.app`

3. **Get Your Webhook URL**
   ```
   https://YOUR-NGROK-ID.ngrok-free.app/api/webhook
   ```

4. **Configure in Bolna AI Dashboard**
   - Go to: https://platform.bolna.ai/
   - Navigate to your agent settings
   - Find "Webhook URL" or "Push all execution data to webhook"
   - Paste your ngrok webhook URL
   - Save

## Detailed Steps

### Step 1: Install ngrok

**Windows:**
- Download from: https://ngrok.com/download
- Or use Chocolatey: `choco install ngrok`
- Or use Scoop: `scoop install ngrok`

**Mac:**
```bash
brew install ngrok
```

**Linux:**
```bash
# Download and extract
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

**Sign up for free account:**
1. Go to https://dashboard.ngrok.com/signup
2. Get your authtoken from the dashboard
3. Run: `ngrok config add-authtoken YOUR_AUTHTOKEN`

### Step 2: Start Flask Server

In your project directory:

```bash
python api_server.py
```

You should see:
```
🚀 Starting Flask API server...
📡 Server will run on http://localhost:5000
```

**Keep this terminal window open!**

### Step 3: Start ngrok Tunnel

Open a **NEW terminal window** (keep Flask running) and run:

```bash
ngrok http 5000
```

You'll see output like:
```
Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:5000
```

**Copy the HTTPS URL** (the one starting with `https://`)

### Step 4: Get Your Webhook URL

Your webhook endpoint will be:
```
https://YOUR-NGROK-ID.ngrok-free.app/api/webhook
```

For example:
```
https://abc123.ngrok-free.app/api/webhook
```

### Step 5: Configure in Bolna AI Dashboard

1. **Login to Bolna AI**
   - Go to: https://platform.bolna.ai/
   - Login to your account

2. **Navigate to Agent Settings**
   - Go to your agent configuration
   - Find "Webhook" section or "Push all execution data to webhook"

3. **Add Webhook URL**
   - Paste your ngrok webhook URL: `https://YOUR-NGROK-ID.ngrok-free.app/api/webhook`
   - Save the configuration

4. **Verify**
   - The webhook is now active
   - Bolna AI will send all execution data to this URL

### Step 6: Test Your Webhook

You can test your webhook manually:

```bash
curl -X POST https://YOUR-NGROK-ID.ngrok-free.app/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "execution_id": "test_123",
    "status": "completed",
    "transcript": "Test transcript",
    "recipient_phone_number": "+918755887760"
  }'
```

Or use the helper script:

```bash
python setup_ngrok_webhook.py
```

## Using the Helper Script

Run the helper script to check your setup:

```bash
python setup_ngrok_webhook.py
```

This script will:
- ✅ Check if Flask server is running
- ✅ Check if ngrok is installed
- ✅ Get your ngrok public URL
- ✅ Show your webhook URL
- ✅ Provide configuration instructions

## Troubleshooting

### ngrok not found

**Error:** `'ngrok' is not recognized`

**Solution:**
1. Install ngrok (see Step 1 above)
2. Make sure ngrok is in your PATH
3. Restart your terminal

### Flask server not running

**Error:** Connection refused to localhost:5000

**Solution:**
```bash
python api_server.py
```
Make sure Flask is running on port 5000.

### ngrok tunnel not connecting

**Check:**
1. Is Flask server running? Test: `curl http://localhost:5000/api/webhook/status`
2. Is ngrok running? Check: `http://localhost:4040` (ngrok web interface)
3. Is port 5000 available? Make sure nothing else is using it

### Webhook not receiving data

**Check:**
1. Verify webhook URL in Bolna AI dashboard is correct
2. Check Flask logs for incoming requests
3. Test webhook manually with curl
4. Check ngrok logs at `http://localhost:4040`

### IP Whitelist Issue

The webhook validates IP addresses. In development with ngrok:
- Localhost requests are always allowed
- ngrok requests from Bolna AI should work automatically
- If you see IP errors, check `api_server.py` IP validation logic

## Keeping ngrok Running

**Option 1: Run in Background (Windows)**
```powershell
Start-Process ngrok -ArgumentList "http 5000"
```

**Option 2: Use ngrok API for Persistent URLs**

For production, consider:
1. Using ngrok with a custom domain
2. Deploying to a cloud service (Heroku, Railway, Render, etc.)
3. Using ngrok reserved domains (paid feature)

## Production Deployment

For production, you have better options:

1. **Deploy Flask App to Cloud**
   - Heroku, Railway, Render, AWS, etc.
   - Use your deployed URL: `https://your-app.com/api/webhook`

2. **Use ngrok Reserved Domain** (Paid)
   - Get a fixed ngrok URL
   - No need to update webhook URL every time

3. **Use VPN/Internal Network**
   - If Bolna AI supports VPN connections
   - More secure for production

## Important Notes

⚠️ **Free ngrok URLs change every time** you restart ngrok. You'll need to:
- Update webhook URL in Bolna AI dashboard each time
- Or use ngrok reserved domains (paid)

⚠️ **Keep both terminals open:**
- Terminal 1: Flask server (`python api_server.py`)
- Terminal 2: ngrok tunnel (`ngrok http 5000`)

⚠️ **ngrok free tier limitations:**
- URLs expire when you stop ngrok
- Limited connections per month
- For production, consider deploying to cloud

## Monitoring Webhooks

### View ngrok Requests
Visit: `http://localhost:4040` to see:
- All requests to your webhook
- Request/response details
- Replay requests for testing

### View Flask Logs
Your Flask server will log all webhook requests:
```
📥 Received webhook payload
📋 Payload keys: ['execution_id', 'status', ...]
🔍 Processing webhook for execution_id: exec_123
✅ Candidate 1 updated: confirmed
```

## Next Steps

Once webhook is configured:
1. Make a test call from your application
2. Check Flask logs for webhook data
3. Verify candidate status updates automatically
4. Monitor ngrok dashboard for incoming requests

## Support

If you encounter issues:
1. Check Flask server logs
2. Check ngrok logs at `http://localhost:4040`
3. Test webhook manually with curl
4. Verify webhook URL in Bolna AI dashboard

