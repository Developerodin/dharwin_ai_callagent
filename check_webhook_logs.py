"""
Check webhook logs and monitor incoming data from Bolna AI
"""

import requests
import json
import time
import os
from datetime import datetime

FLASK_URL = "http://localhost:5000"

def check_webhook_status():
    """Check webhook endpoint status"""
    try:
        response = requests.get(f"{FLASK_URL}/api/webhook/status", timeout=3)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def check_execution_mappings():
    """Check execution mappings file"""
    mapping_file = 'execution_mapping.json'
    if os.path.exists(mapping_file):
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
            return mappings
        except:
            return None
    return None

def check_candidate_statuses():
    """Check current candidate statuses"""
    candidates_file = 'data/candidates.json'
    if os.path.exists(candidates_file):
        try:
            with open(candidates_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('candidates', [])
        except:
            return None
    return None

def test_webhook_endpoint():
    """Test if webhook endpoint is accessible"""
    try:
        test_payload = {
            "execution_id": "test_check_123",
            "status": "test",
            "recipient_phone_number": "+918755887760"
        }
        response = requests.post(
            f"{FLASK_URL}/api/webhook",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        return response.status_code, response.json() if response.status_code < 500 else None
    except Exception as e:
        return None, str(e)

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

def get_ngrok_requests():
    """Get recent requests from ngrok"""
    try:
        response = requests.get('http://localhost:4040/api/requests/http', timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def main():
    print("\n" + "="*70)
    print("📊 Webhook Data Log Checker - Bolna AI")
    print("="*70)
    print()
    
    # Check Flask server
    print("1️⃣ Checking Flask Server...")
    status = check_webhook_status()
    if status:
        print("✅ Flask server is running")
        print(f"   Webhook endpoint: /api/webhook")
        print(f"   Execution mappings: {status.get('execution_mappings', 0)}")
        print(f"   Candidates: {status.get('candidates', 0)}")
        print(f"   Agent initialized: {status.get('agent_initialized', False)}")
    else:
        print("❌ Flask server is NOT running or not accessible")
        print("   Please start Flask: python api_server.py")
        print()
        return
    print()
    
    # Check ngrok
    print("2️⃣ Checking ngrok Tunnel...")
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        webhook_url = f"{ngrok_url}/api/webhook"
        print(f"✅ ngrok tunnel is active")
        print(f"   Public URL: {ngrok_url}")
        print(f"   Webhook URL: {webhook_url}")
        print()
        print(f"📋 Make sure this URL is configured in Bolna AI Dashboard:")
        print(f"   {webhook_url}")
    else:
        print("⚠️  ngrok tunnel not detected")
        print("   Make sure ngrok is running: ngrok http 5000")
        print("   Check ngrok at: http://localhost:4040")
    print()
    
    # Check execution mappings
    print("3️⃣ Checking Execution Mappings...")
    mappings = check_execution_mappings()
    if mappings:
        print(f"✅ Found {len(mappings)} execution mapping(s):")
        for exec_id, mapping in mappings.items():
            print(f"   Execution ID: {exec_id[:20]}...")
            print(f"   → Candidate ID: {mapping.get('candidate_id')}")
            print(f"   → Phone: {mapping.get('phone')}")
            print(f"   → Created: {mapping.get('created_at')}")
    else:
        print("⚠️  No execution mappings found")
        print("   This means no calls have been initiated yet")
    print()
    
    # Check candidate statuses
    print("4️⃣ Checking Candidate Statuses...")
    candidates = check_candidate_statuses()
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
            print(f"   {status_icon} {cand['name']}: {cand['status']}")
    print()
    
    # Check ngrok request history
    print("5️⃣ Checking Recent Webhook Requests (ngrok)...")
    requests_data = get_ngrok_requests()
    if requests_data:
        requests_list = requests_data.get('requests', [])
        if requests_list:
            print(f"✅ Found {len(requests_list)} recent request(s):")
            # Show last 5 requests
            for req in requests_list[-5:]:
                method = req.get('request', {}).get('method', 'N/A')
                path = req.get('request', {}).get('uri', {}).get('path', 'N/A')
                status_code = req.get('response', {}).get('status', 'N/A')
                timestamp = req.get('started_at', 'N/A')
                print(f"   [{timestamp[:19]}] {method} {path} → {status_code}")
        else:
            print("⚠️  No requests received yet")
            print("   Waiting for Bolna AI to send webhook data...")
    else:
        print("⚠️  Could not access ngrok request history")
        print("   Check manually at: http://localhost:4040")
    print()
    
    # Test webhook endpoint
    print("6️⃣ Testing Webhook Endpoint...")
    status_code, result = test_webhook_endpoint()
    if status_code:
        if status_code == 200 or status_code == 400:  # 400 is expected for test without valid execution_id
            print(f"✅ Webhook endpoint is accessible (Status: {status_code})")
        else:
            print(f"⚠️  Webhook returned status: {status_code}")
    else:
        print(f"❌ Could not test webhook: {result}")
    print()
    
    # Summary
    print("="*70)
    print("📋 Summary")
    print("="*70)
    
    if ngrok_url and status:
        webhook_url = f"{ngrok_url}/api/webhook"
        print(f"✅ Webhook is ready to receive data!")
        print(f"   URL: {webhook_url}")
        print()
        print("📝 Next steps:")
        print("   1. Verify webhook URL is configured in Bolna AI Dashboard")
        print("   2. Make a test call from your application")
        print("   3. Monitor Flask logs for incoming webhook data")
        print("   4. Check ngrok dashboard: http://localhost:4040")
        print()
        print("💡 To monitor in real-time, keep Flask running and watch:")
        print("   - Flask terminal for webhook logs")
        print("   - ngrok dashboard at http://localhost:4040")
    else:
        print("⚠️  Setup incomplete - please check the issues above")
    
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

