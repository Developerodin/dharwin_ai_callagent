# Current Webhook Data Status

## 📊 Current State of `data/webhook_data.json`

### What's Currently Stored

The file currently contains **7 entries** from ngrok request logs, but these are **NOT actual Bolna webhook payloads**. They are:

- ❌ HTTP request logs from ngrok (404s, health checks)
- ❌ No transcripts
- ❌ No extracted_data
- ❌ No execution details
- ❌ No call recordings
- ✅ Just metadata (method, path, IP addresses)

### Sample Current Entry

```json
{
  "execution_id": "ngrok_airt_36bQcbicUkee1iLhBHWjWRXdO5J",
  "payload": {
    "_ngrok_metadata": {
      "method": "POST",
      "path": "/",
      "remote_addr": "13.200.45.61"
    }
  },
  "transcript": "",
  "extracted_data": {},
  "status": "unknown"
}
```

**This is just a request log, not a webhook payload!**

---

## ✅ What Will Be Stored (When Real Webhooks Arrive)

When actual webhook POST requests arrive from Bolna AI, the data will include:

### Complete Webhook Payload

```json
{
  "execution_id": "3dddf7ed-5ef4-4dbb-8e27-aace39fc1e61",
  "status": "completed",
  "transcript": "Agent: Hello, this is Ava...",
  "extracted_data": {
    "call_outcome": "ACCEPTED",
    "original_slot": {...},
    "final_slot": {...},
    "notes": "..."
  },
  "telephony_data": {
    "duration": 120,
    "recording_url": "https://..."
  },
  "recipient_phone_number": "+918755887760"
}
```

### What Will Be Saved

- ✅ **Complete Payload** - Full webhook POST body
- ✅ **Transcript** - Full conversation text
- ✅ **Extracted Data** - Structured extraction (call_outcome, slots, notes)
- ✅ **Recording URL** - Link to call recording
- ✅ **Execution Details** - Status, timestamps, metadata
- ✅ **Telephony Data** - Duration, call status
- ✅ **Raw Data** - Complete API response

---

## 🔄 How Data Gets Stored

### 1. Real-Time Webhooks (Automatic)

When Bolna AI sends webhooks to your endpoint:

```
Bolna AI → POST /api/webhook → api_server.py → save_webhook_data() → data/webhook_data.json
```

**This happens automatically!** No manual steps needed.

### 2. Historical Data Fetching (Manual)

To fetch old calls from Bolna API:

```bash
# Fetch all historical calls
python fetch_historical_calls.py

# Fetch specific execution
python fetch_historical_calls.py --execution-id exec_12345

# Fetch limited number (testing)
python fetch_historical_calls.py --limit 10
```

**Note:** Historical data fetching may return 404s if:
- Executions have expired
- Data retention period has passed
- Execution IDs are invalid

---

## 📋 Your Execution IDs

From `execution_mapping.json`, you have:

1. `8d883419-9e4d-4bcf-ad9d-8e8031fca92f` (Dec 8)
2. `05af6448-06e7-4ebb-a0fb-d5e108aea8bd` (Dec 9)
3. `ae6bb4d6-6790-44b6-bf6c-ad9bafa8e4f9` (Dec 9)
4. `3dddf7ed-5ef4-4dbb-8e27-aace39fc1e61` (Dec 9)

**Try fetching these:**
```bash
python fetch_historical_calls.py --execution-id 8d883419-9e4d-4bcf-ad9d-8e8031fca92f
```

---

## 🔍 How to Check for Real Data

### View Current Data

```bash
python view_webhook_data.py
```

### Check for Transcripts

Real webhook data will have:
- ✅ Non-empty `transcript` field
- ✅ `extracted_data` with `call_outcome`
- ✅ Valid `status` (not "unknown")
- ✅ `recipient_phone_number` populated

### Check Execution IDs

Real data will have execution IDs like:
- ✅ `3dddf7ed-5ef4-4dbb-8e27-aace39fc1e61` (UUID format)
- ❌ `ngrok_airt_...` (ngrok request IDs)

---

## 🎯 Next Steps

1. **Wait for Real Webhooks**: When new calls complete, webhooks will automatically be saved

2. **Check Webhook Configuration**: Ensure webhook URL is configured in Bolna Dashboard:
   - URL: `https://inspiratory-cristie-cherishingly.ngrok-free.dev/api/webhook`

3. **Fetch Historical Data**: Try fetching data for your execution IDs:
   ```bash
   python fetch_historical_calls.py --execution-id 8d883419-9e4d-4bcf-ad9d-8e8031fca92f
   ```

4. **Monitor Webhook Logs**: Check Flask server logs when calls complete

---

## 💡 Summary

- **Current state**: Only ngrok request logs (not real webhooks)
- **When webhooks arrive**: They'll be automatically saved with complete data
- **Scripts ready**: `fetch_historical_calls.py` ready to fetch from API
- **Storage ready**: `data/webhook_data.json` configured to store everything

The system is **ready and waiting** for real webhook data! 🚀

