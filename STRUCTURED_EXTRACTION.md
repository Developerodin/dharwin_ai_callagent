# Structured Data Extraction

The agent now extracts structured data from call conversations in a standardized JSON format.

## Extraction Schema

After every call, the agent automatically extracts the following structured data:

```json
{
  "call_outcome": "ACCEPTED" | "REJECTED" | "RESCHEDULED",
  "original_slot": {
    "date": "YYYY-MM-DD",
    "time": "HH:MM AM/PM",
    "day_of_week": "Monday/Tuesday/etc"
  },
  "final_slot": {
    "date": "YYYY-MM-DD",
    "time": "HH:MM AM/PM", 
    "day_of_week": "Monday/Tuesday/etc"
  } | null,
  "notes": "Any additional relevant information"
}
```

## Rules

1. **call_outcome** must be one of:
   - `ACCEPTED` - Candidate confirmed the original slot
   - `REJECTED` - Candidate declined the interview
   - `RESCHEDULED` - Candidate requested a different time slot

2. **If ACCEPTED:**
   - `original_slot` and `final_slot` will be the same
   - Candidate confirmed without changes

3. **If REJECTED:**
   - `final_slot` will be `null`
   - Candidate declined the interview

4. **If RESCHEDULED:**
   - Both `original_slot` and `final_slot` must be populated
   - `final_slot` must be different from `original_slot`

5. **Date Format:** `YYYY-MM-DD` (e.g., "2024-12-12")
6. **Time Format:** `HH:MM AM/PM` (e.g., "10:00 AM", "02:00 PM")

## Examples

### ACCEPTED Example

```json
{
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
}
```

### REJECTED Example

```json
{
  "call_outcome": "REJECTED",
  "original_slot": {
    "date": "2024-12-12",
    "time": "10:00 AM",
    "day_of_week": "Thursday"
  },
  "final_slot": null,
  "notes": "Candidate no longer interested in the position"
}
```

### RESCHEDULED Example

```json
{
  "call_outcome": "RESCHEDULED",
  "original_slot": {
    "date": "2024-12-12",
    "time": "10:00 AM",
    "day_of_week": "Thursday"
  },
  "final_slot": {
    "date": "2024-12-15",
    "time": "02:00 PM",
    "day_of_week": "Sunday"
  },
  "notes": "Candidate had a conflict, selected alternative slot"
}
```

## How It Works

1. **Agent Configuration**
   - Extraction schema is configured in `bolna_agent.py`
   - `extraction_details` enables structured JSON output
   - `request_json: True` enables JSON response format

2. **System Prompt**
   - Updated to instruct agent to extract this structured data
   - Agent knows to output JSON after every call

3. **Webhook Processing**
   - Webhook receives `extracted_data` in payload
   - `parse_call_outcome()` processes structured data
   - Maps `call_outcome` to candidate status:
     - `ACCEPTED` → `confirmed`
     - `REJECTED` → `declined`
     - `RESCHEDULED` → `rescheduled`

4. **Slot Conversion**
   - `convert_slot_to_interview_format()` converts structured format to interview format
   - Updates candidate's `scheduledInterview` in JSON

## Data Flow

```
Call Ends
  ↓
Agent extracts structured data
  ↓
Webhook receives extracted_data
  ↓
parse_call_outcome() processes extraction
  ↓
convert_slot_to_interview_format() converts slots
  ↓
update_candidate_in_json() updates candidate status
```

## Viewing Extracted Data

The extracted data is available in:
1. **Webhook payloads** - Check Flask logs or ngrok dashboard
2. **Execution details** - Available via Execution API
3. **Webhook logs** - Saved in `webhook_logs.json` (if enabled)

## Configuration Files

- `call_extraction_schema.py` - Extraction schema definition
- `slot_converter.py` - Slot format conversion utilities
- `bolna_agent.py` - Agent configuration with extraction_details
- `system_prompt.py` - Instructions for agent to extract data
- `update_candidate_status.py` - Processing extracted data

