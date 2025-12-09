"""
Bolna AI Voice Calling Agent - Main Script
Creates and manages the Ava interview scheduling agent
"""

import requests
import json
from typing import Optional, Dict, Any
from config import (
    BOLNA_API_BASE,
    BOLNA_API_KEY,
    AGENT_NAME,
    AGENT_TYPE,
    MODEL_PROVIDER,
    MODEL_NAME,
    TEMPERATURE,
    VOICE_PROVIDER,
    VOICE_ID,
    VOICE_LANGUAGE
)
from system_prompt import SYSTEM_PROMPT, INTRO_PROMPT
from time_formatter import format_time_for_speech, format_datetime_for_speech, format_slots_for_speech
from call_extraction_schema import EXTRACTION_SCHEMA


class BolnaAgent:
    """Class to interact with Bolna AI API for voice calling agent"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Bolna Agent
        
        Args:
            api_key: Your Bolna AI API key (optional, will use from .env if not provided)
        """
        self.api_key = api_key or BOLNA_API_KEY
        if not self.api_key:
            raise ValueError("API key is required. Set BOLNA_API_KEY in .env file or pass it as parameter.")
        self.base_url = BOLNA_API_BASE
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.agent_id = None
    
    def create_agent(self) -> Dict[str, Any]:
        """
        Create a new voice calling agent on Bolna AI
        
        Returns:
            Dictionary containing agent creation response
        """
        url = f"{self.base_url}/agent"
        
        # Bolna AI API structure based on official documentation
        # Note: For ElevenLabs, voice/voice_id must be at top level, not in provider_config
        synthesizer_config = {
            "provider": VOICE_PROVIDER,
            "stream": True,
            "buffer_size": 150,
            "audio_format": "wav"
        }
        
        # ElevenLabs requires voice or voice_id at top level
        if VOICE_PROVIDER.lower() == "elevenlabs":
            synthesizer_config["voice_id"] = VOICE_ID
            synthesizer_config["provider_config"] = {
                "language": VOICE_LANGUAGE
            }
        else:
            # For other providers like polly
            synthesizer_config["provider_config"] = {
                "voice": VOICE_ID,
                "engine": "generative",
                "language": VOICE_LANGUAGE,
                "sampling_rate": "8000"
            }
        
        payload = {
            "agent_config": {
                "agent_name": AGENT_NAME,
                "agent_type": AGENT_TYPE,
                "tasks": [
                    {
                        "task_type": "conversation",
                        "tools_config": {
                            "llm_agent": {
                                "agent_type": "simple_llm_agent",
                                "agent_flow_type": "streaming",
                                "llm_config": {
                                    "provider": MODEL_PROVIDER,
                                    "family": MODEL_PROVIDER,
                                    "model": MODEL_NAME,
                                    "temperature": TEMPERATURE,
                                    "max_tokens": 500,
                                    "agent_flow_type": "streaming",
                                    "request_json": True,  # Enable JSON output for structured extraction
                                    "base_url": "https://api.openai.com/v1" if MODEL_PROVIDER == "openai" else None,
                                    "presence_penalty": 0,
                                    "frequency_penalty": 0,
                                    "top_p": 0.9,
                                    "min_p": 0.1,
                                    "top_k": 0,
                                    "summarization_details": None,
                                    "extraction_details": {
                                        "format": "json",
                                        "schema": EXTRACTION_SCHEMA
                                    }
                                }
                            },
                            "synthesizer": synthesizer_config,
                            "transcriber": {
                                "provider": "deepgram",
                                "model": "nova-2",
                                "language": "en-US",  # More specific language code
                                "stream": True,
                                "sampling_rate": 16000,
                                "encoding": "linear16",
                                "endpointing": 500,  # Increased from 100ms - less aggressive, better for accents
                                "smart_format": True,  # Enable smart formatting
                                "punctuate": True,  # Enable punctuation
                                "interim_results": True  # Get interim results for faster response
                            },
                            "input": {
                                "provider": "twilio",
                                "format": "wav"
                            },
                            "output": {
                                "provider": "twilio",
                                "format": "wav"
                            },
                            "api_tools": None
                        },
                        "toolchain": {
                            "execution": "parallel",
                            "pipelines": [
                                [
                                    "transcriber",
                                    "llm",
                                    "synthesizer"
                                ]
                            ]
                        },
                        "task_config": {
                            "hangup_after_silence": 10,
                            "incremental_delay": 400,
                            "number_of_words_for_interruption": 2,
                            "hangup_after_LLMCall": False,
                            "call_cancellation_prompt": None,
                            "backchanneling": False,
                            "backchanneling_message_gap": 5,
                            "backchanneling_start_delay": 5,
                            "ambient_noise": False,
                            "ambient_noise_track": "office-ambience",
                            "call_terminate": 300,
                            "voicemail": False,
                            "inbound_limit": -1,
                            "whitelist_phone_numbers": [],
                            "disallow_unknown_numbers": False
                        }
                    }
                ],
                "agent_welcome_message": INTRO_PROMPT
            },
            "agent_prompts": {
                "task_1": {
                    "system_prompt": SYSTEM_PROMPT
                }
            }
        }
        
        # Remove None values from payload
        def remove_none(obj):
            if isinstance(obj, dict):
                return {k: remove_none(v) for k, v in obj.items() if v is not None}
            elif isinstance(obj, list):
                return [remove_none(item) for item in obj]
            else:
                return obj
        
        payload = remove_none(payload)
        
        try:
            print(f"📤 Sending request to: {url}")
            print(f"📋 Payload structure: {json.dumps(payload, indent=2)[:500]}...")
            response = requests.post(url, headers=self.headers, json=payload)
            
            # Print response for debugging
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response: {response.text[:500]}")
            
            response.raise_for_status()
            result = response.json()
            self.agent_id = result.get("agent_id")
            print(f"✅ Agent created successfully!")
            print(f"Agent ID: {self.agent_id}")
            return result
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status Code: {e.response.status_code}")
                print(f"Response: {e.response.text}")
                try:
                    error_detail = e.response.json()
                    print(f"Error Details: {json.dumps(error_detail, indent=2)}")
                except:
                    pass
            raise
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating agent: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def make_call(
        self,
        phone_number: str,
        caller_id: str,
        candidate_name: str,
        interview_date: str,
        interview_time: str,
        alternative_slots: Optional[list] = None,
        scheduled_at: Optional[str] = None,
        position: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make an outbound call using the agent
        
        Args:
            phone_number: Phone number to call (E.164 format: +1234567890)
            caller_id: Caller ID number (E.164 format)
            candidate_name: Name of the candidate
            interview_date: Scheduled interview date (e.g., "Friday, the 12th of December")
            interview_time: Scheduled interview time (e.g., "10:00 A.M.")
            alternative_slots: Optional list of alternative time slots
            scheduled_at: Optional ISO format datetime for scheduled calls (e.g., "2025-08-21T10:35:00")
        
        Returns:
            Dictionary containing call execution details
        """
        if not self.agent_id:
            raise ValueError("Agent not created yet. Please call create_agent() first.")
        
        # Use the correct endpoint: /call (not /agent/{agent_id}/call)
        url = f"{self.base_url}/call"
        
        # Format times for natural speech (TTS-friendly format)
        formatted_time = format_time_for_speech(interview_time)
        formatted_datetime = format_datetime_for_speech(f"{interview_date} at {interview_time}")
        
        # Build user_data for context variables
        # Include both formatted (for speech) and original (for reference) times
        user_data = {
            "candidate_name": candidate_name,
            "interview_date": interview_date,
            "interview_time": interview_time,  # Original format
            "interview_time_formatted": formatted_time,  # Natural speech format
            "interview_datetime": f"{interview_date} at {interview_time}",  # Original
            "interview_datetime_formatted": formatted_datetime,  # Natural speech format
            "name": candidate_name,  
            "date": interview_date,  
            "time": formatted_time,  # Use formatted for speech
            "time_original": interview_time,  # Keep original for reference
            "position": position,
            # Original slot for structured extraction
            "original_slot": {
                "date": interview_date,  # Will be converted to YYYY-MM-DD by agent
                "time": interview_time,  # Original format like "10:00 A.M."
                "day_of_week": interview_date.split(',')[0] if ',' in interview_date else interview_date.split()[0]
            }
        }
        
        if alternative_slots:
            # Format alternative slots for natural speech
            formatted_slots = format_slots_for_speech(alternative_slots)
            user_data["alternative_slots"] = alternative_slots  # Original format
            user_data["alternative_slots_formatted"] = formatted_slots  # Natural speech format
        
        payload = {
            "agent_id": self.agent_id,
            "recipient_phone_number": phone_number,
            "user_data": user_data
        }
        
        # Only add from_phone_number if caller_id is provided
        # For Twilio, if omitted, it will use the default registered number
        if caller_id:
            payload["from_phone_number"] = caller_id
        
        # Add scheduled_at if provided
        if scheduled_at:
            payload["scheduled_at"] = scheduled_at
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            
            # Check for specific error messages in response
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', '')
                    
                    # Check for wallet balance issue
                    if 'wallet' in error_message.lower() or 'balance' in error_message.lower() or 'recharge' in error_message.lower():
                        error_msg = f"💰 WALLET BALANCE LOW: {error_message}"
                        print(f"❌ {error_msg}")
                        raise ValueError(error_msg)
                    
                    # Check for other common errors
                    if error_message:
                        print(f"❌ Bolna API Error: {error_message}")
                        raise ValueError(f"Bolna API Error: {error_message}")
                except (json.JSONDecodeError, ValueError):
                    # If JSON parsing fails or we already raised ValueError, continue with raise_for_status
                    pass
            
            response.raise_for_status()
            result = response.json()
            print(f"✅ Call initiated successfully!")
            print(f"Execution ID: {result.get('execution_id')}")
            return result
        except ValueError as e:
            # Re-raise ValueError (wallet balance or custom errors)
            raise
        except requests.exceptions.RequestException as e:
            error_msg = f"Error making call: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    if 'message' in error_data:
                        error_msg = f"Bolna API Error: {error_data['message']}"
                        if 'wallet' in error_data['message'].lower() or 'balance' in error_data['message'].lower():
                            error_msg = f"💰 WALLET BALANCE LOW: {error_data['message']}"
                except:
                    if e.response.text:
                        error_msg = f"Error: {e.response.text}"
            
            print(f"❌ {error_msg}")
            raise ValueError(error_msg)
    
    def get_execution_details(self, execution_id: str) -> Dict[str, Any]:
        """
        Get details of a call execution
        
        Args:
            execution_id: The execution ID from the call response
        
        Returns:
            Dictionary containing execution details including:
            - status, transcript, cost_breakdown
            - telephony_data (duration, recording_url, etc.)
            - extracted_data (if any data was extracted)
            - context_details
        """
        url = f"{self.base_url}/execution/{execution_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            # Handle both single execution and array response
            if isinstance(result, list) and len(result) > 0:
                return result[0]
            elif isinstance(result, dict) and 'data' in result:
                # Handle paginated response
                data = result['data']
                if isinstance(data, list) and len(data) > 0:
                    return data[0]
                return data
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching execution details: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def get_transcript(self, execution_id: str) -> str:
        """
        Get transcript from a call execution
        
        Args:
            execution_id: The execution ID from the call response
        
        Returns:
            Transcript string from the call
        """
        details = self.get_execution_details(execution_id)
        
        # Try different possible keys for transcript
        transcript = (
            details.get('transcript') or 
            details.get('conversation_transcript') or 
            details.get('call_transcript') or
            details.get('transcript_text') or
            ''
        )
        
        if transcript:
            print(f"📝 Found transcript ({len(transcript)} characters)")
        else:
            print(f"⚠️  No transcript found in execution details")
            print(f"   Available keys: {list(details.keys())}")
        
        return transcript
    
    def get_execution_logs(self, execution_id: str) -> Dict[str, Any]:
        """
        Get logs for a call execution
        
        Args:
            execution_id: The execution ID from the call response
        
        Returns:
            Dictionary containing execution logs with component data
        """
        url = f"{self.base_url}/execution/{execution_id}/logs"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching execution logs: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def list_executions(
        self, 
        agent_id: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        List call executions with pagination
        
        Args:
            agent_id: Optional agent ID to filter executions
            page_number: Page number (default: 1)
            page_size: Number of results per page (default: 10)
        
        Returns:
            Dictionary containing paginated execution list with:
            - data: List of executions
            - page_number, page_size, total, has_more
        """
        url = f"{self.base_url}/execution"
        params = {
            "page_number": page_number,
            "page_size": page_size
        }
        
        if agent_id:
            params["agent_id"] = agent_id
        elif self.agent_id:
            params["agent_id"] = self.agent_id
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error listing executions: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def get_agent(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get details of a specific agent
        
        Args:
            agent_id: The agent ID (uses self.agent_id if not provided)
        
        Returns:
            Dictionary containing agent details including:
            - id, agent_name, agent_type, agent_status
            - tasks configuration
            - agent_prompts
        """
        agent_id = agent_id or self.agent_id
        if not agent_id:
            raise ValueError("Agent ID is required")
        
        url = f"{self.base_url}/v2/agent/{agent_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            
            # Handle both single agent and array response
            if isinstance(result, list) and len(result) > 0:
                return result[0]
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching agent details: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def list_agents(self) -> Dict[str, Any]:
        """
        List all agents associated with the API key
        
        Returns:
            Dictionary containing list of agents
        """
        url = f"{self.base_url}/agent"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error listing agents: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise


def main():
    """Example usage of the Bolna Agent"""
    
    # Initialize the agent (API key loaded from .env file)
    try:
        agent = BolnaAgent()
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    # Create the agent
    print("\n📞 Creating voice calling agent...")
    agent.create_agent()
    
    # Example: Make a call
    print("\n📞 Making a test call...")
    print("(Uncomment the code below and fill in the details to make a call)")
    
    # Uncomment and fill in the details to make a call:
    """
    result = agent.make_call(
        phone_number="+1234567890",  # Candidate's phone number
        caller_id="+0987654321",     # Your caller ID
        candidate_name="John Doe",
        interview_date="Friday, the 12th of December",
        interview_time="10:00 A.M.",
        alternative_slots=[
            "Monday, the 15th of December, at 2:00 P.M.",
            "Tuesday, the 16th of December, at 11:00 A.M.",
            "Wednesday, the 17th of December, at 3:00 P.M."
        ]
    )
    
    execution_id = result.get("execution_id")
    if execution_id:
        print(f"\n📊 Fetching call details...")
        details = agent.get_execution_details(execution_id)
        print(json.dumps(details, indent=2))
    """


if __name__ == "__main__":
    main()

