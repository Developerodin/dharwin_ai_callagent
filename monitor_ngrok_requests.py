"""
Monitor ngrok requests to see incoming webhook data from Bolna AI
This works even if Flask is not running - it shows what ngrok is receiving
"""

import requests
import json
import time
from datetime import datetime

def get_ngrok_tunnels():
    """Get active ngrok tunnels"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_ngrok_requests(limit=10):
    """Get recent requests from ngrok"""
    try:
        response = requests.get(
            f'http://localhost:4040/api/requests/http?limit={limit}',
            timeout=2
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def format_request(req):
    """Format request details for display"""
    request_data = req.get('request', {})
    response_data = req.get('response', {})
    
    method = request_data.get('method', 'N/A')
    uri = request_data.get('uri', {})
    # Handle both dict and string formats
    if isinstance(uri, dict):
        path = uri.get('path', 'N/A')
    else:
        path = str(uri) if uri else 'N/A'
    headers = request_data.get('headers', {})
    
    # Try to get request body
    body = request_data.get('body', '')
    if body:
        try:
            body_json = json.loads(body)
            body_preview = json.dumps(body_json, indent=2)[:500]
        except:
            body_preview = str(body)[:200]
    else:
        body_preview = None
    
    status_code = response_data.get('status', 'N/A')
    started_at = req.get('started_at', 'N/A')
    
    return {
        'method': method,
        'path': path,
        'status': status_code,
        'timestamp': started_at,
        'body': body_preview,
        'headers': headers
    }

def main():
    print("\n" + "="*70)
    print("📡 Monitoring ngrok Requests - Bolna AI Webhook Data")
    print("="*70)
    print()
    
    # Check ngrok
    print("🔍 Checking ngrok...")
    tunnels = get_ngrok_tunnels()
    
    if not tunnels:
        print("❌ ngrok is not running or not accessible")
        print("   Make sure ngrok is running: ngrok http 5000")
        print("   Check ngrok at: http://localhost:4040")
        return
    
    tunnel_list = tunnels.get('tunnels', [])
    if not tunnel_list:
        print("❌ No active ngrok tunnels found")
        return
    
    # Show tunnel info
    print("✅ ngrok is running!")
    print()
    for tunnel in tunnel_list:
        proto = tunnel.get('proto', 'unknown')
        public_url = tunnel.get('public_url', 'N/A')
        config = tunnel.get('config', {})
        addr = config.get('addr', 'N/A')
        
        print(f"   Tunnel: {proto.upper()}")
        print(f"   Public URL: {public_url}")
        print(f"   Forwarding to: {addr}")
        if proto == 'https':
            webhook_url = f"{public_url}/api/webhook"
            print(f"   Webhook URL: {webhook_url}")
        print()
    
    # Get requests
    print("="*70)
    print("📊 Recent Webhook Requests")
    print("="*70)
    print()
    
    requests_data = get_ngrok_requests(limit=20)
    
    if not requests_data:
        print("⚠️  Could not fetch request history")
        print("   Check manually at: http://localhost:4040")
        return
    
    requests_list = requests_data.get('requests', [])
    
    if not requests_list:
        print("📭 No requests received yet")
        print()
        print("💡 Waiting for Bolna AI to send webhook data...")
        print("   Make sure:")
        print("   1. Webhook URL is configured in Bolna AI Dashboard")
        print("   2. Flask server is running: python api_server.py")
        print("   3. A call has been initiated")
        print()
        print("🔄 Monitoring for new requests... (Press Ctrl+C to stop)")
        print()
        
        # Monitor for new requests
        last_count = 0
        try:
            while True:
                new_requests = get_ngrok_requests(limit=5)
                if new_requests:
                    current_count = len(new_requests.get('requests', []))
                    if current_count > last_count:
                        print(f"✅ New request detected! ({current_count} total)")
                        last_count = current_count
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n👋 Stopped monitoring")
        return
    
    # Show requests
    print(f"✅ Found {len(requests_list)} recent request(s)\n")
    
    # Show last 10 requests
    for i, req in enumerate(requests_list[-10:], 1):
        formatted = format_request(req)
        
        print(f"Request #{i}")
        print(f"  Time: {formatted['timestamp'][:19]}")
        print(f"  Method: {formatted['method']}")
        print(f"  Path: {formatted['path']}")
        print(f"  Status: {formatted['status']}")
        
        if formatted['body']:
            print(f"  Body:")
            print("  " + "\n  ".join(formatted['body'].split("\n")[:10]))
            if len(formatted['body']) > 500:
                print("  ... (truncated)")
        
        # Check if it's a webhook request
        if '/api/webhook' in formatted['path'] or '/webhook' in formatted['path']:
            print("  ✅ This is a webhook request!")
            if formatted['body']:
                try:
                    body_data = json.loads(formatted['body'])
                    exec_id = body_data.get('execution_id') or body_data.get('executionId')
                    status = body_data.get('status')
                    if exec_id:
                        print(f"     Execution ID: {exec_id}")
                    if status:
                        print(f"     Status: {status}")
                except:
                    pass
        
        print()
    
    # Summary
    webhook_requests = [
        req for req in requests_list 
        if '/api/webhook' in format_request(req)['path'] or '/webhook' in format_request(req)['path']
    ]
    
    print("="*70)
    print("📋 Summary")
    print("="*70)
    print(f"Total requests: {len(requests_list)}")
    print(f"Webhook requests: {len(webhook_requests)}")
    print()
    
    if webhook_requests:
        print("✅ Webhook is receiving data from Bolna AI!")
        print()
        print("💡 Next steps:")
        print("   1. Check Flask server logs for processing details")
        print("   2. Verify candidate status updates")
        print("   3. Monitor Flask terminal for webhook logs")
    else:
        print("⚠️  No webhook requests found yet")
        print()
        print("💡 Make sure:")
        print("   1. Webhook URL is configured in Bolna AI Dashboard")
        print("   2. Flask server is running: python api_server.py")
        print("   3. A call has been initiated")
    
    print()
    print("🔗 View full request details at: http://localhost:4040")
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

