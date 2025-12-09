# Migrating Old Webhook Logs - Guide

## ✅ What Was Done

Successfully fetched **7 old webhook requests** from ngrok logs and migrated them to permanent storage!

## 📁 Migration Tools Created

### 1. **fetch_old_webhook_logs.py**
- Checks for old logs in multiple locations:
  - `webhook_logs.json` (temporary storage)
  - ngrok request logs (via ngrok API)
- Automatically migrates found logs to permanent storage

### 2. **migrate_webhook_logs.py**
- Specifically migrates logs from `webhook_logs.json`
- Preserves all data structure
- Handles duplicates intelligently

## 🔍 How to Use

### Fetch and Migrate All Old Logs
```bash
python fetch_old_webhook_logs.py
```

This script will:
1. Check for `webhook_logs.json` (temporary storage)
2. Check ngrok request logs (via ngrok API at http://localhost:4040)
3. Ask if you want to migrate found logs
4. Save everything to `data/webhook_data.json`

### Migrate Only from Temporary Storage
```bash
python migrate_webhook_logs.py
```

This script migrates only from `webhook_logs.json` file.

## 📊 What Gets Migrated

All webhook data including:
- ✅ Complete payload
- ✅ Extracted data (call_outcome, original_slot, final_slot, notes)
- ✅ Transcripts
- ✅ Status information
- ✅ Telephony data
- ✅ Metadata (execution_id, candidate_id, timestamps)

## 📍 Storage Location

Migrated data is stored in:
```
data/webhook_data.json
```

## 🔍 View Migrated Data

```bash
# View all migrated entries
python view_webhook_data.py

# View specific execution
python view_webhook_data.py --execution-id exec_12345

# View with full payload
python view_webhook_data.py --full
```

## ✨ Features

- **Automatic Detection** - Finds logs in multiple locations
- **Smart Migration** - Avoids duplicates
- **Preserves Data** - All information maintained
- **Organized Storage** - Indexed by execution_id
- **Chronological Index** - Easy timeline viewing

## 📝 Migration Results

✅ **7 webhook requests** migrated from ngrok logs
✅ All data preserved in permanent storage
✅ Ready to view with `view_webhook_data.py`

## 💡 Next Steps

1. View the migrated data:
   ```bash
   python view_webhook_data.py
   ```

2. If you have more old logs, run migration again:
   ```bash
   python fetch_old_webhook_logs.py
   ```

3. All future webhooks will automatically be stored permanently!

