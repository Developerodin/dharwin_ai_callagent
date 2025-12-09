"""
View webhook logs saved by Flask server
"""

import json
import os
from datetime import datetime

def view_webhook_logs():
    """View saved webhook logs"""
    log_file = 'webhook_logs.json'
    
    if not os.path.exists(log_file):
        print("\n" + "="*70)
        print("📭 No Webhook Logs Found")
        print("="*70)
        print()
        print("ℹ️  Webhook logs are saved when webhooks are received.")
        print("   The webhook endpoint logs all payloads automatically.")
        print()
        print("💡 To see webhook data:")
        print("   1. Check Flask server terminal (where api_server.py is running)")
        print("      - Flask logs show all webhook payloads in real-time")
        print("   2. View ngrok dashboard: http://localhost:4040")
        print("      - Shows all HTTP requests including webhook payloads")
        print("   3. Wait for a call to complete - webhook will be sent automatically")
        print()
        return
    
    with open(log_file, 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    print("\n" + "="*70)
    print("📥 Webhook Logs - Data Received from Bolna AI")
    print("="*70)
    print()
    print(f"✅ Found {len(logs)} webhook log(s)\n")
    
    for i, log_entry in enumerate(reversed(logs), 1):
        timestamp = log_entry.get('timestamp', 'N/A')
        payload = log_entry.get('payload', {})
        
        print(f"Webhook #{i} - {timestamp}")
        print("-" * 70)
        print(f"\n📦 Payload:")
        print(json.dumps(payload, indent=2))
        
        # Extract key information
        exec_id = payload.get('execution_id') or payload.get('executionId')
        status = payload.get('status')
        transcript = payload.get('transcript') or payload.get('conversation_transcript', '')
        extracted_data = payload.get('extracted_data', {})
        recipient = payload.get('recipient_phone_number')
        
        print(f"\n📋 Key Information:")
        if exec_id:
            print(f"   Execution ID: {exec_id}")
        if status:
            print(f"   Status: {status}")
        if recipient:
            print(f"   Recipient: {recipient}")
        if transcript:
            print(f"   Transcript: {transcript[:300]}...")
        if extracted_data:
            print(f"   Extracted Data: {json.dumps(extracted_data, indent=4)}")
        
        print()
        print("="*70)
        print()

if __name__ == "__main__":
    view_webhook_logs()

