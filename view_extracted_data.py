"""
View extracted data from webhook logs
Shows the structured extraction data (call_outcome, original_slot, final_slot, notes)
"""

import json
import os
from datetime import datetime

def view_extracted_data(limit=10):
    """View extracted data from webhook logs"""
    webhook_log_file = 'webhook_logs.json'
    
    if not os.path.exists(webhook_log_file):
        print(f"❌ {webhook_log_file} not found")
        print("   This file is created when webhooks are received.")
        return
    
    try:
        with open(webhook_log_file, 'r', encoding='utf-8') as f:
            webhook_logs = json.load(f)
        
        if not webhook_logs:
            print("📭 No webhook logs found")
            return
        
        print(f"\n{'='*70}")
        print(f"📊 Extracted Data from Webhook Logs")
        print(f"{'='*70}\n")
        print(f"Total logs: {len(webhook_logs)}\n")
        
        # Filter logs with extracted_data
        logs_with_extraction = [
            log for log in webhook_logs 
            if log.get('payload', {}).get('extracted_data', {}).get('call_outcome')
        ]
        
        if not logs_with_extraction:
            print("⚠️  No logs with structured extracted_data found")
            print("   Showing all logs instead:\n")
            logs_with_extraction = webhook_logs[-limit:]
        
        # Show recent logs
        for i, log in enumerate(logs_with_extraction[-limit:], 1):
            payload = log.get('payload', {})
            timestamp = log.get('timestamp', 'Unknown')
            execution_id = (
                payload.get('execution_id') or 
                payload.get('executionId') or 
                payload.get('id') or 
                'Unknown'
            )
            
            extracted_data = payload.get('extracted_data', {})
            
            print(f"{'─'*70}")
            print(f"📋 Log #{i}")
            print(f"   Timestamp: {timestamp}")
            print(f"   Execution ID: {execution_id}")
            print(f"   Status: {payload.get('status', 'Unknown')}")
            
            if extracted_data and extracted_data.get('call_outcome'):
                print(f"\n   ✅ STRUCTURED EXTRACTION DATA:")
                print(f"      Call Outcome: {extracted_data.get('call_outcome')}")
                
                original_slot = extracted_data.get('original_slot')
                if original_slot:
                    print(f"      Original Slot:")
                    print(f"         Date: {original_slot.get('date')}")
                    print(f"         Time: {original_slot.get('time')}")
                    print(f"         Day: {original_slot.get('day_of_week')}")
                
                final_slot = extracted_data.get('final_slot')
                if final_slot:
                    print(f"      Final Slot:")
                    print(f"         Date: {final_slot.get('date')}")
                    print(f"         Time: {final_slot.get('time')}")
                    print(f"         Day: {final_slot.get('day_of_week')}")
                elif extracted_data.get('call_outcome') == 'REJECTED':
                    print(f"      Final Slot: null (REJECTED)")
                
                notes = extracted_data.get('notes')
                if notes:
                    print(f"      Notes: {notes}")
                
                print(f"\n      Full extracted_data:")
                print(f"      {json.dumps(extracted_data, indent=6)}")
            else:
                print(f"   ⚠️  No structured extracted_data found in this log")
                if extracted_data:
                    print(f"   Available keys: {list(extracted_data.keys())}")
            
            print()
        
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"❌ Error reading webhook logs: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    view_extracted_data(limit)

