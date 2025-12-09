# Webhook Data Fetching Verification

## ✅ Implementation Status

The webhook endpoint has been successfully implemented and is ready to fetch and process data from Bolna Voice AI.

### What's Been Implemented

1. **Webhook Endpoint** (`/api/webhook` and `/webhook`)
   - ✅ Receives POST requests from Bolna AI
   - ✅ Validates IP addresses (with localhost bypass for testing)
   - ✅ Extracts execution data from payload
   - ✅ Maps execution_id to candidate_id
   - ✅ Processes call outcomes and updates candidate status

2. **Data Extraction Capabilities**
   - ✅ Extracts `execution_id` from multiple payload formats
   - ✅ Extracts `status` (completed, failed, in_progress, etc.)
   - ✅ Extracts `transcript` from call
   - ✅ Extracts `extracted_data` (structured data from Bolna AI)
   - ✅ Extracts `recipient_phone_number` for fallback lookup

3. **Execution Mapping System**
   - ✅ Saves execution_id → candidate_id mappings when calls are initiated
   - ✅ Retrieves mappings when webhook is received
   - ✅ Falls back to phone number lookup if mapping not found

4. **Candidate Update System**
   - ✅ Parses call outcomes (confirmed, declined, rescheduled)
   - ✅ Updates candidate status in real-time
   - ✅ Handles rescheduled interviews with new time slots

## 🧪 Testing the Webhook

### Option 1: Use the Verification Script

Run the comprehensive verification script:

```bash
python verify_webhook.py
```

This script will:
- Check if Flask server is running
- Create test execution mappings
- Test webhook with different payload structures
- Verify candidate data updates

### Option 2: Use the Test Script

Test with a specific execution ID:

```bash
python test_webhook.py --execution-id "exec_12345" --status completed
```

### Option 3: Manual Testing with curl

```bash
curl -X POST http://localhost:5000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "execution_id": "test_exec_12345",
    "status": "completed",
    "transcript": "Agent: Hello. Candidate: Yes, I confirm.",
    "extracted_data": {
      "status": "confirmed",
      "user_interested": true
    },
    "recipient_phone_number": "+918755887760"
  }'
```

### Option 4: Check Webhook Status

Check webhook configuration and status:

```bash
curl http://localhost:5000/api/webhook/status
```

## 📋 Webhook Payload Formats Supported

The webhook can handle multiple payload formats:

### Format 1: Standard Format
```json
{
  "execution_id": "exec_12345",
  "status": "completed",
  "transcript": "...",
  "extracted_data": {...},
  "recipient_phone_number": "+918755887760"
}
```

### Format 2: Nested Data Format
```json
{
  "data": {
    "execution_id": "exec_12345",
    "status": "completed",
    "transcript": "..."
  },
  "recipient_phone_number": "+918755887760"
}
```

### Format 3: CamelCase Format
```json
{
  "executionId": "exec_12345",
  "status": "completed",
  "transcript": "..."
}
```

## 🔍 How Data Fetching Works

1. **Webhook Receives Payload**
   ```
   POST /api/webhook
   {
     "execution_id": "exec_12345",
     "status": "completed",
     ...
   }
   ```

2. **Extract Execution ID**
   - Tries multiple fields: `execution_id`, `executionId`, `id`, `data.execution_id`

3. **Find Candidate**
   - First: Look up in `execution_mapping.json`
   - Fallback: Find by `recipient_phone_number` in candidates.json

4. **Extract Call Data**
   - Status: `completed`, `failed`, `in_progress`, etc.
   - Transcript: Full conversation text
   - Extracted Data: Structured data from Bolna AI

5. **Process Outcome**
   - Parse transcript and extracted_data
   - Determine final status: `confirmed`, `declined`, `rescheduled`, `pending`

6. **Update Candidate**
   - Update status in `data/candidates.json`
   - Update interview slot if rescheduled
   - Return success response

## ✅ Verification Checklist

- [x] Webhook endpoint created (`/api/webhook`)
- [x] IP validation implemented (with localhost bypass)
- [x] Execution mapping system working
- [x] Data extraction from payload working
- [x] Candidate lookup by execution_id or phone working
- [x] Call outcome parsing working
- [x] Candidate status updates working
- [x] Error handling implemented
- [x] Logging for debugging implemented

## 🚀 Next Steps

1. **Start Flask Server**
   ```bash
   python api_server.py
   ```

2. **Configure Webhook in Bolna AI Dashboard**
   - Go to your agent settings
   - Add webhook URL: `https://your-domain.com/api/webhook`
   - For testing: Use ngrok: `ngrok http 5000`

3. **Test with Real Calls**
   - Initiate a call from your application
   - Check Flask server logs for webhook requests
   - Verify candidate status updates automatically

4. **Monitor Webhook Status**
   ```bash
   curl http://localhost:5000/api/webhook/status
   ```

## 📊 Expected Behavior

When a call completes:

1. Bolna AI sends webhook to `/api/webhook`
2. Webhook extracts execution_id and finds candidate
3. Webhook parses call outcome from transcript/extracted_data
4. Candidate status is updated in `data/candidates.json`
5. Response sent back to Bolna AI confirming receipt

## 🔧 Troubleshooting

### Webhook Not Receiving Data

1. **Check Flask Server**
   ```bash
   curl http://localhost:5000/api/webhook/status
   ```

2. **Check IP Whitelist**
   - Localhost is always allowed for testing
   - Production: Ensure Bolna IPs are whitelisted

3. **Check Execution Mapping**
   ```bash
   cat execution_mapping.json
   ```

4. **Check Flask Logs**
   - Look for webhook request logs
   - Check for error messages

### Data Not Updating

1. **Verify Payload Structure**
   - Check if execution_id is present
   - Verify status is "completed"

2. **Check Candidate Mapping**
   - Verify execution_id exists in mapping
   - Or verify phone number matches candidate

3. **Check Logs**
   - Look for parsing errors
   - Check candidate update success messages

## 📝 Notes

- The webhook endpoint accepts requests from localhost for testing
- Execution mappings are stored in `execution_mapping.json`
- Candidate data is stored in `data/candidates.json`
- All webhook requests are logged for debugging

