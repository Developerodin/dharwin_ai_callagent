"""
Helper script to set up ngrok tunnel for Bolna AI webhook
This script helps you get the public URL for your local webhook endpoint
"""

import subprocess
import time
import requests
import json
import sys
import os

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False

def check_flask_running(port=5000):
    """Check if Flask server is running"""
    try:
        response = requests.get(f'http://localhost:{port}/api/webhook/status', timeout=2)
        return response.status_code == 200
    except:
        return False

def get_ngrok_url():
    """Get the public URL from ngrok API"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            data = response.json()
            tunnels = data.get('tunnels', [])
            if tunnels:
                for tunnel in tunnels:
                    if tunnel.get('proto') == 'https':
                        return tunnel.get('public_url')
                # Fallback to first tunnel if no HTTPS
                return tunnels[0].get('public_url')
    except:
        pass
    return None

def print_instructions():
    """Print setup instructions"""
    print("\n" + "="*70)
    print("🌐 ngrok Webhook Setup for Bolna AI")
    print("="*70)
    print()
    print("STEP 1: Install ngrok (if not installed)")
    print("   Visit: https://ngrok.com/download")
    print("   Or use: choco install ngrok (Windows)")
    print("   Or use: brew install ngrok (Mac)")
    print()
    print("STEP 2: Start your Flask server (if not running)")
    print("   python api_server.py")
    print()
    print("STEP 3: Start ngrok tunnel")
    print("   ngrok http 5000")
    print()
    print("STEP 4: Copy your webhook URL")
    print("   Your webhook URL will be: https://YOUR-NGROK-ID.ngrok-free.app/api/webhook")
    print()
    print("STEP 5: Configure in Bolna AI Dashboard")
    print("   1. Go to: https://platform.bolna.ai/")
    print("   2. Navigate to your agent settings")
    print("   3. Find 'Webhook URL' or 'Push all execution data to webhook' section")
    print("   4. Paste your ngrok webhook URL")
    print("   5. Save the configuration")
    print()
    print("="*70)
    print()

def main():
    print_instructions()
    
    # Check if Flask is running
    print("🔍 Checking Flask server...")
    if check_flask_running():
        print("✅ Flask server is running on port 5000")
    else:
        print("❌ Flask server is NOT running!")
        print("   Please start it with: python api_server.py")
        print()
        return
    
    # Check if ngrok is installed
    print("\n🔍 Checking ngrok installation...")
    if check_ngrok_installed():
        print("✅ ngrok is installed")
    else:
        print("❌ ngrok is NOT installed")
        print("   Install from: https://ngrok.com/download")
        print()
        return
    
    # Check if ngrok is running
    print("\n🔍 Checking if ngrok tunnel is running...")
    ngrok_url = get_ngrok_url()
    
    if ngrok_url:
        webhook_url = f"{ngrok_url}/api/webhook"
        print(f"✅ ngrok tunnel is active!")
        print(f"\n📡 Your public webhook URL:")
        print(f"   {webhook_url}")
        print()
        print(f"📋 Copy this URL and configure it in Bolna AI Dashboard:")
        print(f"   1. Go to: https://platform.bolna.ai/")
        print(f"   2. Agent Settings → Webhook")
        print(f"   3. Paste: {webhook_url}")
        print(f"   4. Save")
        print()
        print("🧪 Test your webhook:")
        print(f"   curl -X POST {webhook_url} \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"execution_id\":\"test\",\"status\":\"completed\"}'")
        print()
    else:
        print("❌ ngrok tunnel is NOT running")
        print()
        print("📝 To start ngrok:")
        print("   1. Open a new terminal window")
        print("   2. Run: ngrok http 5000")
        print("   3. Copy the HTTPS URL (starts with https://)")
        print("   4. Your webhook URL will be: https://YOUR-NGROK-ID.ngrok-free.app/api/webhook")
        print()
        print("💡 Tip: Keep ngrok running in a separate terminal while testing")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

