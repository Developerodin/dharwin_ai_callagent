# Candidate-Specific Rescheduling Slots

## ✅ Changes Applied

Each candidate now has **assigned rescheduling slots** that are **only offered to them** during calls.

### 📋 Slot Assignments

**Available Slots Reference:**
- Slot 1: Monday, the 15th of December at 2:00 P.M.
- Slot 2: Tuesday, the 16th of December at 11:00 A.M.
- Slot 3: Wednesday, the 17th of December at 3:00 P.M.
- Slot 4: Thursday, the 18th of December at 10:30 A.M.
- Slot 5: Friday, the 19th of December at 1:00 P.M.
- Slot 6: Monday, the 22nd of December at 9:00 A.M.
- Slot 7: Tuesday, the 23rd of December at 2:30 P.M.

**Candidate Assignments:**

1. **Prakhar Sharma** (ID: 1)
   - Scheduled: Friday, the 12th of December at 11:00 A.M.
   - Rescheduling Slots: **[1, 3, 5]**
     - Monday, the 15th at 2:00 P.M.
     - Wednesday, the 17th at 3:00 P.M.
     - Friday, the 19th at 1:00 P.M.

2. **Ronak Vaya** (ID: 2)
   - Scheduled: Monday, the 15th of December at 2:00 P.M.
   - Rescheduling Slots: **[2, 4, 6]**
     - Tuesday, the 16th at 11:00 A.M.
     - Thursday, the 18th at 10:30 A.M.
     - Monday, the 22nd at 9:00 A.M.

3. **Priya Patel** (ID: 3)
   - Scheduled: Tuesday, the 16th of December at 11:00 A.M.
   - Rescheduling Slots: **[3, 6, 7]**
     - Wednesday, the 17th at 3:00 P.M.
     - Monday, the 22nd at 9:00 A.M.
     - Tuesday, the 23rd at 2:30 P.M.

4. **Amit Kumar** (ID: 4)
   - Scheduled: Wednesday, the 17th of December at 3:00 P.M.
   - Rescheduling Slots: **[4, 1, 5]**
     - Thursday, the 18th at 10:30 A.M.
     - Monday, the 15th at 2:00 P.M.
     - Friday, the 19th at 1:00 P.M.

5. **Sneha Singh** (ID: 5)
   - Scheduled: Thursday, the 18th of December at 10:30 A.M.
   - Rescheduling Slots: **[5, 2, 7]**
     - Friday, the 19th at 1:00 P.M.
     - Tuesday, the 16th at 11:00 A.M.
     - Tuesday, the 23rd at 2:30 P.M.

## 🔧 Technical Implementation

### 1. Data Structure (`data/candidates.json`)
Each candidate now has a `reschedulingSlots` field:
```json
{
  "id": 1,
  "name": "Prakhar Sharma",
  ...
  "reschedulingSlots": [1, 3, 5],
  ...
}
```

### 2. Backend (`api_server.py`)
- ✅ Checks for `reschedulingSlots` in candidate data
- ✅ Maps slot IDs to actual slot datetimes
- ✅ Excludes the candidate's currently scheduled slot
- ✅ Falls back to default behavior if no slots assigned
- ✅ Logs which slots are being used

### 3. Frontend API (`app/api/call/route.ts`)
- ✅ Updated to use candidate-specific slots
- ✅ Same fallback logic as backend

## 🎯 How It Works

1. **When a call is initiated:**
   - System reads candidate's `reschedulingSlots` array
   - Maps slot IDs to actual slot datetimes from `availableSlots`
   - Excludes the candidate's current scheduled slot
   - Passes only these slots to the agent

2. **During the call:**
   - Agent only offers the candidate's assigned slots
   - Agent cannot offer slots not in their `reschedulingSlots` array

3. **If no slots assigned:**
   - System falls back to default behavior (first 3 available slots)
   - Warning is logged for missing slot assignments

## ✅ Benefits

- **Control**: Each candidate gets specific slots assigned to them
- **Organization**: Prevents offering unavailable slots
- **Flexibility**: Easy to modify assignments per candidate
- **Backward Compatible**: Falls back if slots not assigned

## 📝 To Modify Slot Assignments

Simply edit `data/candidates.json` and update the `reschedulingSlots` array for any candidate:

```json
{
  "id": 1,
  "reschedulingSlots": [1, 3, 5]  // Change these IDs
}
```

The slot IDs must match the `id` field in the `availableSlots` array.

---

**Each candidate now has their own specific rescheduling slots!** ✅

