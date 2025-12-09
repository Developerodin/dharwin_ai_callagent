"""
Configuration file for Bolna AI Voice Calling Agent
Loads configuration from environment variables (.env file)
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bolna AI API Configuration
BOLNA_API_BASE = "https://api.bolna.ai"

# Load API key from environment variables
# Get your actual API key from: https://platform.bolna.ai/ → Developers tab
BOLNA_API_KEY = os.getenv("BOLNA_API_KEY", "")

# Agent Configuration
AGENT_NAME = "Ava - Bolna AI Voice Calling Agent"
AGENT_TYPE = "conversational"

# Model Configuration
MODEL_PROVIDER = "openai"
MODEL_NAME = "gpt-4"
TEMPERATURE = 0.7

# Voice Configuration
VOICE_PROVIDER = "elevenlabs"
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice ID from ElevenLabs
VOICE_LANGUAGE = "en"

# Agent ID (if you already have an agent created)
AGENT_ID = os.getenv("AGENT_ID", None)  # Will create new agent if none exists

