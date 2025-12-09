# Batch Executions API Guide

This guide explains how to fetch batch executions from Bolna AI using the Execution API.

## Overview

The Batch Executions API allows you to retrieve all executions (call records) with detailed information including:
- Call outcomes and status
- Conversation metrics
- Transcripts
- Telephony data (duration, recording URLs)
- Extracted data
- Cost breakdowns

## Usage

### Command Line Tool

Fetch executions using the command-line script:

```bash
# Fetch all executions for your agent
python fetch_batch_executions.py

# Fetch executions with details
python fetch_batch_executions.py --details

# Fetch specific batch
python fetch_batch_executions.py --batch-id BATCH_ID

# Fetch for specific agent
python fetch_batch_executions.py --agent-id AGENT_ID

# Fetch specific page
python fetch_batch_executions.py --page 1 --page-size 50

# Fetch all pages automatically
python fetch_batch_executions.py --all-pages

# Output as JSON
python fetch_batch_executions.py --json
```

### Python Code

```python
from fetch_batch_executions import fetch_batch_executions

# Fetch executions
data = fetch_batch_executions(
    batch_id=None,  # Optional batch ID
    agent_id="your_agent_id",  # Optional agent ID
    page_number=1,
    page_size=50
)

if data:
    executions = data.get('data', [])
    total = data.get('total', 0)
    print(f"Found {total} executions")
```

### Flask API Endpoint

Query executions via HTTP:

```bash
# Get all executions
GET http://localhost:5000/api/executions

# With query parameters
GET http://localhost:5000/api/executions?agent_id=AGENT_ID&page_number=1&page_size=50

# Specific batch
GET http://localhost:5000/api/executions?batch_id=BATCH_ID
```

## Response Format

### Paginated Response

```json
{
  "success": true,
  "data": {
    "page_number": 1,
    "page_size": 50,
    "total": 150,
    "has_more": true,
    "data": [
      {
        "execution_id": "exec_1234567890",
        "status": "completed",
        "created_at": "2024-12-08T10:30:00Z",
        "telephony_data": {
          "duration": 120,
          "recipient_phone_number": "+918755887760",
          "call_status": "completed",
          "recording_url": "https://..."
        },
        "transcript": "Full conversation transcript...",
        "extracted_data": {
          "status": "confirmed",
          "user_interested": true
        },
        "cost_breakdown": {
          "total_cost": 0.05,
          "components": {...}
        }
      }
    ]
  }
}
```

## Use Cases

### 1. Monitor All Calls

```bash
# Get all executions for your agent
python fetch_batch_executions.py --all-pages --details
```

### 2. Analyze Call Metrics

```python
from fetch_batch_executions import fetch_batch_executions
import json

data = fetch_batch_executions(all_pages=True)
executions = data['data']

# Calculate metrics
total_calls = len(executions)
completed = sum(1 for e in executions if e['status'] == 'completed')
total_duration = sum(
    e.get('telephony_data', {}).get('duration', 0) 
    for e in executions
)

print(f"Total Calls: {total_calls}")
print(f"Completed: {completed}")
print(f"Average Duration: {total_duration / total_calls:.1f}s")
```

### 3. Export to CSV

```python
import csv
from fetch_batch_executions import fetch_batch_executions

data = fetch_batch_executions(all_pages=True)
executions = data['data']

with open('executions.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Execution ID', 'Status', 'Duration', 'Recipient', 'Created'])
    
    for exec_data in executions:
        telephony = exec_data.get('telephony_data', {})
        writer.writerow([
            exec_data.get('execution_id'),
            exec_data.get('status'),
            telephony.get('duration', 0),
            telephony.get('recipient_phone_number', ''),
            exec_data.get('created_at', '')
        ])
```

### 4. Find Failed Calls

```python
from fetch_batch_executions import fetch_batch_executions

data = fetch_batch_executions(all_pages=True)
failed = [
    e for e in data['data'] 
    if e['status'].lower() in ['failed', 'error', 'cancelled']
]

print(f"Found {len(failed)} failed calls")
for exec_data in failed:
    print(f"- {exec_data['execution_id']}: {exec_data['status']}")
```

## Integration with Webhook

The batch executions API complements the webhook system:

- **Webhook**: Real-time updates when calls complete
- **Batch API**: Historical data and bulk analysis

You can use batch executions to:
- Verify webhook updates were processed correctly
- Backfill missing data if webhooks failed
- Analyze historical call patterns
- Generate reports

## Query Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `batch_id` | string | Filter by batch ID | None (all batches) |
| `agent_id` | string | Filter by agent ID | Uses config AGENT_ID |
| `page_number` | integer | Page number | 1 |
| `page_size` | integer | Results per page | 50 (max 100) |

## Response Fields

Each execution includes:

- **execution_id**: Unique execution identifier
- **status**: Call status (completed, failed, in_progress, etc.)
- **created_at**: Timestamp when call was created
- **updated_at**: Last update timestamp
- **agent_id**: Agent that handled the call
- **telephony_data**: Call metadata
  - `duration`: Call duration in seconds
  - `recipient_phone_number`: Called number
  - `call_status`: Detailed call status
  - `recording_url`: Call recording URL (if available)
- **transcript**: Full conversation transcript
- **extracted_data**: Structured data extracted from conversation
- **cost_breakdown**: Cost information
- **context_details**: Additional context data

## Error Handling

```python
from fetch_batch_executions import fetch_batch_executions

data = fetch_batch_executions()

if not data:
    print("Failed to fetch executions")
    print("Check:")
    print("1. BOLNA_API_KEY is set in .env")
    print("2. Agent ID is correct")
    print("3. API endpoint is accessible")
else:
    print(f"Successfully fetched {data.get('total', 0)} executions")
```

## Best Practices

1. **Use Pagination**: Don't fetch all pages at once for large datasets
2. **Cache Results**: Store frequently accessed data locally
3. **Filter by Date**: Use timestamps to filter recent executions
4. **Handle Rate Limits**: Add delays between requests if needed
5. **Error Retry**: Implement retry logic for failed requests

## Examples

### Example 1: Get Recent Executions

```python
from fetch_batch_executions import fetch_batch_executions
from datetime import datetime, timedelta

data = fetch_batch_executions(page_size=100)
executions = data['data']

# Filter recent (last 24 hours)
now = datetime.now()
recent = [
    e for e in executions 
    if datetime.fromisoformat(e['created_at'].replace('Z', '+00:00')) > now - timedelta(days=1)
]

print(f"Recent calls (24h): {len(recent)}")
```

### Example 2: Export All Transcripts

```python
from fetch_batch_executions import fetch_batch_executions
import json

data = fetch_batch_executions(all_pages=True)
executions = data['data']

transcripts = []
for exec_data in executions:
    transcript = exec_data.get('transcript') or exec_data.get('conversation_transcript')
    if transcript:
        transcripts.append({
            'execution_id': exec_data.get('execution_id'),
            'status': exec_data.get('status'),
            'transcript': transcript
        })

with open('all_transcripts.json', 'w') as f:
    json.dump(transcripts, f, indent=2)
```

### Example 3: Monitor via Flask Endpoint

```bash
# In your application
curl http://localhost:5000/api/executions?page_size=10
```

## Troubleshooting

**No executions returned:**
- Check if agent_id is correct
- Verify calls have been made
- Check date range (executions might be old)

**API errors:**
- Verify BOLNA_API_KEY in .env
- Check API endpoint URL
- Review rate limits

**Missing data:**
- Some fields may not be available immediately
- Wait for calls to complete
- Check execution status

