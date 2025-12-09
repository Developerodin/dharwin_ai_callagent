# Candidate Management Features

## ✅ Features Implemented

### 1. Individual Candidate Reset Button
- ✅ Each candidate card now has a **"🔄 Reset"** button
- ✅ Resets candidate status to 'pending'
- ✅ Clears rescheduling history (removes `originalInterview`)
- ✅ Confirmation dialog before reset
- ✅ Backend endpoint: `POST /api/candidate/<candidate_id>/reset`

### 2. Add New Candidate
- ✅ **"➕ Add Candidate"** button in the header
- ✅ Modal form with all required fields:
  - Name *
  - Phone *
  - Email *
  - Position *
  - Scheduled Interview Slot * (dropdown from available slots)
  - Rescheduling Slots (multi-select checkboxes)
  - Application Date (defaults to today)
- ✅ Backend endpoint: `POST /api/candidate/add`
- ✅ Auto-generates new candidate ID
- ✅ Validates required fields

### 3. Manage Rescheduling Slots
- ✅ **"📅 Manage Slots"** button on each candidate card
- ✅ Modal showing all available slots
- ✅ Check/uncheck slots to assign to candidate
- ✅ Shows currently assigned slots
- ✅ Updates candidate's `reschedulingSlots` array
- ✅ Backend endpoint: `PUT /api/candidate/<candidate_id>/rescheduling-slots`

## 🔧 Implementation Details

### Backend API Endpoints

#### 1. Reset Individual Candidate
```python
POST /api/candidate/<candidate_id>/reset
```
- Resets status to 'pending'
- Removes `originalInterview` if exists
- Clears rescheduling history

#### 2. Add New Candidate
```python
POST /api/candidate/add
Body: {
  "name": "string",
  "phone": "string",
  "email": "string",
  "position": "string",
  "scheduledInterview": {
    "date": "string",
    "time": "string",
    "day": "string",
    "datetime": "string"
  },
  "applicationDate": "YYYY-MM-DD",
  "reschedulingSlots": [1, 2, 3]
}
```

#### 3. Update Rescheduling Slots
```python
PUT /api/candidate/<candidate_id>/rescheduling-slots
Body: {
  "reschedulingSlots": [1, 2, 3]
}
```

### Frontend Components

#### 1. CandidateCard
- Added `onReset` prop
- Added `onManageSlots` prop
- Reset button with red styling
- Manage Slots button

#### 2. AddCandidateModal
- Full form with validation
- Dropdown for scheduled interview slot
- Multi-select for rescheduling slots
- Submits to backend API

#### 3. ManageReschedulingSlotsModal
- Shows candidate name
- Lists all available slots
- Checkboxes for selection
- Visual feedback for selected slots
- Saves changes to backend

### Data Structure Updates

#### Candidate with Rescheduling Slots
```json
{
  "id": 1,
  "name": "Prakhar Sharma",
  "status": "pending",
  "scheduledInterview": { ... },
  "originalInterview": { ... },  // Only when rescheduled
  "reschedulingSlots": [1, 3, 5]  // Array of slot IDs
}
```

## 📝 Usage Instructions

### Reset Candidate
1. Click **"🔄 Reset"** button on candidate card
2. Confirm in dialog
3. Candidate status resets to 'pending'
4. Rescheduling history is cleared

### Add New Candidate
1. Click **"➕ Add Candidate"** button in header
2. Fill in all required fields
3. Select scheduled interview slot
4. (Optional) Select rescheduling slots
5. Click **"Add Candidate"**
6. New candidate appears in list

### Manage Rescheduling Slots
1. Click **"📅 Manage Slots"** button on candidate card
2. Modal opens showing all available slots
3. Check/uncheck slots to assign
4. Selected slots are highlighted
5. Click **"Save"**
6. Slots are updated for that candidate

## ✅ Validation

- Required fields validated before submission
- Slot IDs validated against available slots
- Candidate existence checked before updates
- Confirmation dialogs for destructive actions
- Error messages for failed operations

---

**All candidate management features are now fully functional!** ✅

