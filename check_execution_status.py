"""
Quick script to check execution status and see webhook data
"""

import json
import os
from fetch_execution_details import fetch_execution_details, format_execution_details

def main():
    print("\n" + "="*70)
    print("🔍 Check Execution Status & Webhook Data")
    print("="*70)
    print()
    
    # Check execution mappings
    mapping_file = 'execution_mapping.json'
    if not os.path.exists(mapping_file):
        print("❌ No execution mappings found")
        print("   No calls have been initiated yet")
        return
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        mappings = json.load(f)
    
    if not mappings:
        print("❌ No execution mappings found")
        return
    
    print(f"✅ Found {len(mappings)} execution(s)\n")
    
    # Show all executions
    for i, (exec_id, mapping) in enumerate(mappings.items(), 1):
        print(f"{i}. Execution ID: {exec_id}")
        print(f"   Candidate ID: {mapping.get('candidate_id')}")
        print(f"   Phone: {mapping.get('phone')}")
        print(f"   Created: {mapping.get('created_at')}")
        print()
    
    # Fetch details for the latest execution
    latest_exec_id = list(mappings.keys())[-1]
    print(f"📊 Fetching details for latest execution: {latest_exec_id}\n")
    
    details = fetch_execution_details(latest_exec_id)
    
    if details:
        print(format_execution_details(details))
        
        # Check if webhook should have updated
        status = details.get('status', '').lower()
        if status in ['completed', 'ended', 'stopped']:
            print("✅ Call is completed - webhook should have been sent")
            print("   Check Flask logs for webhook processing")
        elif status in ['failed', 'error', 'cancelled']:
            print("⚠️  Call failed/cancelled - webhook should have been sent")
            print("   Candidate status should be reset to 'pending'")
        else:
            print(f"⏳ Call status: {status} (still in progress)")
            print("   Webhook will be sent when call completes")
    else:
        print("❌ Could not fetch execution details")
        print("   Check your BOLNA_API_KEY in .env file")

if __name__ == "__main__":
    main()

