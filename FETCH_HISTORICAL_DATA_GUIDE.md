# Fetch Historical Call Data from Bolna API

## 🎯 Overview

This script fetches complete historical call data from Bolna's API including:
- ✅ **Transcripts** - Full conversation transcripts
- ✅ **Call Recordings** - Recording URLs
- ✅ **Call Traces/Logs** - Execution logs and traces
- ✅ **Raw Data** - Complete execution details from API
- ✅ **Extracted Data** - Structured extraction data
- ✅ **Telephony Data** - Call duration, status, metadata

## 📋 Usage

### Fetch All Historical Calls

Fetch all executions from your agent's call history:

```bash
python fetch_historical_calls.py
```

### Fetch Specific Execution

Fetch complete data for a specific execution:

```bash
python fetch_historical_calls.py --execution-id exec_12345
```

### Fetch with Options

```bash
# Fetch from specific agent
python fetch_historical_calls.py --agent-id agent_abc123

# Limit number of pages (each page = 50 executions)
python fetch_historical_calls.py --max-pages 5

# Limit number of executions to fetch (for testing)
python fetch_historical_calls.py --limit 10
```

## 📊 What Gets Fetched

For each execution, the script fetches:

1. **Execution Details** - Complete execution information
   - Status, timestamps, agent info
   - Telephony data (duration, recording URLs)
   - Cost breakdown
   - User data

2. **Transcript** - Full conversation transcript
   - Complete conversation text
   - Speaker labels (if available)

3. **Recording URL** - Call recording download link
   - Extracted from telephony_data
   - Direct link to audio file

4. **Execution Logs/Traces** - Detailed execution logs
   - Component logs
   - LLM interactions
   - System traces
   - Error logs (if any)

5. **Raw Data** - Complete API response
   - Full JSON response from Bolna API
   - All available fields
   - Metadata

6. **Extracted Data** - Structured extraction
   - call_outcome (ACCEPTED/REJECTED/RESCHEDULED)
   - original_slot, final_slot
   - Notes

## 💾 Storage

All fetched data is stored in:
```
data/webhook_data.json
```

Each execution is stored with:
- Complete execution details
- Transcript
- Recording URL
- Execution logs
- Raw API response
- Timestamp when fetched
- Source marker (`fetched_from: 'bolna_api'`)

## 🔍 View Fetched Data

### View All Stored Data
```bash
python view_webhook_data.py
```

### View Specific Execution
```bash
python view_webhook_data.py --execution-id exec_12345
```

### View with Full Details
```bash
python view_webhook_data.py --execution-id exec_12345 --full
```

## 📋 Examples

### Example 1: Fetch Recent Calls
```bash
# Fetch first 10 executions (testing)
python fetch_historical_calls.py --limit 10
```

### Example 2: Fetch All Calls from Agent
```bash
# Fetch all calls (up to 10 pages = 500 executions)
python fetch_historical_calls.py --max-pages 10
```

### Example 3: Fetch Specific Call
```bash
# Fetch complete data for one call
python fetch_historical_calls.py --execution-id 3dddf7ed-5ef4-4dbb-8e27-aace39fc1e61
```

## 🔄 Data Flow

```
Bolna API Call History Dashboard
         ↓
list_executions() → Get all execution IDs
         ↓
For each execution:
  ├─ get_execution_details() → Full execution data
  ├─ get_transcript() → Conversation transcript
  ├─ get_execution_logs() → Traces and logs
  └─ Extract recording URL → From telephony_data
         ↓
Save to data/webhook_data.json
         ↓
Permanent storage with all data
```

## ⚙️ Configuration

The script uses:
- `AGENT_ID` from `config.py` (or `.env`)
- `BOLNA_API_KEY` from `.env`
- Automatically finds candidate mappings from `execution_mapping.json`

## 📊 Output

The script provides:
- Progress updates for each execution
- Summary statistics (fetched, errors)
- Automatic saving to permanent storage
- Candidate ID mapping (if available)

## 💡 Tips

1. **Rate Limiting**: The script includes automatic rate limiting (0.3s between requests)

2. **Pagination**: Default fetches 10 pages (500 executions). Adjust with `--max-pages`

3. **Testing**: Use `--limit` to test with a small number first

4. **Resume**: If interrupted, re-run to continue. Existing data is preserved and updated

5. **Incremental**: Only fetches new data. Existing executions are updated with latest data

## 🔗 Related Scripts

- `view_webhook_data.py` - View stored data
- `fetch_execution_details.py` - Fetch single execution details
- `migrate_webhook_logs.py` - Migrate old logs

