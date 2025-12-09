# Webhook Configuration Guide for Bolna Dashboard

## 🎯 Quick Setup Checklist

- [ ] Flask server running (`python api_server.py`)
- [ ] ngrok tunnel active (`ngrok http 5000`)
- [ ] Webhook URL copied
- [ ] Configured in Bolna Dashboard
- [ ] Test call made
- [ ] Webhook data received

## 📋 Step-by-Step Instructions

### Step 1: Verify Local Setup

Run the verification script:

```bash
python verify_webhook_config.py
```

This will check:
- ✅ Flask server status
- ✅ ngrok tunnel status
- ✅ Webhook URL availability
- ✅ Endpoint accessibility

### Step 2: Get Your Webhook URL

Your webhook URL should be:

```
https://inspiratory-cristie-cherishingly.ngrok-free.dev/api/webhook
```

**Note:** If ngrok restarts, you'll get a new URL. Check with:

```bash
python verify_webhook_config.py
```

### Step 3: Configure in Bolna Dashboard

1. **Go to Bolna Platform**
   - URL: https://platform.bolna.ai/
   - Log in with your account

2. **Navigate to Agent Settings**
   - Find your agent (Agent ID: `aeb6eee0-20f2-4b23-b6ad-fe57bb0adf34`)
   - Click on agent to open settings

3. **Find Webhook Section**
   Look for one of these sections:
   - **"Webhook Configuration"**
   - **"Webhook Settings"**
   - **"Real-time Data Push"**
   - **"Execution Webhook"**
   - **"Push all execution data to webhook"**
   - **"Webhook URL"**

4. **Enter Webhook URL**
   - Paste: `https://inspiratory-cristie-cherishingly.ngrok-free.dev/api/webhook`
   - Make sure there are no trailing spaces

5. **Save Configuration**
   - Click "Save" or "Update"
   - Confirm the webhook is enabled/active

### Step 4: Verify Configuration

After saving, you should see:
- ✅ Webhook URL displayed in dashboard
- ✅ Status showing "Active" or "Enabled"
- ✅ Test button (if available) to send test webhook

### Step 5: Test the Webhook

1. **Make a Test Call**
   ```bash
   # Use your application or API to make a call
   curl -X POST http://localhost:5000/api/call \
     -H "Content-Type: application/json" \
     -d '{"candidateId": 1, "phone": "+918755887760", "name": "Test"}'
   ```

2. **Monitor Flask Logs**
   Watch for webhook POST requests:
   ```
   📥 Received webhook payload
   📋 Payload keys: [...]
   ```

3. **Check Stored Data**
   ```bash
   python view_webhook_data.py
   ```

## 🔍 Troubleshooting

### Webhook Not Receiving Data

1. **Check Flask Server**
   ```bash
   # Verify server is running
   python verify_webhook_config.py
   ```

2. **Check ngrok Tunnel**
   - Visit: http://localhost:4040
   - Verify tunnel is active
   - Check for incoming requests

3. **Verify Webhook URL**
   - Must be accessible from internet
   - Must use HTTPS (ngrok provides this)
   - Must end with `/api/webhook`

4. **Check IP Whitelist**
   - Bolna sends from specific IPs
   - Our webhook handler validates these
   - ngrok automatically handles this

5. **Check Bolna Dashboard**
   - Webhook URL is saved correctly
   - Webhook is enabled/active
   - No error messages displayed

### Common Issues

**Issue: "Webhook URL not accessible"**
- Solution: Ensure ngrok is running and tunnel is active

**Issue: "404 Not Found"**
- Solution: Check webhook URL ends with `/api/webhook`

**Issue: "No webhook data received"**
- Solution: 
  - Verify webhook URL in Bolna Dashboard
  - Make a test call
  - Check Flask logs for errors

**Issue: "ngrok URL changed"**
- Solution: 
  - Update webhook URL in Bolna Dashboard
  - Or use ngrok reserved domain (paid plan)

## 📊 Verification Commands

```bash
# Check webhook configuration
python verify_webhook_config.py

# View webhook status
curl http://localhost:5000/api/webhook/status

# Monitor ngrok requests
python monitor_ngrok_requests.py

# View stored webhook data
python view_webhook_data.py
```

## 🔗 Useful Links

- **Bolna Platform**: https://platform.bolna.ai/
- **Bolna Documentation**: https://www.bolna.ai/docs/
- **ngrok Dashboard**: http://localhost:4040
- **Webhook URL File**: `WEBHOOK_URL.txt`

## 📝 Webhook URL Format

Your webhook URL should match this format:

```
https://[ngrok-subdomain].ngrok-free.dev/api/webhook
```

**Current URL:**
```
https://inspiratory-cristie-cherishingly.ngrok-free.dev/api/webhook
```

## ✅ Success Indicators

You'll know the webhook is working when:

1. ✅ Flask logs show webhook POST requests
2. ✅ `data/webhook_data.json` contains entries with:
   - Non-empty `transcript`
   - `extracted_data` with `call_outcome`
   - Valid `status` (not "unknown")
   - `recipient_phone_number` populated
3. ✅ Candidate status updates automatically
4. ✅ ngrok dashboard shows POST requests to `/api/webhook`

## 🚀 Next Steps

Once webhook is configured:

1. Make a test call
2. Monitor Flask server logs
3. Verify data is saved
4. Check candidate status updates
5. View stored data with `python view_webhook_data.py`

---

**Need Help?** Run `python verify_webhook_config.py` to check your setup!

