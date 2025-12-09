# Original Interview Tracking for Rescheduled Candidates

## ✅ Changes Applied

When a candidate's interview is rescheduled, the system now **preserves the original interview date/time** so HR can see both:
1. **Original Interview**: When it was originally supposed to happen
2. **Rescheduled Interview**: The new scheduled time

## 📋 Data Structure

### Before Rescheduling
```json
{
  "id": 1,
  "name": "Prakhar Sharma",
  "status": "pending",
  "scheduledInterview": {
    "date": "Friday, the 12th of December",
    "time": "11:00 A.M.",
    "datetime": "Friday, the 12th of December at 11:00 A.M."
  }
}
```

### After Rescheduling
```json
{
  "id": 1,
  "name": "Prakhar Sharma",
  "status": "rescheduled",
  "scheduledInterview": {
    "date": "Monday, the 15th of December",
    "time": "2:00 P.M.",
    "datetime": "Monday, the 15th of December at 2:00 P.M."
  },
  "originalInterview": {
    "date": "Friday, the 12th of December",
    "time": "11:00 A.M.",
    "datetime": "Friday, the 12th of December at 11:00 A.M."
  }
}
```

## 🔧 Technical Implementation

### 1. Backend Update (`update_candidate_status.py`)

When status is set to `'rescheduled'`:
- ✅ Checks if `originalInterview` already exists (to prevent overwriting)
- ✅ Saves a copy of current `scheduledInterview` as `originalInterview`
- ✅ Updates `scheduledInterview` with the new rescheduled time
- ✅ Logs both original and new interview times

```python
# Preserve original interview if not already stored
if 'originalInterview' not in candidate:
    candidate['originalInterview'] = candidate['scheduledInterview'].copy()
    print(f"💾 Saved original interview: {candidate['originalInterview']['datetime']}")

# Update to new scheduled interview
candidate['scheduledInterview'] = {
    'day': updated_interview.get('day', ...),
    'date': updated_interview.get('date', ...),
    'time': updated_interview.get('time', ...),
    'datetime': updated_interview.get('datetime', ...)
}
```

### 2. Frontend Update (`CandidateCard.tsx`)

**Display Logic:**
- ✅ If status is `'rescheduled'` AND `originalInterview` exists:
  - Shows **"Original Interview"** (yellow/amber background)
  - Shows **"Rescheduled Interview"** (green background)
- ✅ Otherwise:
  - Shows standard **"Scheduled Interview"** display

**Visual Design:**
- **Original Interview**: 
  - Background: Light yellow (`#fff3cd`)
  - Text: Dark yellow (`#856404`)
  - Border: Yellow accent (`#ffc107`)
  
- **Rescheduled Interview**:
  - Background: Light green (`#d4edda`)
  - Text: Dark green (`#155724`)
  - Border: Green accent (`#28a745`)

### 3. TypeScript Interfaces

Updated in both `CandidateCard.tsx` and `CandidateList.tsx`:
```typescript
interface Candidate {
  ...
  scheduledInterview: { ... }
  originalInterview?: {  // Optional - only exists when rescheduled
    date: string
    time: string
    day: string
    datetime: string
  }
  ...
}
```

## 🎯 User Experience

### For HR Team:

**Before Rescheduling:**
```
Scheduled Interview:
📅 Friday, the 12th of December at 11:00 A.M.
```

**After Rescheduling:**
```
Original Interview:
📅 Friday, the 12th of December at 11:00 A.M.

Rescheduled Interview:
📅 Monday, the 15th of December at 2:00 P.M.
```

## ✅ Benefits

1. **Full History**: HR can see when the interview was originally scheduled
2. **Audit Trail**: Track all rescheduling changes
3. **Planning**: Understand interview scheduling patterns
4. **Transparency**: Clear visibility of original vs. new time

## 📝 Behavior Notes

- **Original is preserved once**: If a candidate is rescheduled multiple times, the `originalInterview` keeps the very first scheduled time
- **Only for rescheduled status**: `originalInterview` only appears when status is `'rescheduled'`
- **Backward compatible**: Candidates without `originalInterview` display normally

---

**Original interview data is now preserved and displayed for rescheduled candidates!** ✅

