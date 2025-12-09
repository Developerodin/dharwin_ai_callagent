# TTS Time Formatting for Natural Speech

## Overview

The agent now formats times in natural speech format for better TTS (Text-to-Speech) output. Instead of saying "2:00 PM", the agent will say "2 o'clock in the afternoon".

## Implementation

### Time Formatter Module

Created `time_formatter.py` with functions to convert time formats:

- **`format_time_for_speech(time_str)`** - Converts "10:00 A.M." → "10 o'clock in the morning"
- **`format_datetime_for_speech(datetime_str)`** - Formats full datetime strings
- **`format_slots_for_speech(slots)`** - Formats arrays of datetime slots

### Examples

| Input | Output |
|-------|--------|
| "10:00 A.M." | "10 o'clock in the morning" |
| "2:00 P.M." | "2 o'clock in the afternoon" |
| "11:00 P.M." | "11 o'clock at night" |
| "6:00 P.M." | "6 o'clock in the evening" |
| "12:00 P.M." | "12 o'clock in the afternoon" (noon) |
| "12:00 A.M." | "12 o'clock at night" (midnight) |
| "6:30 A.M." | "6 30 in the morning" |

### Time of Day Logic

- **Morning**: 6:00 AM - 11:59 AM → "in the morning"
- **Afternoon**: 12:00 PM - 5:59 PM → "in the afternoon"
- **Evening**: 6:00 PM - 8:59 PM → "in the evening"
- **Night**: 9:00 PM - 11:59 PM → "at night"
- **Early Morning**: 1:00 AM - 5:59 AM → "in the early morning"
- **Midnight**: 12:00 AM → "at night"

## Integration

### System Prompt

Updated `system_prompt.py` to instruct the agent to:
- Always use natural time formatting
- Use formatted time variables from context
- Never say "2:00 PM" or "10:00 AM" format

### Agent Configuration

Updated `bolna_agent.py` to:
- Format times before sending to Bolna AI
- Provide both original and formatted times in context variables:
  - `interview_time` - Original format (for reference)
  - `interview_time_formatted` - Natural speech format (for TTS)
  - `alternative_slots` - Original format array
  - `alternative_slots_formatted` - Natural speech format array

### API Server

Updated `api_server.py` to import time formatting functions for future use.

## Context Variables Available to Agent

When making a call, the agent receives these context variables:

```python
{
    "candidate_name": "John Doe",
    "interview_date": "Friday, the 12th of December",
    "interview_time": "10:00 A.M.",  # Original format
    "interview_time_formatted": "10 o'clock in the morning",  # For TTS
    "interview_datetime": "Friday, the 12th of December at 10:00 A.M.",
    "interview_datetime_formatted": "Friday, the 12th of December at 10 o'clock in the morning",
    "alternative_slots": ["Monday, the 15th at 2:00 P.M.", ...],  # Original
    "alternative_slots_formatted": ["Monday, the 15th at 2 o'clock in the afternoon", ...]  # For TTS
}
```

## Usage Examples

### Example 1: Confirming Interview Time

**Before:**
> "Your interview is scheduled for Friday, the 12th of December at 10:00 A.M."

**After:**
> "Your interview is scheduled for Friday, the 12th of December at 10 o'clock in the morning"

### Example 2: Offering Alternative Slots

**Before:**
> "Option one: Monday, the 15th of December at 2:00 P.M."
> "Option two: Tuesday, the 16th of December at 11:00 P.M."

**After:**
> "Option one: Monday, the 15th of December at 2 o'clock in the afternoon"
> "Option two: Tuesday, the 16th of December at 11 o'clock at night"

## Testing

Run the time formatter test:

```bash
python time_formatter.py
```

This will show examples of all time conversions.

## Benefits

1. **More Natural Speech** - Sounds like a human speaking
2. **Better TTS Quality** - ElevenLabs TTS reads "2 o'clock" more naturally than "2:00 PM"
3. **Clearer Communication** - Easier to understand over the phone
4. **Professional** - More conversational and less robotic

## Webhook Integration

The existing webhook endpoint (`/api/webhook`) continues to work as before. Times are formatted when calls are initiated, ensuring the agent always uses natural time formatting in its speech.

## Notes

- The agent is instructed to **always** use formatted times in speech
- Original time formats are preserved for data storage and reference
- Both formats are available in context variables for flexibility

