"""
Check what webhook data was processed and stored
"""

import json
import os
from datetime import datetime

def check_candidate_updates():
    """Check candidate status changes"""
    candidates_file = 'data/candidates.json'
    if os.path.exists(candidates_file):
        with open(candidates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('candidates', [])
    return []

def check_execution_mappings():
    """Check execution mappings"""
    mapping_file = 'execution_mapping.json'
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def main():
    print("\n" + "="*70)
    print("📊 Webhook Data Analysis")
    print("="*70)
    print()
    
    # Check execution mappings
    print("1️⃣ Execution Mappings (Calls Made)")
    print("-" * 70)
    mappings = check_execution_mappings()
    if mappings:
        print(f"✅ Found {len(mappings)} execution(s):")
        for i, (exec_id, mapping) in enumerate(mappings.items(), 1):
            print(f"\n   {i}. Execution ID: {exec_id}")
            print(f"      Candidate ID: {mapping.get('candidate_id')}")
            print(f"      Phone: {mapping.get('phone')}")
            print(f"      Created: {mapping.get('created_at')}")
    else:
        print("⚠️  No execution mappings found")
    print()
    
    # Check candidate statuses
    print("2️⃣ Candidate Status Updates")
    print("-" * 70)
    candidates = check_candidate_updates()
    if candidates:
        print(f"✅ Found {len(candidates)} candidate(s):")
        for cand in candidates:
            status_icon = {
                'pending': '⏳',
                'calling': '📞',
                'confirmed': '✅',
                'declined': '❌',
                'rescheduled': '🔄'
            }.get(cand['status'], '❓')
            
            print(f"\n   {status_icon} {cand['name']} (ID: {cand['id']})")
            print(f"      Status: {cand['status']}")
            print(f"      Phone: {cand['phone']}")
            
            # Check if status was updated by webhook
            if cand['status'] != 'pending' and cand['id'] == 1:
                print(f"      ✅ Status updated (likely by webhook)")
    print()
    
    # Analysis
    print("="*70)
    print("📋 Analysis")
    print("="*70)
    print()
    
    candidate_1 = next((c for c in candidates if c['id'] == 1), None)
    if candidate_1:
        if candidate_1['status'] == 'pending':
            print("ℹ️  Candidate 1 status: 'pending'")
            print("   This could mean:")
            print("   - Webhook received and processed (call failed/cancelled)")
            print("   - Webhook reset status after call ended")
            print("   - Status was manually reset")
        elif candidate_1['status'] in ['confirmed', 'declined', 'rescheduled']:
            print(f"✅ Candidate 1 status: '{candidate_1['status']}'")
            print("   Webhook successfully processed and updated candidate!")
        elif candidate_1['status'] == 'calling':
            print("⏳ Candidate 1 status: 'calling'")
            print("   Call is still in progress - waiting for webhook")
    
    print()
    print("💡 To see webhook payloads:")
    print("   1. Check Flask server terminal logs (where api_server.py is running)")
    print("   2. View ngrok dashboard: http://localhost:4040")
    print("   3. Flask logs will show webhook payload details")
    print()
    print("📝 Latest execution IDs that should receive webhooks:")
    for exec_id in list(mappings.keys())[-3:]:
        print(f"   - {exec_id}")
    print()

if __name__ == "__main__":
    main()

