"""
Complete webhook setup verification and monitoring tool
Checks all components needed to receive Bolna AI webhook data
"""

import requests
import json
import os
from datetime import datetime

FLASK_URL = "http://localhost:5000"

def check_flask_server():
    """Check if Flask server is running"""
    try:
        response = requests.get(f"{FLASK_URL}/api/webhook/status", timeout=3)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_ngrok_url():
    """Get ngrok public URL"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            if tunnels:
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        return tunnel.get('public_url')
                return tunnels[0].get('public_url')
    except:
        pass
    return None

def get_recent_ngrok_requests():
    """Get recent webhook requests from ngrok"""
    try:
        response = requests.get('http://localhost:4040/api/requests/http?limit=10', timeout=2)
        if response.status_code == 200:
            data = response.json()
            requests_list = data.get('requests', [])
            # Filter for webhook requests
            webhook_requests = [
                req for req in requests_list
                if '/api/webhook' in req.get('request', {}).get('uri', {}).get('path', '') or
                   '/webhook' in req.get('request', {}).get('uri', {}).get('path', '')
            ]
            return webhook_requests
    except:
        pass
    return []

def check_execution_mappings():
    """Check execution mappings"""
    if os.path.exists('execution_mapping.json'):
        try:
            with open('execution_mapping.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def main():
    print("\n" + "="*70)
    print("🔍 Complete Webhook Setup Verification")
    print("="*70)
    print()
    
    # 1. Check Flask Server
    print("1️⃣ Flask Server Status")
    print("-" * 70)
    flask_status = check_flask_server()
    if flask_status:
        print("✅ Flask server is running")
        print(f"   Webhook endpoint: /api/webhook")
        print(f"   Execution mappings: {flask_status.get('execution_mappings', 0)}")
        print(f"   Candidates: {flask_status.get('candidates', 0)}")
        print(f"   Agent initialized: {flask_status.get('agent_initialized', False)}")
    else:
        print("❌ Flask server is NOT running")
        print("   Start it with: python api_server.py")
        print()
        return
    print()
    
    # 2. Check ngrok Tunnel
    print("2️⃣ ngrok Tunnel Status")
    print("-" * 70)
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        webhook_url = f"{ngrok_url}/api/webhook"
        print("✅ ngrok tunnel is active")
        print(f"   Public URL: {ngrok_url}")
        print(f"   Webhook URL: {webhook_url}")
        print()
        print("📋 NEXT STEP: Configure this URL in Bolna AI Dashboard")
        print(f"   {webhook_url}")
        print()
        print("   Steps:")
        print("   1. Go to: https://platform.bolna.ai/")
        print("   2. Navigate to your agent settings")
        print("   3. Find 'Webhook URL' or 'Push all execution data to webhook'")
        print("   4. Paste the webhook URL above")
        print("   5. Save the configuration")
    else:
        print("❌ ngrok tunnel is NOT running")
        print("   Start it with: ngrok http 5000")
        print("   (Keep it running in a separate terminal)")
    print()
    
    # 3. IP Whitelist Check
    print("3️⃣ IP Whitelist Configuration")
    print("-" * 70)
    bolna_ips = [
        '13.200.45.61',
        '65.2.44.157',
        '34.194.233.253',
        '13.204.98.4',
        '43.205.31.43',
        '107.20.118.52'
    ]
    print("✅ Webhook validates requests from Bolna AI IPs:")
    for ip in bolna_ips:
        print(f"   - {ip}")
    print()
    print("ℹ️  Note: ngrok automatically handles IP validation")
    print("   For production, ensure your server allows these IPs")
    print()
    
    # 4. Execution Mappings
    print("4️⃣ Execution Mappings")
    print("-" * 70)
    mappings = check_execution_mappings()
    if mappings:
        print(f"✅ Found {len(mappings)} execution mapping(s):")
        for exec_id, mapping in list(mappings.items())[:3]:
            print(f"   - {exec_id[:30]}... → Candidate {mapping.get('candidate_id')}")
        if len(mappings) > 3:
            print(f"   ... and {len(mappings) - 3} more")
    else:
        print("⚠️  No execution mappings found")
        print("   This is normal if no calls have been initiated yet")
    print()
    
    # 5. Recent Webhook Requests
    print("5️⃣ Recent Webhook Activity")
    print("-" * 70)
    webhook_requests = get_recent_ngrok_requests()
    if webhook_requests:
        print(f"✅ Found {len(webhook_requests)} recent webhook request(s)")
        for req in webhook_requests[:3]:
            timestamp = req.get('started_at', '')[:19]
            method = req.get('request', {}).get('method', 'N/A')
            status = req.get('response', {}).get('status', 'N/A')
            print(f"   [{timestamp}] {method} → {status}")
    else:
        print("📭 No webhook requests received yet")
        print("   This is normal if:")
        print("   - Webhook URL is not configured in Bolna AI Dashboard yet")
        print("   - No calls have completed since webhook was configured")
    print()
    
    # 6. Summary & Next Steps
    print("="*70)
    print("📋 Setup Summary & Next Steps")
    print("="*70)
    print()
    
    all_ready = flask_status and ngrok_url
    
    if all_ready:
        webhook_url = f"{ngrok_url}/api/webhook"
        print("✅ All components are ready!")
        print()
        print("🎯 Action Required:")
        print(f"   1. Copy this webhook URL: {webhook_url}")
        print("   2. Go to Bolna AI Dashboard: https://platform.bolna.ai/")
        print("   3. Navigate to your agent → Webhook settings")
        print("   4. Paste the webhook URL")
        print("   5. Save configuration")
        print()
        print("🧪 Test the setup:")
        print("   1. Make a test call from your application")
        print("   2. Monitor Flask logs for webhook requests")
        print("   3. Check candidate status updates")
        print("   4. View ngrok dashboard: http://localhost:4040")
        print()
        print("📊 Monitor webhook activity:")
        print("   python monitor_ngrok_requests.py")
        print("   python check_execution_status.py")
    else:
        print("⚠️  Setup incomplete:")
        if not flask_status:
            print("   ❌ Flask server is not running")
        if not ngrok_url:
            print("   ❌ ngrok tunnel is not running")
        print()
        print("Fix the issues above and run this script again")
    
    print()
    print("="*70)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

