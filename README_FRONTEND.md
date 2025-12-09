# Next.js Frontend - Dharwin Interview Scheduler

A modern web interface for managing interview scheduling calls using the Bolna AI voice agent.

## Features

- 📋 View all candidates with their interview schedules
- 📞 Initiate voice calls to candidates
- 🔄 Real-time call status updates
- 📅 View and manage available interview slots
- 🎨 Modern, responsive UI with gradient design

## Setup

### 1. Install Dependencies

```bash
npm install
# or
yarn install
```

### 2. Run Development Server

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Connect to Backend (Optional)

To enable actual Bolna AI calls, you need to run the Flask API server:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Make sure .env file has BOLNA_API_KEY set
# Add CALLER_ID to .env (optional):
# CALLER_ID=+911234567890

# Run Flask server
python api_server.py
```

Then update the Next.js API routes to call `http://localhost:5000` instead of using mock data.

## Project Structure

```
├── app/
│   ├── api/              # Next.js API routes
│   │   ├── candidates/   # Fetch candidate list
│   │   ├── call/         # Initiate calls
│   │   └── call-status/  # Get call status
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Main page
│   └── globals.css       # Global styles
├── components/
│   ├── CandidateList.tsx # Candidate list component
│   ├── CandidateCard.tsx # Individual candidate card
│   └── CallStatus.tsx    # Call status display
├── data/
│   └── candidates.json   # Mock candidate data
└── api_server.py         # Flask backend (optional)
```

## Mock Data

The `data/candidates.json` file contains:
- **Candidates**: List of job applicants with their details
- **Available Slots**: Alternative interview time slots for rescheduling

### Sample Candidate (Prakhar Sharma)

```json
{
  "id": 1,
  "name": "Prakhar Sharma",
  "phone": "+918755887760",
  "email": "prakhar.sharma@example.com",
  "position": "Software Engineer",
  "status": "pending",
  "scheduledInterview": {
    "date": "Friday, the 12th of December",
    "time": "10:00 A.M.",
    "day": "Friday",
    "datetime": "Friday, the 12th of December at 10:00 A.M."
  }
}
```

## API Endpoints

### GET `/api/candidates`
Returns the list of all candidates with their interview schedules.

### POST `/api/call`
Initiates a call to a candidate.

**Request Body:**
```json
{
  "candidateId": 1,
  "phone": "+918755887760",
  "name": "Prakhar Sharma",
  "interviewDate": "Friday, the 12th of December",
  "interviewTime": "10:00 A.M."
}
```

**Response:**
```json
{
  "success": true,
  "executionId": "exec_1234567890_1",
  "alternativeSlots": [
    "Monday, the 15th of December at 2:00 P.M.",
    "Tuesday, the 16th of December at 11:00 A.M."
  ]
}
```

### GET `/api/call-status/[executionId]`
Gets the status of an ongoing or completed call.

### GET `/api/available-slots`
Gets available interview slots, optionally excluding a specific datetime.

**Query Parameters:**
- `exclude`: Datetime to exclude from results

## Integration with Bolna AI

To connect the frontend with actual Bolna AI calls:

1. **Update API Routes**: Modify `app/api/call/route.ts` to call the Flask server:
   ```typescript
   const response = await fetch('http://localhost:5000/api/call', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ ... })
   })
   ```

2. **Run Flask Server**: Start `api_server.py` which bridges Next.js with Bolna AI

3. **Configure Environment**: Ensure `.env` has:
   - `BOLNA_API_KEY`: Your Bolna AI API key
   - `CALLER_ID`: Your caller ID number (optional)

## Available Slots for Rescheduling

When a candidate declines their scheduled interview, the system automatically fetches available slots from `candidates.json`. The agent (Ava) will offer these alternative slots during the call:

- Monday, the 15th of December at 2:00 P.M.
- Tuesday, the 16th of December at 11:00 A.M.
- Wednesday, the 17th of December at 3:00 P.M.
- And more...

## Candidate Status

Candidates can have the following statuses:
- **pending**: Interview not yet confirmed
- **calling**: Call in progress
- **confirmed**: Interview slot confirmed
- **declined**: Candidate declined or not interested

## Build for Production

```bash
npm run build
npm start
```

## Technologies Used

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **CSS Modules**: Component styling
- **Flask**: Python backend API (optional)

