# Candidate-Specific Rescheduling Slots Fix

## Problem
The agent was offering slots that weren't allocated to the specific candidate, including slots that don't exist or aren't in their `reschedulingSlots` array.

## Solution

### 1. Enhanced Slot Filtering Logic (`api_server.py`)

**Changes:**
- Added validation to ensure slot IDs exist in `availableSlots`
- Filters out invalid slot IDs with warning logs
- Ensures current interview datetime is excluded
- Only passes valid, candidate-specific slots to the agent

**Key Improvements:**
```python
# Validates each slot ID before including
for slot_id in slot_ids:
    if slot_id not in slot_map:
        invalid_slot_ids.append(slot_id)
        print(f"⚠️  Slot ID {slot_id} not found in availableSlots")
        continue
    
    slot_datetime = slot_map[slot_id]['datetime']
    if slot_datetime == current_datetime:
        print(f"⚠️  Skipping slot ID {slot_id} (same as current interview)")
        continue
    
    valid_slots.append(slot_datetime)
```

**Logging:**
- Shows requested slot IDs vs. valid slot datetimes
- Warns about invalid slot IDs
- Alerts if no valid slots are found after filtering

### 2. Enhanced System Prompt (`system_prompt.py`)

**Added Explicit Restrictions:**

1. **In "If Candidate Cannot Attend" Section:**
   - ⭐ CRITICAL: MUST ONLY offer slots from `{alternative_slots_formatted}`
   - DO NOT invent, suggest, or reference any other time slots
   - These are the ONLY available alternatives for this candidate

2. **In Guardrails Section:**
   - Added explicit "Never" rules:
     - ⭐ SUGGEST, OFFER, OR MENTION ANY TIME SLOTS NOT IN `{alternative_slots_formatted}`
     - ⭐ Reference dates or times not in the array
     - ⭐ Invent or create new slot options
   - Added explicit "Always" rule:
     - ⭐ ONLY offer slots from `{alternative_slots_formatted}`

3. **Updated FAQ Section:**
   - Modified "Can I reschedule my interview?" response to explicitly use only provided slots

## How It Works

### Flow:
1. **API receives call request** with `candidate_id`
2. **Reads candidate data** from `candidates.json`
3. **Extracts `reschedulingSlots` array** (e.g., `[1, 3, 5]`)
4. **Validates each slot ID:**
   - Checks if slot ID exists in `availableSlots`
   - Excludes slot if it matches current interview datetime
   - Logs warnings for invalid IDs
5. **Builds filtered list** of valid slot datetimes
6. **Passes to agent** via `alternative_slots` parameter
7. **Agent receives** only valid, candidate-specific slots in `{alternative_slots_formatted}`

### Example:
For Candidate 1 with `reschedulingSlots: [1, 3, 5]`:
- Slot ID 1: "Monday, the 15th of December at 2:00 P.M." ✅ Valid
- Slot ID 3: "Wednesday, the 17th of December at 3:00 P.M." ✅ Valid
- Slot ID 5: "Friday, the 19th of December at 1:00 P.M." ✅ Valid

**Result:** Agent will ONLY offer these 3 slots, nothing else.

## Verification

To verify the fix is working:

1. **Check logs** when making a call:
   ```
   📅 Using candidate-specific rescheduling slots for candidate 1:
      Requested slot IDs: [1, 3, 5]
      Valid slot datetimes: ['Monday, the 15th of December at 2:00 P.M.', ...]
   ```

2. **Monitor agent behavior:**
   - Agent should only mention slots from `{alternative_slots_formatted}`
   - No references to other dates/times not in the array

3. **Test with invalid slot IDs:**
   - If a candidate has invalid slot IDs, warnings will appear in logs
   - Invalid slots will be skipped automatically

## Files Modified

1. **`api_server.py`** (lines 564-613)
   - Enhanced slot filtering and validation
   - Added comprehensive logging

2. **`system_prompt.py`** (multiple sections)
   - Added explicit restrictions in Guardrails
   - Enhanced "If Candidate Cannot Attend" section
   - Updated FAQ response

## Testing Checklist

- [x] Slot IDs are validated against `availableSlots`
- [x] Invalid slot IDs are filtered out with warnings
- [x] Current interview datetime is excluded
- [x] Only valid slots are passed to agent
- [x] System prompt explicitly restricts to provided slots only
- [x] Agent cannot invent or suggest other slots

## Notes

- The agent will now strictly follow the `reschedulingSlots` array
- If a candidate has no valid slots after filtering, a warning is logged
- The system prompt has multiple layers of enforcement to prevent slot invention
- All slot validation happens server-side before the call is initiated

