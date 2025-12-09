"""
Fetch and display execution details from Bolna AI Execution API
This script retrieves call execution data including status, transcript, and telephony data
"""

import requests
import json
import sys
from datetime import datetime
from config import BOLNA_API_BASE, BOLNA_API_KEY

def fetch_execution_details(execution_id: str):
    """
    Fetch execution details from Bolna AI API
    
    Args:
        execution_id: The execution ID to fetch details for
    
    Returns:
        Dictionary containing execution details
    """
    if not BOLNA_API_KEY:
        print("❌ BOLNA_API_KEY not found in .env file")
        print("   Please set BOLNA_API_KEY in your .env file")
        return None
    
    url = f"{BOLNA_API_BASE}/execution/{execution_id}"
    headers = {
        "Authorization": f"Bearer {BOLNA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📡 Fetching execution details for: {execution_id}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        # Handle different response formats
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        elif isinstance(result, dict) and 'data' in result:
            data = result['data']
            if isinstance(data, list) and len(data) > 0:
                return data[0]
            return data
        return result
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def format_execution_details(details: dict):
    """Format execution details for display"""
    if not details:
        return "No details available"
    
    output = []
    output.append("="*70)
    output.append("📊 Execution Details")
    output.append("="*70)
    output.append("")
    
    # Basic Information
    output.append("📋 Basic Information:")
    output.append(f"   Execution ID: {details.get('execution_id', details.get('id', 'N/A'))}")
    output.append(f"   Status: {details.get('status', 'N/A')}")
    output.append(f"   Created At: {details.get('created_at', 'N/A')}")
    output.append(f"   Updated At: {details.get('updated_at', details.get('modified_at', 'N/A'))}")
    output.append("")
    
    # Agent Information
    if 'agent_id' in details:
        output.append("🤖 Agent Information:")
        output.append(f"   Agent ID: {details.get('agent_id', 'N/A')}")
        output.append("")
    
    # Telephony Data
    telephony_data = details.get('telephony_data', {})
    if telephony_data:
        output.append("📞 Telephony Data:")
        output.append(f"   Duration: {telephony_data.get('duration', 'N/A')} seconds")
        output.append(f"   Call Status: {telephony_data.get('call_status', 'N/A')}")
        output.append(f"   Recording URL: {telephony_data.get('recording_url', 'N/A')}")
        if 'caller_id' in telephony_data:
            output.append(f"   Caller ID: {telephony_data.get('caller_id', 'N/A')}")
        if 'recipient_phone_number' in telephony_data:
            output.append(f"   Recipient: {telephony_data.get('recipient_phone_number', 'N/A')}")
        output.append("")
    
    # Transcript
    transcript = (
        details.get('transcript') or 
        details.get('conversation_transcript') or 
        details.get('call_transcript') or
        details.get('transcript_text')
    )
    if transcript:
        output.append("📝 Transcript:")
        output.append("   " + "\n   ".join(transcript[:1000].split("\n")))
        if len(transcript) > 1000:
            output.append(f"   ... (truncated, {len(transcript)} total characters)")
        output.append("")
    
    # Extracted Data
    extracted_data = details.get('extracted_data', {})
    if extracted_data:
        output.append("📊 Extracted Data:")
        output.append(json.dumps(extracted_data, indent=4))
        output.append("")
    
    # Cost Breakdown
    cost_breakdown = details.get('cost_breakdown', {})
    if cost_breakdown:
        output.append("💰 Cost Breakdown:")
        output.append(json.dumps(cost_breakdown, indent=4))
        output.append("")
    
    # Context Details
    context_details = details.get('context_details', {})
    if context_details:
        output.append("📋 Context Details:")
        output.append(json.dumps(context_details, indent=4))
        output.append("")
    
    # User Data
    user_data = details.get('user_data', {})
    if user_data:
        output.append("👤 User Data:")
        output.append(json.dumps(user_data, indent=4))
        output.append("")
    
    # All Keys (for debugging)
    output.append("🔍 All Available Keys:")
    output.append(f"   {', '.join(details.keys())}")
    output.append("")
    output.append("="*70)
    
    return "\n".join(output)

def get_execution_from_mapping():
    """Get execution IDs from execution_mapping.json"""
    try:
        with open('execution_mapping.json', 'r', encoding='utf-8') as f:
            mappings = json.load(f)
        return list(mappings.keys())
    except:
        return []

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fetch execution details from Bolna AI Execution API"
    )
    parser.add_argument(
        '--execution-id',
        type=str,
        help='Execution ID to fetch (e.g., exec_1234567890)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all execution IDs from execution_mapping.json'
    )
    parser.add_argument(
        '--latest',
        action='store_true',
        help='Fetch details for the latest execution from mapping'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output raw JSON instead of formatted text'
    )
    
    args = parser.parse_args()
    
    # List execution IDs
    if args.list:
        print("\n📋 Execution IDs from execution_mapping.json:")
        print("="*70)
        execution_ids = get_execution_from_mapping()
        if execution_ids:
            for i, exec_id in enumerate(execution_ids, 1):
                print(f"{i}. {exec_id}")
        else:
            print("No execution IDs found")
        print()
        return
    
    # Get execution ID
    execution_id = args.execution_id
    
    if not execution_id:
        if args.latest:
            # Get latest from mapping
            execution_ids = get_execution_from_mapping()
            if execution_ids:
                execution_id = execution_ids[-1]
                print(f"📋 Using latest execution ID: {execution_id}\n")
            else:
                print("❌ No execution IDs found in execution_mapping.json")
                print("   Use --execution-id to specify an execution ID")
                return
        else:
            # Show help
            execution_ids = get_execution_from_mapping()
            if execution_ids:
                print("\n📋 Available Execution IDs:")
                for i, exec_id in enumerate(execution_ids, 1):
                    print(f"   {i}. {exec_id}")
                print()
                print("Usage:")
                print("  python fetch_execution_details.py --execution-id EXEC_ID")
                print("  python fetch_execution_details.py --latest")
                print("  python fetch_execution_details.py --list")
            else:
                print("❌ No execution ID provided")
                print("Usage: python fetch_execution_details.py --execution-id EXEC_ID")
            return
    
    # Fetch details
    details = fetch_execution_details(execution_id)
    
    if details:
        if args.json:
            print(json.dumps(details, indent=2))
        else:
            print(format_execution_details(details))
    else:
        print("❌ Failed to fetch execution details")
        sys.exit(1)

if __name__ == "__main__":
    main()

