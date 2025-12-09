# Webhook Data Storage - Complete Implementation

## ✅ What Was Implemented

All webhook data is now **permanently stored** in `data/webhook_data.json` (beside `candidates.json`).

## 📁 Storage Location

**File:** `data/webhook_data.json`

## 📦 What Gets Stored

Every webhook POST request stores:

1. **Complete Payload** - Full original webhook payload from Bolna AI
2. **Extracted Data** - Structured extraction (`call_outcome`, `original_slot`, `final_slot`, `notes`)
3. **Transcript** - Full conversation transcript
4. **Status** - Call status (completed, failed, in_progress, etc.)
5. **Telephony Data** - Duration, recording URLs, etc.
6. **Metadata** - Execution ID, Candidate ID, timestamps
7. **Phone Number** - Recipient phone number

## 🔄 How It Works

1. Webhook receives POST request from Bolna AI
2. System extracts `execution_id` and finds `candidate_id`
3. **ALL payload data** is saved to `data/webhook_data.json`
4. Data is organized by `execution_id` for easy lookup
5. Chronological index maintained in `all_webhooks` array

## 📊 Data Structure

```json
{
  "execution_id_1": {
    "execution_id": "...",
    "candidate_id": 1,
    "timestamp": "2024-12-09T15:04:30.123456",
    "received_at": "2024-12-09 15:04:30",
    "payload": { /* Complete original payload */ },
    "extracted_data": {
      "call_outcome": "ACCEPTED",
      "original_slot": {...},
      "final_slot": {...},
      "notes": "..."
    },
    "transcript": "...",
    "status": "completed",
    "recipient_phone_number": "+918755887760",
    "telephony_data": {...}
  },
  "all_webhooks": [...]
}
```

## 🔍 How to View Stored Data

### View Recent Entries
```bash
python view_webhook_data.py
```

### View Specific Execution
```bash
python view_webhook_data.py --execution-id exec_12345
```

### View with Full Payload
```bash
python view_webhook_data.py --full
```

### View Last 20 Entries
```bash
python view_webhook_data.py --limit 20
```

## ✨ Features

- ✅ **Permanent Storage** - All data stored forever (no limits)
- ✅ **Complete Data** - Every webhook payload stored in full
- ✅ **Organized** - Indexed by execution_id for fast lookup
- ✅ **Chronological Index** - `all_webhooks` array for timeline view
- ✅ **Extracted Data** - Structured extraction data preserved
- ✅ **Transcripts** - Full conversation transcripts stored
- ✅ **Telephony Data** - Call duration, recordings, etc.

## 📝 Files Modified

1. **api_server.py**
   - Added `save_webhook_data()` function
   - Integrated into webhook handler
   - Saves data immediately after receiving webhook

2. **view_webhook_data.py** (New)
   - Script to view stored webhook data
   - Supports filtering and full payload viewing

3. **EXTRACTED_DATA_STORAGE.md** (Updated)
   - Documentation updated with new storage location

## 🚀 Ready to Use

The system is now ready! When webhooks are received:

1. Data is automatically saved to `data/webhook_data.json`
2. You can view it anytime using `view_webhook_data.py`
3. All extracted_data is permanently preserved
4. Complete webhook history is maintained

## 📍 Location

All webhook data is stored in:
```
data/
  ├── candidates.json          (processed candidate data)
  └── webhook_data.json        (ALL webhook data) ⭐ NEW
```

