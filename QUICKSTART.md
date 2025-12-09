# Quick Start Guide

## 🚀 Getting Started

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

1. Copy `.env.example` to `.env` (if it doesn't exist, create it)
2. Add your Bolna AI API key:

```env
BOLNA_API_KEY=your_actual_api_key_here



### Step 3: Install Node.js Dependencies

```bash
npm install
```

### Step 4: Start the Flask Backend (Optional but Recommended)

In one terminal:

```bash
python api_server.py
```

This will start the Flask server on `http://localhost:5000`

### Step 5: Start the Next.js Frontend

In another terminal:

```bash
npm run dev
```

This will start the Next.js app on `http://localhost:3000`

## 📱 Using the Application

1. Open `http://localhost:3000` in your browser
2. You'll see a list of candidates including:
   - **Prakhar Sharma** (your name) - Phone: +918755887760
   - Other mock candidates
3. Click "📞 Call Now" next to any candidate to initiate a call
4. The system will:
   - Update the candidate status to "calling"
   - Initiate the call via Bolna AI (if Flask backend is running)
   - Show call status in real-time
   - Provide available slots for rescheduling if the candidate declines

## 🔄 Rescheduling Flow

When a candidate declines their scheduled interview:

1. The system fetches available slots from `data/candidates.json`
2. Ava (the voice agent) will offer these alternative slots during the call
3. The candidate can choose a new slot
4. The system updates the candidate's interview schedule

## 📊 Mock Data

The mock data includes:
- **5 candidates** with different positions
- **7 available interview slots** for rescheduling
- All candidates have scheduled interviews
- Status can be: `pending`, `calling`, `confirmed`, or `declined`

## 🛠️ Troubleshooting

### Flask Backend Not Connecting

- Make sure Flask server is running on port 5000
- Check that `.env` file has `BOLNA_API_KEY` set
- Verify the API key is valid

### Next.js Not Starting

- Make sure Node.js is installed (v18 or higher)
- Run `npm install` to install dependencies
- Check for port conflicts (default port is 3000)

### Calls Not Working

- Ensure Flask backend is running
- Verify Bolna AI API key is correct
- Check that SIP trunk is configured in Bolna AI dashboard
- Phone numbers must be in E.164 format (e.g., +918755887760)

## 📝 Notes

- The frontend works with mock data even without the Flask backend
- For actual calls, both Flask backend and Next.js frontend must be running
- Available slots are automatically fetched from JSON when a candidate needs to reschedule
- All candidate data is stored in `data/candidates.json`

