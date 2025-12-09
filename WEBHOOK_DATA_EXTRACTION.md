# Webhook Data Extraction Summary

## What the Webhook Fetches from Bolna AI

When a call ends, Bolna AI sends a webhook POST request to your endpoint with the following data:

### Webhook Payload Structure

```json
{
  "execution_id": "ae6bb4d6-6790-44b6-bf6c-ad9bafa8e4f9",
  "status": "completed",
  "transcript": "Full conversation transcript...",
  "extracted_data": {
    "call_outcome": "ACCEPTED" | "REJECTED" | "RESCHEDULED",
    "original_slot": {
      "date": "2024-12-12",
      "time": "10:00 AM",
      "day_of_week": "Thursday"
    },
    "final_slot": {
      "date": "2024-12-12",
      "time": "10:00 AM",
      "day_of_week": "Thursday"
    } | null,
    "notes": "Additional information"
  },
  "recipient_phone_number": "+918755887760",
  "telephony_data": {
    "duration": 120,
    "call_status": "completed",
    "recording_url": "https://..."
  },
  "cost_breakdown": {
    "total_cost": 0.05
  }
}
```

## Data Processing Flow

### 1. Webhook Receives Data
- **Endpoint:** `/api/webhook`
- **Method:** POST
- **Source:** Bolna AI (from whitelisted IPs)

### 2. Data Extraction
The webhook extracts:
- ✅ `execution_id` - Links to candidate
- ✅ `status` - Call status (completed, failed, etc.)
- ✅ `transcript` - Full conversation text
- ✅ `extracted_data` - **Structured extraction with call_outcome, slots**
- ✅ `recipient_phone_number` - For candidate lookup

### 3. Structured Data Processing
The `extracted_data` field contains:
```json
{
  "call_outcome": "ACCEPTED",
  "original_slot": {
    "date": "2024-12-12",
    "time": "10:00 AM",
    "day_of_week": "Thursday"
  },
  "final_slot": {...} | null,
  "notes": "..."
}
```

This is automatically extracted by the agent during the call.

### 4. Status Mapping
- `call_outcome: "ACCEPTED"` → Candidate status: `confirmed`
- `call_outcome: "REJECTED"` → Candidate status: `declined`
- `call_outcome: "RESCHEDULED"` → Candidate status: `rescheduled` + update interview slot

### 5. Candidate Update
- Status updated in `data/candidates.json`
- Interview slot updated if rescheduled
- Changes are saved immediately

## Where Data is Stored

| Data | Storage Location |
|------|------------------|
| Execution Mappings | `execution_mapping.json` |
| Candidate Status | `data/candidates.json` |
| Webhook Logs | `webhook_logs.json` (if enabled) |
| Full Transcript | Processed but not stored (can be logged) |
| Extracted Data | Available in webhook response |

## Viewing Fetched Data

### Check Webhook Logs
```bash
python view_webhook_logs.py
```

### Check Candidate Updates
```bash
cat data/candidates.json
```

### Check Execution Mappings
```bash
cat execution_mapping.json
```

### Monitor Real-Time
```bash
python monitor_ngrok_requests.py
```

## Example: What Gets Fetched

When a call completes, the webhook receives and processes:

1. **Call Outcome:** ACCEPTED/REJECTED/RESCHEDULED
2. **Original Slot:** Date, time, day of week
3. **Final Slot:** Confirmed slot (or null if rejected)
4. **Transcript:** Full conversation
5. **Telephony Data:** Duration, recording URL
6. **Notes:** Additional context

All this data is used to update the candidate status in real-time!

