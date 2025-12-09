"""
Update agent system prompt and welcome message
This script updates the agent configuration in Bolna Dashboard with the fixed prompt
"""

import requests
import json
import os
from config import BOLNA_API_BASE, BOLNA_API_KEY, AGENT_ID
from system_prompt import SYSTEM_PROMPT, INTRO_PROMPT

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

def update_agent_prompts(agent_data):
    """Update agent prompts with fixed system prompt"""
    
    # Update agent_welcome_message
    agent_data['agent_welcome_message'] = INTRO_PROMPT
    
    # Update agent_prompts
    agent_data['agent_prompts'] = {
        'task_1': {
            'system_prompt': SYSTEM_PROMPT
        }
    }
    
    return agent_data

def update_agent(agent_data):
    """Update agent with new prompts"""
    url = f"{BOLNA_API_BASE}/v2/agent/{AGENT_ID}"
    headers = {
        "Authorization": f"Bearer {BOLNA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepare update payload
    payload = {
        "agent_welcome_message": agent_data.get('agent_welcome_message'),
        "agent_prompts": agent_data.get('agent_prompts')
    }
    
    try:
        print(f"📤 Updating agent {AGENT_ID} with fixed prompts...")
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
    print(f"🔧 Update Agent System Prompt")
    print(f"{'='*70}\n")
    
    if not AGENT_ID:
        print("❌ AGENT_ID not found in config")
        print("   Set AGENT_ID in .env file or config.py")
        return
    
    if not BOLNA_API_KEY:
        print("❌ BOLNA_API_KEY not found")
        return
    
    print(f"📋 Agent ID: {AGENT_ID}\n")
    print(f"📋 New Welcome Message: {INTRO_PROMPT}\n")
    
    # Get current agent
    print("1️⃣  Fetching current agent configuration...")
    agent_data = get_current_agent()
    
    if not agent_data:
        print("❌ Could not fetch agent configuration")
        return
    
    print("✅ Agent configuration fetched\n")
    
    # Update prompts
    print("2️⃣  Updating with fixed prompts...")
    updated_agent = update_agent_prompts(agent_data)
    
    print("✅ Prompts updated:")
    print(f"   Welcome Message: {updated_agent.get('agent_welcome_message')}")
    print(f"   System Prompt: Updated with name verification requirements")
    print()
    
    # Update agent
    print("3️⃣  Saving updated prompts to Bolna...")
    result = update_agent(updated_agent)
    
    if result:
        print("✅ Agent prompts updated successfully!")
        print()
        print(f"{'='*70}")
        print(f"📊 Changes Applied")
        print(f"{'='*70}")
        print("✅ Welcome message updated")
        print("✅ System prompt updated with mandatory name verification")
        print("✅ Wrong person handling fixed (won't auto-decline)")
        print("✅ Decline confirmation required")
        print()
        print("💡 Test the agent with a new call:")
        print("   - Agent should ask for name verification first")
        print("   - Agent should state candidate's name")
        print("   - Wrong person should NOT be marked as declined")
        print(f"{'='*70}\n")
    else:
        print("❌ Failed to update agent")
        print()
        print("💡 Manual Update Required:")
        print("   1. Go to: https://platform.bolna.ai/")
        print("   2. Navigate to your agent settings")
        print("   3. Update System Prompt with the content from system_prompt.py")
        print("   4. Update Welcome Message to: 'Hello, this is Ava calling from Dharwin.'")

if __name__ == '__main__':
    main()

