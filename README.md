# Bolna AI Voice Calling Agent - Ava

A complete voice calling agent system built with Bolna AI that handles interview scheduling for Dharwin job portal candidates. The agent, named Ava, can communicate in both English and Hindi to confirm or reschedule interview slots.

## 🎯 Project Structure

This project includes:
- **Python Backend**: Bolna AI agent integration (`bolna_agent.py`)
- **Next.js Frontend**: Modern web interface for managing calls
- **Flask API Server**: Bridge between frontend and Bolna AI
- **Mock Data**: JSON file with candidates and available slots

## Features

- 🤖 AI-powered voice agent with natural conversation flow
- 🌐 Bilingual support (English and Hindi)
- 📞 Automated outbound calling
- ⏰ Interview slot confirmation and rescheduling
- 💬 Context-aware conversations with candidate information
- 🔔 **Real-time webhook updates** - Automatically receive call execution data and update candidate status

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Create a `.env` file in the project root (copy from `.env.example` if it exists):
   ```bash
   cp .env.example .env
   ```

2. Get your Bolna AI API Key:
   - Log in to the [Bolna AI Dashboard](https://platform.bolna.ai/)
   - Navigate to the "Developers" tab
   - Click on "Generate a new API Key"
   - Save the API key securely (it will be shown only once)

3. Add your API key to the `.env` file:
   ```env
   BOLNA_API_KEY=your_actual_api_key_here
   API_BASE_NAME=bn-2e2bd14b4f0449358d8e8c2b0ebe556a
   API_KEY_NAME=sienna-edward-2072
   ```

**Important**: The `.env` file is already in `.gitignore` to protect your API key. Never commit it to version control.

### 3. Configure the Agent

You can modify the following settings in `config.py`:
- Model provider and name
- Voice provider and voice ID
- Temperature settings

### 4. System Prompt

The detailed system prompt for Ava is stored in `system_prompt.py`. It includes:
- Personality and demeanor guidelines
- Interview opening scripts (English & Hindi)
- Slot confirmation flows
- Response handling for different scenarios
- FAQs

## Usage

### Create the Agent

Run the main script to create the agent (API key is automatically loaded from `.env`):

```bash
python bolna_agent.py
```

### Make a Call

You can use the `BolnaAgent` class in your own scripts:

```python
from bolna_agent import BolnaAgent

# Initialize the agent (API key loaded from .env file)
agent = BolnaAgent()

# Create the agent (only needed once)
agent.create_agent()

# Make a call
result = agent.make_call(
    phone_number="+1234567890",  # Candidate's phone number (E.164 format)
    caller_id="+0987654321",     # Your caller ID (E.164 format)
    candidate_name="John Doe",
    interview_date="Friday, the 12th of December",
    interview_time="10:00 A.M.",
    alternative_slots=[
        "Monday, the 15th of December, at 2:00 P.M.",
        "Tuesday, the 16th of December, at 11:00 A.M."
    ]
)

# Get call execution details
execution_id = result.get("execution_id")
if execution_id:
    details = agent.get_execution_details(execution_id)
    print(details)
```

### Example Script

Use the provided `example_call.py` or create your own:

```python
from bolna_agent import BolnaAgent

# Initialize agent (API key loaded from .env file)
agent = BolnaAgent()

# Create agent if not already created
agent.create_agent()

# Make a call to a candidate
result = agent.make_call(
    phone_number="+919876543210",
    caller_id="+911234567890",
    candidate_name="Priya Sharma",
    interview_date="Friday, the 12th of December",
    interview_time="10:00 A.M.",
    alternative_slots=[
        "Monday, the 15th of December, at 2:00 P.M.",
        "Tuesday, the 16th of December, at 11:00 A.M."
    ]
)

print(f"Call initiated! Execution ID: {result.get('execution_id')}")
```

## Agent Behavior

Ava follows these key principles:

1. **Polite & Professional**: Maintains a warm, respectful tone
2. **Patient**: Allows candidates time to process information
3. **Clear Communication**: Speaks slowly when reading dates and times
4. **Bilingual**: Seamlessly switches between English and Hindi based on candidate preference
5. **Adaptive**: Adjusts pace and tone based on candidate comfort

## Phone Number Format

Always use E.164 format for phone numbers:
- Format: `+[country code][number]`
- Example: `+919876543210` (India), `+1234567890` (USA)

## API Endpoints Used

- `POST /agent` - Create a new agent
- `POST /agent/{agent_id}/call` - Make an outbound call
- `GET /execution/{execution_id}` - Get call execution details
- `GET /agent` - List all agents

## Configuration Files

- `.env` - Environment variables (API keys - **not committed to git**)
- `.env.example` - Template for environment variables
- `config.py` - API and agent configuration (loads from .env)
- `system_prompt.py` - Complete system prompt for Ava
- `bolna_agent.py` - Main agent class and functions

## Notes

- The agent ID is stored after creation, so you don't need to create it multiple times
- Make sure you have SIP trunk configured in Bolna AI dashboard for outbound calls
- The system prompt includes detailed instructions for handling various scenarios
- Ava will automatically adapt her language based on candidate preference

## Frontend (Next.js)

The project includes a modern Next.js frontend for managing interview calls. See [README_FRONTEND.md](README_FRONTEND.md) for detailed frontend documentation.

### Quick Frontend Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the candidate management interface.

### Mock Data

The frontend uses `data/candidates.json` which includes:
- **Prakhar Sharma** (Phone: +918755887760) - Software Engineer
- 4 additional mock candidates
- 7 available interview slots for rescheduling

## Flask API Server

To enable actual Bolna AI calls from the frontend, run the Flask server:

```bash
python api_server.py
```

This starts a server on `http://localhost:5000` that bridges the Next.js frontend with the Bolna AI Python backend.

### Webhook Support

The Flask server includes a webhook endpoint (`/api/webhook`) that receives real-time call execution data from Bolna AI and automatically updates candidate statuses. This eliminates the need for polling and provides instant updates.

**Setup Instructions:**
1. Configure your webhook URL in the Bolna AI dashboard (e.g., `https://your-domain.com/api/webhook`)
2. The webhook endpoint validates requests from Bolna AI's authorized IP addresses
3. Candidate statuses are updated automatically when calls complete

**Note:** Make sure to expose your Flask server using a tool like ngrok or deploy it to a public server for webhooks to work.

## Support

For API documentation, visit: https://www.bolna.ai/docs/api-reference/introduction

For issues or questions, refer to the Bolna AI platform documentation.

## Quick Start

### Using Startup Scripts (Recommended)

The easiest way to start the project is using the provided startup scripts:

#### First-Time Setup

**Windows:**
```powershell
.\start.ps1
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

The first-time setup script will:
- ✅ Check for Python and Node.js installations
- ✅ Create and activate Python virtual environment
- ✅ Install Python dependencies (if needed)
- ✅ Install Node.js dependencies (if needed)
- ✅ Start Flask API server on http://localhost:5000
- ✅ Start Next.js frontend on http://localhost:3000

#### Development Mode (with ngrok)

After initial setup, use the development script for daily development:

**Windows:**
```powershell
.\start-dev.ps1
```

**Linux/Mac:**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

The development script will:
- ✅ Activate Python virtual environment
- ✅ Start ngrok tunnel (for webhook support)
- ✅ Start Flask API server on http://localhost:5000
- ✅ Start Next.js frontend on http://localhost:3000
- ✅ Display webhook URL for Bolna AI configuration

**Note:** Make sure ngrok is installed before using `start-dev.ps1`. Download from [ngrok.com](https://ngrok.com/download).

### Manual Setup (Individual Commands)

If you prefer to start each component manually in separate terminals, see [START_COMMANDS.md](START_COMMANDS.md) for step-by-step instructions with individual commands.

For complete setup instructions, see [QUICKSTART.md](QUICKSTART.md).

