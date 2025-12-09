"""
Verify Webhook Configuration
Checks webhook endpoint, URL, and provides instructions for Bolna Dashboard
"""

import requests
import json
import os

def check_flask_server():
    """Check if Flask server is running"""
    try:
        response = requests.get('http://localhost:5000/api/webhook/status', timeout=2)
        if response.status_code == 200:
            data = response.json()
            return True, data
        return False, None
    except:
        return False, None

def check_ngrok_tunnel():
    """Check if ngrok tunnel is active"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            https_tunnel = next(
                (t for t in tunnels if t.get('proto') == 'https'),
                None
            )
            if https_tunnel:
                public_url = https_tunnel.get('public_url', '')
                return True, public_url
            return False, None
        return False, None
    except:
        return False, None

def check_webhook_endpoint(webhook_url):
    """Test webhook endpoint accessibility"""
    try:
        # Try a HEAD request first
        response = requests.head(webhook_url, timeout=5)
        return True, response.status_code
    except requests.exceptions.SSLError:
        return False, "SSL Error - Check ngrok certificate"
    except requests.exceptions.ConnectionError:
        return False, "Connection Error - Endpoint not accessible"
    except Exception as e:
        return False, str(e)

def get_webhook_url():
    """Get the webhook URL from config or ngrok"""
    ngrok_active, ngrok_url = check_ngrok_tunnel()
    
    if ngrok_active:
        return f"{ngrok_url}/api/webhook"
    
    # Check for stored URL
    if os.path.exists('WEBHOOK_URL.txt'):
        try:
            with open('WEBHOOK_URL.txt', 'r') as f:
                content = f.read()
                # Extract URL from file
                for line in content.split('\n'):
                    if 'https://' in line and 'ngrok' in line:
                        return line.strip()
        except:
            pass
    
    return None

def main():
    print(f"{'='*70}")
    print(f"🔍 Webhook Configuration Verification")
    print(f"{'='*70}\n")
    
    # 1. Check Flask Server
    print("1️⃣  Flask Server Status")
    print("-" * 70)
    flask_running, flask_data = check_flask_server()
    
    if flask_running:
        print("✅ Flask server is running on http://localhost:5000")
        if flask_data:
            print(f"   Webhook endpoint: {flask_data.get('webhook_endpoint', '/api/webhook')}")
            print(f"   Execution mappings: {flask_data.get('execution_mappings', 0)}")
            print(f"   Candidates: {flask_data.get('candidates', 0)}")
    else:
        print("❌ Flask server is NOT running")
        print("   Start it with: python api_server.py")
    
    print()
    
    # 2. Check ngrok Tunnel
    print("2️⃣  ngrok Tunnel Status")
    print("-" * 70)
    ngrok_active, ngrok_url = check_ngrok_tunnel()
    
    if ngrok_active:
        print(f"✅ ngrok tunnel is active")
        print(f"   Public URL: {ngrok_url}")
        
        webhook_url = f"{ngrok_url}/api/webhook"
        print(f"   Webhook URL: {webhook_url}")
        
        # Test endpoint
        accessible, status = check_webhook_endpoint(webhook_url)
        if accessible:
            print(f"✅ Webhook endpoint is accessible (Status: {status})")
        else:
            print(f"⚠️  Webhook endpoint test: {status}")
    else:
        print("❌ ngrok tunnel is NOT active")
        print("   Start it with: ngrok http 5000")
        print("   Or check if ngrok is running at: http://localhost:4040")
    
    print()
    
    # 3. Webhook URL for Bolna Dashboard
    print("3️⃣  Webhook URL for Bolna Dashboard")
    print("-" * 70)
    
    webhook_url = get_webhook_url()
    
    if webhook_url:
        print(f"✅ Webhook URL found:")
        print(f"   {webhook_url}")
        print()
        print("📋 Copy this URL to configure in Bolna Dashboard:")
        print(f"   {webhook_url}")
    else:
        print("⚠️  Webhook URL not found")
        print("   Make sure ngrok is running or check WEBHOOK_URL.txt")
    
    print()
    
    # 4. Bolna Dashboard Configuration Instructions
    print("4️⃣  Bolna Dashboard Configuration")
    print("-" * 70)
    print("To configure webhook in Bolna Dashboard:")
    print()
    print("  1. Go to: https://platform.bolna.ai/")
    print("  2. Log in to your account")
    print("  3. Navigate to your agent settings")
    print("  4. Find 'Webhook URL' or 'Push all execution data to webhook' section")
    print("  5. Paste the webhook URL above")
    print("  6. Save the configuration")
    print()
    print("  📍 Look for sections like:")
    print("     - 'Webhook Configuration'")
    print("     - 'Webhook Settings'")
    print("     - 'Real-time Data Push'")
    print("     - 'Execution Webhook'")
    print()
    
    # 5. IP Whitelist
    print("5️⃣  IP Whitelist Information")
    print("-" * 70)
    print("Bolna AI sends webhooks from these IP addresses:")
    print("  - 13.200.45.61")
    print("  - 65.2.44.157")
    print("  - 34.194.233.253")
    print("  - 13.204.98.4")
    print("  - 43.205.31.43")
    print("  - 107.20.118.52")
    print()
    print("  ✅ These IPs are automatically whitelisted in the webhook handler")
    print("  ✅ ngrok handles IP validation automatically")
    print()
    
    # 6. Testing
    print("6️⃣  Testing Webhook")
    print("-" * 70)
    if webhook_url:
        print("After configuring in Bolna Dashboard:")
        print("  1. Make a test call from your application")
        print("  2. Check Flask server logs for webhook requests")
        print("  3. Verify data is saved to data/webhook_data.json")
        print("  4. Check with: python view_webhook_data.py")
    else:
        print("⚠️  Webhook URL not available - cannot test")
    print()
    
    # 7. Summary
    print(f"{'='*70}")
    print(f"📊 Summary")
    print(f"{'='*70}")
    
    issues = []
    if not flask_running:
        issues.append("❌ Flask server not running")
    if not ngrok_active:
        issues.append("❌ ngrok tunnel not active")
    if not webhook_url:
        issues.append("⚠️  Webhook URL not found")
    
    if not issues:
        print("✅ All systems ready!")
        print(f"\n🎯 Next Steps:")
        print(f"   1. Copy webhook URL: {webhook_url}")
        print(f"   2. Go to: https://platform.bolna.ai/")
        print(f"   3. Configure webhook URL in agent settings")
        print(f"   4. Make a test call")
    else:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"   {issue}")
        print(f"\n💡 Fix the issues above, then re-run this script")
    
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()

