# Where Extracted Data is Stored

## 📍 Current Storage Locations

### 1. **Permanent Storage: `data/webhook_data.json`** ⭐ NEW
**Location:** `data/webhook_data.json` (beside `candidates.json`)  
**Purpose:** Stores **ALL webhook data permanently** - complete payloads, extracted_data, transcripts, telephony data

**Structure:**
```json
{
  "execution_id_1": {
    "execution_id": "exec_12345",
    "candidate_id": 1,
    "timestamp": "2024-12-09T15:04:30.123456",
    "received_at": "2024-12-09 15:04:30",
    "payload": {
      // Complete original webhook payload
    },
    "extracted_data": {
      "call_outcome": "ACCEPTED",
      "original_slot": {...},
      "final_slot": {...},
      "notes": "..."
    },
    "transcript": "Full conversation transcript...",
    "status": "completed",
    "recipient_phone_number": "+918755887760",
    "telephony_data": {
      "duration": 120,
      "recording_url": "https://..."
    }
  },
  "all_webhooks": [
    {
      "execution_id": "exec_12345",
      "candidate_id": 1,
      "timestamp": "2024-12-09T15:04:30.123456",
      "status": "completed"
    }
  ]
}
```

**Details:**
- ✅ **Permanent storage** - all data stored forever (no limits)
- ✅ Contains **complete webhook payload**
- ✅ Contains **structured extraction data** (call_outcome, original_slot, final_slot, notes)
- ✅ Contains **full transcript**
- ✅ Contains **telephony data** (duration, recording_url)
- ✅ Organized by `execution_id` for easy lookup
- ✅ Includes chronological index in `all_webhooks` array

**When it's created:**
- Automatically created when webhook receives data
- Updated on every webhook POST request
- Stored in `data/` folder beside `candidates.json`

---

### 2. **Temporary Storage: `webhook_logs.json`** (Legacy)
**Location:** Root directory  
**Purpose:** Legacy storage - kept for backward compatibility

**Structure:**
```json
[
  {
    "timestamp": "2024-12-09T15:04:30.123456",
    "payload": {
      "execution_id": "exec_12345",
      "status": "completed",
      "extracted_data": {
        "call_outcome": "ACCEPTED",
        "original_slot": {
          "date": "2024-12-12",
          "time": "10:00 AM",
          "day_of_week": "Thursday"
        },
        "final_slot": {
          "date": "2024-12-12",
          "time": "10:00 AM",
          "day_of_week": "Thursday"
        },
        "notes": "Candidate confirmed without hesitation"
      },
      "transcript": "...",
      "recipient_phone_number": "+918755887760"
    }
  }
]
```

**Details:**
- ✅ Contains **full structured extraction data** (call_outcome, original_slot, final_slot, notes)
- ✅ Includes complete webhook payload
- ⚠️ Only keeps **last 50 logs** (automatically pruned)
- ⚠️ **Temporary storage** - older logs are deleted

**When it's created:**
- Automatically created when webhook receives data
- Updated on every webhook POST request

---

### 3. **Processed Storage: `data/candidates.json`**
**Location:** `data/candidates.json`  
**Purpose:** Stores processed candidate data and status updates

**What's stored:**
```json
{
  "candidates": [
    {
      "id": 1,
      "name": "Prakhar Sharma",
      "status": "confirmed",  // ← Processed from extracted_data.call_outcome
      "scheduledInterview": {  // ← Processed from extracted_data.final_slot
        "day": "Thursday",
        "date": "2024-12-12",
        "time": "10:00 AM",
        "datetime": "Thursday, 2024-12-12 at 10:00 AM"
      }
    }
  ]
}
```

**What's NOT stored:**
- ❌ Raw `extracted_data` structure
- ❌ `call_outcome` field (only the processed `status`)
- ❌ `original_slot` (only `final_slot` is stored as `scheduledInterview`)
- ❌ `notes` field
- ❌ Full transcript

**Mapping:**
- `extracted_data.call_outcome = "ACCEPTED"` → `status = "confirmed"`
- `extracted_data.call_outcome = "REJECTED"` → `status = "declined"`
- `extracted_data.call_outcome = "RESCHEDULED"` → `status = "rescheduled"`
- `extracted_data.final_slot` → `scheduledInterview` (converted format)

---

## 📊 Data Flow

```
Webhook Receives Data
         ↓
webhook_logs.json (temporary)
  - Full payload with extracted_data
  - Last 50 logs only
         ↓
Processing
  - Parse extracted_data
  - Convert to candidate format
         ↓
data/candidates.json (permanent)
  - Status updated
  - Interview schedule updated
  - Raw extracted_data NOT stored
```

---

## 🔍 How to View Extracted Data

### View from Permanent Storage (Recommended)
```bash
# View recent webhook data
python view_webhook_data.py

# View specific execution
python view_webhook_data.py --execution-id exec_12345

# View with full payload
python view_webhook_data.py --full

# View last 20 entries
python view_webhook_data.py --limit 20
```

### View Specific Execution Data
```bash
python -c "import json; data = json.load(open('data/webhook_data.json')); print(json.dumps(data.get('exec_12345', {}), indent=2))"
```

### View All Extracted Data
```bash
python -c "import json; data = json.load(open('data/webhook_data.json')); [print(f\"{k}: {v.get('extracted_data', {})}\") for k, v in data.items() if k != 'all_webhooks']"
```

### View from Legacy Logs (if needed)
```bash
python view_extracted_data.py
```

---

## ⚠️ Important Notes

1. ✅ **ALL webhook data is NOW permanently stored** in `data/webhook_data.json`
2. ✅ **No data limits** - all webhook payloads are stored forever
3. ✅ **Complete data** - includes payload, extracted_data, transcript, telephony data
4. **Processed results** are also stored in `candidates.json` for quick access
5. Legacy `webhook_logs.json` still exists but is no longer the primary storage

---

## 💡 Options to Store Extracted Data Permanently

If you want to store extracted_data permanently, you can:

### Option 1: Add to candidates.json
Modify `update_candidate_in_json()` to store:
```python
candidate['extracted_data'] = extracted_data
candidate['call_notes'] = extracted_data.get('notes')
```

### Option 2: Create separate file
Create `data/extracted_data.json`:
```python
{
  "exec_12345": {
    "timestamp": "2024-12-09T15:04:30",
    "candidate_id": 1,
    "extracted_data": {
      "call_outcome": "ACCEPTED",
      ...
    }
  }
}
```

### Option 3: Database storage
Store in SQLite/PostgreSQL for better querying and retention.

---

## 📁 File Locations Summary

| Data Type | File | Permanent? | Contains extracted_data? | Contains all webhook data? |
|-----------|------|------------|-------------------------|----------------------------|
| **Webhook Data** | `data/webhook_data.json` | ✅ **Yes** | ✅ **Yes (full structure)** | ✅ **Yes (complete payload)** |
| Candidate Data | `data/candidates.json` | ✅ Yes | ❌ No (only processed) | ❌ No |
| Execution Mappings | `execution_mapping.json` | ✅ Yes | ❌ No | ❌ No |
| Webhook Logs (Legacy) | `webhook_logs.json` | ❌ No (last 50 only) | ✅ Yes | ✅ Yes |

