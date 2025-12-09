"""
View all stored webhook data from data/webhook_data.json
Shows complete webhook payloads, extracted_data, transcripts, and more
"""

import json
import os
from datetime import datetime

def view_webhook_data(execution_id: str = None, limit: int = 10, show_full: bool = False):
    """
    View stored webhook data
    
    Args:
        execution_id: Specific execution ID to view (optional)
        limit: Number of recent entries to show
        show_full: Show full payload (default: False, shows summary)
    """
    webhook_data_file = 'data/webhook_data.json'
    
    if not os.path.exists(webhook_data_file):
        print(f"❌ {webhook_data_file} not found")
        print("   This file is created when webhooks are received.")
        return
    
    try:
        with open(webhook_data_file, 'r', encoding='utf-8') as f:
            webhook_data = json.load(f)
        
        # If specific execution_id requested
        if execution_id:
            if execution_id in webhook_data:
                entry = webhook_data[execution_id]
                print(f"\n{'='*70}")
                print(f"📊 Webhook Data for Execution: {execution_id}")
                print(f"{'='*70}\n")
                print_json_entry(entry, show_full=True)
            else:
                print(f"❌ Execution ID '{execution_id}' not found")
                print(f"   Available execution IDs: {list(k for k in webhook_data.keys() if k != 'all_webhooks')[:10]}")
            return
        
        # Show recent entries from chronological list
        all_webhooks = webhook_data.get('all_webhooks', [])
        
        if not all_webhooks:
            print("📭 No webhook data found")
            return
        
        print(f"\n{'='*70}")
        print(f"📊 Stored Webhook Data")
        print(f"{'='*70}\n")
        print(f"Total executions: {len([k for k in webhook_data.keys() if k != 'all_webhooks'])}")
        print(f"Showing last {min(limit, len(all_webhooks))} entries:\n")
        
        for i, entry_summary in enumerate(all_webhooks[:limit], 1):
            exec_id = entry_summary['execution_id']
            entry = webhook_data.get(exec_id, {})
            
            print(f"{'─'*70}")
            print(f"📋 Entry #{i}")
            print(f"   Execution ID: {exec_id}")
            print(f"   Candidate ID: {entry_summary.get('candidate_id', 'N/A')}")
            print(f"   Timestamp: {entry_summary.get('timestamp', 'N/A')}")
            print(f"   Status: {entry_summary.get('status', 'N/A')}")
            
            if entry:
                print_json_entry(entry, show_full=show_full)
            print()
        
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"❌ Error reading webhook data: {e}")
        import traceback
        traceback.print_exc()

def print_json_entry(entry: dict, show_full: bool = False):
    """Print formatted entry"""
    print(f"   Received At: {entry.get('received_at', 'N/A')}")
    
    # Show extracted_data
    extracted_data = entry.get('extracted_data', {})
    if extracted_data:
        print(f"\n   ✅ EXTRACTED DATA:")
        call_outcome = extracted_data.get('call_outcome')
        if call_outcome:
            print(f"      Call Outcome: {call_outcome}")
            
            original_slot = extracted_data.get('original_slot')
            if original_slot:
                print(f"      Original Slot: {original_slot.get('day_of_week')}, {original_slot.get('date')} at {original_slot.get('time')}")
            
            final_slot = extracted_data.get('final_slot')
            if final_slot:
                print(f"      Final Slot: {final_slot.get('day_of_week')}, {final_slot.get('date')} at {final_slot.get('time')}")
            elif call_outcome == 'REJECTED':
                print(f"      Final Slot: null (REJECTED)")
            
            notes = extracted_data.get('notes')
            if notes:
                print(f"      Notes: {notes}")
        else:
            print(f"      {json.dumps(extracted_data, indent=8)}")
    
    # Show transcript preview
    transcript = entry.get('transcript', '')
    if transcript:
        preview = transcript[:200] + '...' if len(transcript) > 200 else transcript
        print(f"\n   📝 Transcript ({len(transcript)} chars):")
        print(f"      {preview}")
    
    # Show phone number
    phone = entry.get('recipient_phone_number')
    if phone:
        print(f"\n   📞 Phone: {phone}")
    
    # Show telephony data
    telephony = entry.get('telephony_data', {})
    if telephony:
        duration = telephony.get('duration')
        recording_url = telephony.get('recording_url')
        if duration or recording_url:
            print(f"\n   📊 Telephony Data:")
            if duration:
                print(f"      Duration: {duration} seconds")
            if recording_url:
                print(f"      Recording: {recording_url}")
    
    # Show full payload if requested
    if show_full:
        print(f"\n   📦 Full Payload:")
        print(f"      {json.dumps(entry.get('payload', {}), indent=8)}")

if __name__ == '__main__':
    import sys
    
    execution_id = None
    limit = 10
    show_full = False
    
    # Parse arguments
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--execution-id' or args[i] == '-e':
            execution_id = args[i + 1]
            i += 2
        elif args[i] == '--limit' or args[i] == '-l':
            limit = int(args[i + 1])
            i += 2
        elif args[i] == '--full' or args[i] == '-f':
            show_full = True
            i += 1
        else:
            i += 1
    
    view_webhook_data(execution_id=execution_id, limit=limit, show_full=show_full)
