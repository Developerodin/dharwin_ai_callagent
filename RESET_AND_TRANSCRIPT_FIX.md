# Reset Status & Transcript Storage Fixes

## ✅ Issues Fixed

### 1. Reset Status Not Working

**Problem**: The reset function only reset candidates with status `'calling'` to `'pending'`. It ignored candidates with status `'declined'`, `'confirmed'`, `'rescheduled'`, etc.

**Fix**: Updated `reset_candidate_statuses()` function to reset **ALL** statuses to `'pending'`, not just `'calling'`.

**Before**:
```python
for candidate in data['candidates']:
    if candidate['status'] == 'calling':  # ❌ Only resets 'calling'
        candidate['status'] = 'pending'
```

**After**:
```python
for candidate in data['candidates']:
    old_status = candidate.get('status', 'unknown')
    if old_status != 'pending':
        candidate['status'] = 'pending'  # ✅ Resets ALL statuses
        reset_count += 1
```

### 2. Separate Transcript Storage

**Problem**: Transcripts were only stored in `webhook_data.json` mixed with all other webhook data, making it hard to find and read transcripts for specific candidates.

**Solution**: Created separate transcript storage in `data/transcripts.json` organized by:
- Candidate ID
- Candidate Name
- Position
- Caller ID
- Recipient Phone Number

**New Function**: `save_transcript_separately()`
- Automatically called when webhook data is saved
- Stores transcripts organized by candidate
- Includes all candidate metadata
- Maintains chronological list

## 📁 New File Structure

### `data/transcripts.json`

Structure:
```json
{
  "by_candidate": {
    "1": {
      "candidate_id": 1,
      "candidate_name": "Prakhar Sharma",
      "position": "Software Engineer",
      "phone": "+918755887760",
      "email": "prakhar.sharma@example.com",
      "transcripts": {
        "execution_id_1": {
          "execution_id": "...",
          "candidate_id": 1,
          "candidate_name": "Prakhar Sharma",
          "position": "Software Engineer",
          "candidate_phone": "+918755887760",
          "candidate_email": "prakhar.sharma@example.com",
          "caller_id": "+16282774700",
          "recipient_phone": "+918755887760",
          "transcript": "...",
          "timestamp": "...",
          "status": "completed",
          "call_duration": 46.3
        }
      }
    }
  },
  "all_transcripts": [
    {
      "execution_id": "...",
      "candidate_id": 1,
      "candidate_name": "Prakhar Sharma",
      "position": "Software Engineer",
      "timestamp": "...",
      "caller_id": "+16282774700",
      "recipient_phone": "+918755887760"
    }
  ]
}
```

## 🔧 How It Works

### When a Webhook is Received:

1. **Save webhook data** → `data/webhook_data.json` (unchanged)
2. **Save transcript separately** → `data/transcripts.json` (NEW)
   - Extracts candidate info from `candidates.json`
   - Includes caller ID from telephony data
   - Organizes by candidate ID

### Transcript Storage Includes:

- ✅ Candidate ID
- ✅ Candidate Name
- ✅ Position
- ✅ Candidate Phone
- ✅ Candidate Email
- ✅ Caller ID (agent's phone number)
- ✅ Recipient Phone (candidate's phone)
- ✅ Full Transcript
- ✅ Timestamp
- ✅ Call Status
- ✅ Call Duration

## 📖 Viewing Transcripts

### New Script: `view_transcripts.py`

**View all transcripts:**
```bash
python view_transcripts.py
```

**List all candidates with transcripts:**
```bash
python view_transcripts.py --list
```

**View transcripts for a specific candidate:**
```bash
python view_transcripts.py --candidate=1
```

**View transcript for a specific execution:**
```bash
python view_transcripts.py --execution=2b822c24-991e-485c-b427-695be186d04f
```

## 🧪 Testing

### Test Reset Function:

1. Set a candidate status to `'declined'`:
   ```bash
   # Edit data/candidates.json or use the frontend
   ```

2. Click "Reset All Statuses to Pending" button in the frontend

3. Verify all statuses are reset:
   ```bash
   python -c "import json; data = json.load(open('data/candidates.json')); print([c['status'] for c in data['candidates']])"
   ```
   Should show: `['pending', 'pending', 'pending', ...]`

### Test Transcript Storage:

1. Make a call or wait for a webhook
2. Check transcript storage:
   ```bash
   python view_transcripts.py --list
   ```
3. View specific candidate transcripts:
   ```bash
   python view_transcripts.py --candidate=1
   ```

## 📊 Files Modified

1. **`api_server.py`**:
   - Fixed `reset_candidate_statuses()` function
   - Added `save_transcript_separately()` function
   - Integrated transcript saving in `save_webhook_data()`

2. **`view_transcripts.py`** (NEW):
   - Script to view transcripts organized by candidate
   - Supports filtering by candidate ID or execution ID

## ✅ Benefits

### Reset Function:
- ✅ Resets ALL statuses, not just 'calling'
- ✅ Better logging of what was reset
- ✅ Returns success/failure status

### Separate Transcript Storage:
- ✅ Easy to find transcripts by candidate
- ✅ Includes all candidate metadata
- ✅ Organized structure for easy reading
- ✅ Separate from webhook data (cleaner)
- ✅ Includes caller ID for reference

## 🔄 Next Steps

1. **Test the reset button** in the frontend - it should now work correctly
2. **Make a test call** to verify transcripts are being saved separately
3. **Use `view_transcripts.py`** to browse transcripts by candidate

---

**Both issues are now fixed!** 🎉

