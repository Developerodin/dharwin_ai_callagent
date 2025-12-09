# Data Storage Locations

This document explains where all the fetched webhook data is being stored.

## 📁 Storage Locations

### 1. **Execution Mappings** 
**File:** `execution_mapping.json` (root directory)

**What's stored:**
- Mapping between `execution_id` (from Bolna AI) and `candidate_id`
- Phone number associated with each execution
- Timestamp when the mapping was created

**Example:**
```json
{
  "exec_1234567890": {
    "candidate_id": 1,
    "phone": "+918755887760",
    "created_at": "2024-12-01 10:30:00"
  }
}
```

**When it's created:**
- Automatically created when a call is initiated via `/api/call`
- Stored before the call is made to Bolna AI

**Purpose:**
- Used by webhook to identify which candidate to update when execution data arrives

---

### 2. **Candidate Data Updates**
**File:** `data/candidates.json`

**What's stored:**
- All candidate information (name, phone, email, position)
- **Candidate status** (updated by webhook):
  - `pending` - Initial/default status
  - `calling` - Call in progress
  - `confirmed` - Candidate confirmed interview
  - `declined` - Candidate declined interview
  - `rescheduled` - Candidate requested new time slot
- **Interview schedule** (updated if rescheduled):
  - `scheduledInterview.date`
  - `scheduledInterview.time`
  - `scheduledInterview.day`
  - `scheduledInterview.datetime`

**Example:**
```json
{
  "candidates": [
    {
      "id": 1,
      "name": "Prakhar Sharma",
      "phone": "+918755887760",
      "email": "prakhar.sharma@example.com",
      "position": "Software Engineer",
      "status": "confirmed",  // ← Updated by webhook
      "scheduledInterview": {
        "date": "Friday, the 12th of December",
        "time": "10:00 A.M.",
        "day": "Friday",
        "datetime": "Friday, the 12th of December at 10:00 A.M."
      },
      "applicationDate": "2024-11-25"
    }
  ]
}
```

**When it's updated:**
- When webhook receives completed call data from Bolna AI
- Status is updated based on call outcome (confirmed/declined/rescheduled)
- Interview schedule is updated if candidate rescheduled

---

## 🔄 Data Flow

### Step 1: Call Initiation
```
POST /api/call
  ↓
execution_mapping.json created
  {
    "exec_123": {
      "candidate_id": 1,
      "phone": "+918755887760"
    }
  }
```

### Step 2: Webhook Receives Data
```
POST /api/webhook (from Bolna AI)
  ↓
Payload received:
  {
    "execution_id": "exec_123",
    "status": "completed",
    "transcript": "...",
    "extracted_data": {...}
  }
```

### Step 3: Data Processing
```
1. Look up execution_id in execution_mapping.json
   → Finds candidate_id: 1

2. Parse call outcome from transcript/extracted_data
   → Determines status: "confirmed"

3. Update data/candidates.json
   → Updates candidate[0].status = "confirmed"
```

### Step 4: Storage Updated
```
data/candidates.json updated:
  {
    "candidates": [{
      "id": 1,
      "status": "confirmed"  ← Updated!
    }]
  }
```

---

## 📊 What Data is NOT Stored

The following data from webhook payloads is **processed but not permanently stored**:

- **Full transcript** - Used for parsing but not saved to file
- **Raw webhook payload** - Processed and discarded
- **Telephony data** (duration, recording_url) - Not stored
- **Cost breakdown** - Not stored
- **Execution logs** - Not stored

**Note:** If you want to store transcripts or other data, you would need to add additional storage logic.

---

## 🔍 How to View Stored Data

### View Execution Mappings
```bash
cat execution_mapping.json
# or
python -c "import json; print(json.dumps(json.load(open('execution_mapping.json')), indent=2))"
```

### View Candidate Data
```bash
cat data/candidates.json
# or
python -c "import json; print(json.dumps(json.load(open('data/candidates.json')), indent=2))"
```

### View Specific Candidate Status
```bash
python -c "import json; data = json.load(open('data/candidates.json')); print([c['status'] for c in data['candidates']])"
```

---

## 💾 File Locations Summary

| Data Type | File Location | Purpose |
|-----------|--------------|---------|
| Execution Mappings | `execution_mapping.json` | Maps execution_id → candidate_id |
| Candidate Data | `data/candidates.json` | All candidate info + status updates |
| Available Slots | `data/candidates.json` | Interview time slots |

---

## 🔧 Modifying Storage

If you want to store additional data (like transcripts), you can:

1. **Add to candidates.json:**
   ```python
   candidate['call_transcript'] = transcript
   candidate['call_duration'] = telephony_data.get('duration')
   ```

2. **Create separate storage file:**
   ```python
   # Store in data/call_logs.json
   call_logs[execution_id] = {
       'transcript': transcript,
       'status': status,
       'timestamp': datetime.now()
   }
   ```

3. **Use a database:**
   - Replace JSON files with SQLite/PostgreSQL
   - Store transcripts, logs, and detailed call data

---

## 📝 Notes

- All data is stored in **JSON format** for easy reading and editing
- Files are updated **in-place** (overwritten, not appended)
- No data is stored in memory permanently - everything is file-based
- Execution mappings persist across server restarts
- Candidate updates are immediately reflected in the JSON file

