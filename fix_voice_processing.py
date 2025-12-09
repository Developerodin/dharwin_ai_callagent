"""
Fix Voice Processing Issues
Updates agent configuration to improve voice recognition and processing
"""

import requests
import json
import os
from config import BOLNA_API_BASE, BOLNA_API_KEY, AGENT_ID

def get_current_agent():
    """Get current agent configuration"""
    url = f"{BOLNA_API_BASE}/v2/agent/{AGENT_ID}"
    headers = {
        "Authorization": f"Bearer {BOLNA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching agent: {e}")
        return None

def update_agent_transcriber(agent_data):
    """Update transcriber configuration to improve voice processing"""
    
    # Find the conversation task
    tasks = agent_data.get('tasks', [])
    conversation_task = None
    for task in tasks:
        if task.get('task_type') == 'conversation':
            conversation_task = task
            break
    
    if not conversation_task:
        print("❌ Conversation task not found")
        return None
    
    tools_config = conversation_task.get('tools_config', {})
    
    # Update transcriber configuration for better voice processing
    transcriber_config = {
        "provider": "deepgram",
        "model": "nova-2",  # Use latest model for better accuracy
        "language": "en-US",  # More specific language code
        "stream": True,
        "sampling_rate": 16000,
        "encoding": "linear16",
        "endpointing": 500,  # Increased from 100ms to 500ms - less aggressive
        "smart_format": True,  # Enable smart formatting
        "punctuate": True,  # Enable punctuation
        "diarize": False,  # Disable speaker diarization for now
        "interim_results": True,  # Get interim results for faster response
        "keywords": [],  # Can add keywords if needed
        "language_detection": False,  # Keep English for now, enable if multi-language needed
    }
    
    tools_config['transcriber'] = transcriber_config
    
    # Update task config for better voice handling
    task_config = conversation_task.get('task_config', {})
    task_config.update({
        "hangup_after_silence": 15,  # Increased from 10 to 15 seconds
        "incremental_delay": 400,  # Keep reasonable delay
        "number_of_words_for_interruption": 1,  # Reduced from 2 - more responsive
        "trigger_user_online_message_after": 8,  # Reduced from 10 - check sooner
        "language_detection_turns": None,  # Disable auto-detection for now
        "generate_precise_transcript": True,  # Enable precise transcript generation
    })
    
    conversation_task['task_config'] = task_config
    conversation_task['tools_config'] = tools_config
    
    return agent_data

def update_agent(agent_data):
    """Update agent with new configuration"""
    url = f"{BOLNA_API_BASE}/v2/agent/{AGENT_ID}"
    headers = {
        "Authorization": f"Bearer {BOLNA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare update payload (only send what needs updating)
    payload = {
        "tasks": agent_data.get('tasks', []),
        "agent_prompts": agent_data.get('agent_prompts', {})
    }
    
    try:
        print(f"📤 Updating agent {AGENT_ID}...")
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error updating agent: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None

def main():
    print(f"{'='*70}")
    print(f"🔧 Fix Voice Processing Configuration")
    print(f"{'='*70}\n")
    
    if not AGENT_ID:
        print("❌ AGENT_ID not found in config")
        print("   Set AGENT_ID in .env file or config.py")
        return
    
    if not BOLNA_API_KEY:
        print("❌ BOLNA_API_KEY not found")
        return
    
    print(f"📋 Agent ID: {AGENT_ID}\n")
    
    # Get current agent
    print("1️⃣  Fetching current agent configuration...")
    agent_data = get_current_agent()
    
    if not agent_data:
        print("❌ Could not fetch agent configuration")
        return
    
    print("✅ Agent configuration fetched\n")
    
    # Update transcriber
    print("2️⃣  Updating transcriber configuration...")
    updated_agent = update_agent_transcriber(agent_data)
    
    if not updated_agent:
        print("❌ Could not update configuration")
        return
    
    print("✅ Configuration updated:")
    transcriber = updated_agent['tasks'][0]['tools_config']['transcriber']
    print(f"   Model: {transcriber.get('model')}")
    print(f"   Language: {transcriber.get('language')}")
    print(f"   Endpointing: {transcriber.get('endpointing')}ms")
    print(f"   Smart Format: {transcriber.get('smart_format')}")
    print(f"   Interim Results: {transcriber.get('interim_results')}")
    print()
    
    # Update agent
    print("3️⃣  Saving updated configuration to Bolna...")
    result = update_agent(updated_agent)
    
    if result:
        print("✅ Agent updated successfully!")
        print()
        print(f"{'='*70}")
        print(f"📊 Changes Applied")
        print(f"{'='*70}")
        print("✅ Transcriber model: nova-2 (latest)")
        print("✅ Language: en-US (more specific)")
        print("✅ Endpointing: 500ms (less aggressive)")
        print("✅ Smart formatting: Enabled")
        print("✅ Interim results: Enabled")
        print("✅ Precise transcripts: Enabled")
        print("✅ Hangup after silence: 15s (increased)")
        print()
        print("💡 Test the agent with a new call to see improvements!")
        print(f"{'='*70}\n")
    else:
        print("❌ Failed to update agent")

if __name__ == '__main__':
    main()

