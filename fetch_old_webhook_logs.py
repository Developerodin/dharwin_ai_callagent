"""
Fetch old webhook logs from various sources:
1. webhook_logs.json (temporary storage)
2. ngrok request logs (via ngrok API)
3. Any other potential log files
"""

import json
import os
import requests
from datetime import datetime

def check_webhook_logs_file():
    """Check for webhook_logs.json in root directory"""
    log_file = 'webhook_logs.json'
    
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            print(f"✅ Found {log_file}")
            print(f"   Total entries: {len(logs) if isinstance(logs, list) else 'N/A'}")
            return logs
        except Exception as e:
            print(f"⚠️  Error reading {log_file}: {e}")
            return None
    else:
        print(f"❌ {log_file} not found")
        return None

def fetch_ngrok_requests(limit=50):
    """Fetch webhook requests from ngrok local API"""
    try:
        print(f"\n🔍 Checking ngrok request logs...")
        response = requests.get(
            f'http://localhost:4040/api/requests/http?limit={limit}',
            timeout=2
        )
        
        if response.status_code == 200:
            data = response.json()
            requests_list = data.get('requests', [])
            
            # Filter for webhook requests
            webhook_requests = []
            for req in requests_list:
                try:
                    req_data = req.get('request', {})
                    uri = req_data.get('uri', {})
                    
                    # Handle both dict and string formats
                    if isinstance(uri, str):
                        path = uri
                    elif isinstance(uri, dict):
                        path = uri.get('path', '')
                    else:
                        path = str(uri)
                    
                    # Check if it's a webhook request
                    if '/api/webhook' in path or path == '/' or 'webhook' in path.lower():
                        webhook_requests.append(req)
                except Exception as e:
                    # Skip malformed requests
                    continue
            
            if webhook_requests:
                print(f"✅ Found {len(webhook_requests)} webhook requests in ngrok logs")
                return webhook_requests
            else:
                print(f"⚠️  No webhook requests found in ngrok logs")
                return []
        else:
            print(f"⚠️  ngrok API not accessible (status: {response.status_code})")
            print(f"   Make sure ngrok is running and accessible at http://localhost:4040")
            return []
            
    except requests.exceptions.ConnectionError:
        print(f"⚠️  Cannot connect to ngrok API")
        print(f"   Make sure ngrok is running")
        return []
    except Exception as e:
        print(f"⚠️  Error fetching ngrok requests: {e}")
        return []

def convert_ngrok_request_to_payload(ngrok_request):
    """Convert ngrok request format to webhook payload format"""
    try:
        request_data = ngrok_request.get('request', {})
        uri = request_data.get('uri', {})
        headers = request_data.get('headers', {})
        body = request_data.get('body', '')
        
        # Handle uri as string or dict
        if isinstance(uri, str):
            path = uri
        elif isinstance(uri, dict):
            path = uri.get('path', '')
        else:
            path = str(uri)
        
        # Try to parse body as JSON
        payload = {}
        if body:
            try:
                if isinstance(body, str):
                    payload = json.loads(body)
                elif isinstance(body, dict):
                    payload = body
                else:
                    payload = {'raw_body': str(body)}
            except:
                payload = {'raw_body': body}
        
        # Add metadata
        payload['_ngrok_metadata'] = {
            'timestamp': ngrok_request.get('started_at', ''),
            'method': request_data.get('method', ''),
            'path': path,
            'remote_addr': (
                headers.get('X-Forwarded-For', [None])[0] 
                if isinstance(headers.get('X-Forwarded-For'), list) 
                else headers.get('X-Forwarded-For', '')
            ) if headers else ''
        }
        
        return payload
    except Exception as e:
        print(f"⚠️  Error converting ngrok request: {e}")
        import traceback
        traceback.print_exc()
        return {}

def migrate_from_ngrok(ngrok_requests):
    """Migrate ngrok requests to permanent storage"""
    if not ngrok_requests:
        return
    
    print(f"\n📥 Migrating {len(ngrok_requests)} requests from ngrok...")
    
    webhook_data_file = 'data/webhook_data.json'
    os.makedirs('data', exist_ok=True)
    
    # Load existing storage
    webhook_data = {}
    if os.path.exists(webhook_data_file):
        try:
            with open(webhook_data_file, 'r', encoding='utf-8') as f:
                webhook_data = json.load(f)
        except:
            pass
    
    if 'all_webhooks' not in webhook_data:
        webhook_data['all_webhooks'] = []
    
    migrated = 0
    
    for ngrok_req in ngrok_requests:
        try:
            payload = convert_ngrok_request_to_payload(ngrok_req)
            
            # Extract execution_id
            execution_id = (
                payload.get('execution_id') or 
                payload.get('executionId') or 
                payload.get('id') or
                payload.get('data', {}).get('execution_id') or
                f"ngrok_{ngrok_req.get('id', 'unknown')}"
            )
            
            # Skip if already exists
            if execution_id in webhook_data:
                continue
            
            # Find candidate_id
            candidate_id = None
            mapping_file = 'execution_mapping.json'
            if os.path.exists(mapping_file):
                try:
                    with open(mapping_file, 'r', encoding='utf-8') as f:
                        mappings = json.load(f)
                        mapping = mappings.get(execution_id)
                        if mapping:
                            candidate_id = mapping.get('candidate_id')
                except:
                    pass
            
            # Create entry
            timestamp = ngrok_req.get('started_at', datetime.now().isoformat())
            entry = {
                'execution_id': execution_id,
                'candidate_id': candidate_id,
                'timestamp': timestamp,
                'received_at': timestamp.split('T')[0] + ' ' + timestamp.split('T')[1].split('.')[0] if 'T' in timestamp else timestamp,
                'payload': payload,
                'extracted_data': payload.get('extracted_data', {}),
                'transcript': payload.get('transcript', ''),
                'status': payload.get('status', 'unknown'),
                'recipient_phone_number': payload.get('recipient_phone_number'),
                'telephony_data': payload.get('telephony_data', {}),
                '_source': 'ngrok_logs'
            }
            
            webhook_data[execution_id] = entry
            webhook_data['all_webhooks'].insert(0, {
                'execution_id': execution_id,
                'candidate_id': candidate_id,
                'timestamp': timestamp,
                'status': entry['status']
            })
            
            migrated += 1
            
        except Exception as e:
            print(f"⚠️  Error processing ngrok request: {e}")
            continue
    
    # Save
    if migrated > 0:
        with open(webhook_data_file, 'w', encoding='utf-8') as f:
            json.dump(webhook_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Migrated {migrated} requests from ngrok to permanent storage")

def main():
    print(f"{'='*70}")
    print(f"🔍 Fetching Old Webhook Logs")
    print(f"{'='*70}\n")
    
    # Check temporary storage
    old_logs = check_webhook_logs_file()
    
    # Migrate from temporary storage
    if old_logs:
        print(f"\n💡 Run 'python migrate_webhook_logs.py' to migrate these logs")
    
    # Check ngrok
    ngrok_requests = fetch_ngrok_requests(limit=100)
    
    if ngrok_requests:
        print(f"\n💡 Found {len(ngrok_requests)} webhook requests in ngrok")
        response = input("   Migrate these to permanent storage? (y/n): ").strip().lower()
        if response == 'y':
            migrate_from_ngrok(ngrok_requests)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 Summary")
    print(f"{'='*70}")
    
    if old_logs:
        print(f"✅ Temporary logs found: {len(old_logs)} entries")
        print(f"   Run: python migrate_webhook_logs.py")
    else:
        print(f"❌ No temporary logs found")
    
    if ngrok_requests:
        print(f"✅ ngrok logs found: {len(ngrok_requests)} webhook requests")
    else:
        print(f"❌ No ngrok logs found")
    
    # Check permanent storage
    if os.path.exists('data/webhook_data.json'):
        try:
            with open('data/webhook_data.json', 'r', encoding='utf-8') as f:
                permanent_data = json.load(f)
                count = len([k for k in permanent_data.keys() if k != 'all_webhooks'])
                print(f"✅ Permanent storage: {count} entries")
        except:
            pass
    
    print(f"\n💡 View stored data: python view_webhook_data.py")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()

