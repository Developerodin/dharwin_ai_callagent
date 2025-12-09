"""
Test Bolna AI API connection and endpoints
"""

import requests
import os
from config import BOLNA_API_BASE, BOLNA_API_KEY

def test_api_connection():
    """Test basic API connection"""
    print("\n" + "="*70)
    print("🧪 Testing Bolna AI API Connection")
    print("="*70)
    print()
    
    if not BOLNA_API_KEY:
        print("❌ BOLNA_API_KEY not found in .env file")
        return False
    
    print(f"✅ API Key found: {BOLNA_API_KEY[:10]}...")
    print(f"✅ API Base URL: {BOLNA_API_BASE}")
    print()
    
    headers = {
        "Authorization": f"Bearer {BOLNA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test 1: List agents
    print("1️⃣ Testing: List Agents")
    print("-" * 70)
    try:
        url = f"{BOLNA_API_BASE}/agent"
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            agents = response.json()
            if isinstance(agents, list):
                print(f"   ✅ Found {len(agents)} agent(s)")
                if agents:
                    print(f"   Agent IDs: {[a.get('agent_id') or a.get('id') for a in agents[:3]]}")
            elif isinstance(agents, dict):
                print(f"   ✅ Response received")
                print(f"   Keys: {list(agents.keys())}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    print()
    
    # Test 2: List executions (batch)
    print("2️⃣ Testing: List Executions (Batch)")
    print("-" * 70)
    try:
        url = f"{BOLNA_API_BASE}/execution"
        params = {"page_number": 1, "page_size": 5}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'data' in data:
                executions = data['data']
                print(f"   ✅ Found {len(executions)} execution(s) (page 1)")
                if executions:
                    exec_id = executions[0].get('execution_id') or executions[0].get('id')
                    print(f"   First execution ID: {exec_id}")
                    print(f"   Status: {executions[0].get('status', 'N/A')}")
            elif isinstance(data, list):
                print(f"   ✅ Found {len(data)} execution(s)")
                if data:
                    exec_id = data[0].get('execution_id') or data[0].get('id')
                    print(f"   First execution ID: {exec_id}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    print()
    
    # Test 3: Test specific execution ID
    print("3️⃣ Testing: Fetch Specific Execution")
    print("-" * 70)
    
    # First get a valid execution ID
    try:
        url = f"{BOLNA_API_BASE}/execution"
        params = {"page_number": 1, "page_size": 1}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'data' in data and data['data']:
                test_exec_id = data['data'][0].get('execution_id') or data['data'][0].get('id')
            elif isinstance(data, list) and data:
                test_exec_id = data[0].get('execution_id') or data[0].get('id')
            else:
                test_exec_id = None
            
            if test_exec_id:
                print(f"   Using execution ID: {test_exec_id}")
                # Try to fetch it
                detail_url = f"{BOLNA_API_BASE}/execution/{test_exec_id}"
                detail_response = requests.get(detail_url, headers=headers, timeout=10)
                print(f"   Status: {detail_response.status_code}")
                if detail_response.status_code == 200:
                    print(f"   ✅ Successfully fetched execution details")
                else:
                    print(f"   ❌ Error: {detail_response.text}")
            else:
                print("   ⚠️  No executions found to test with")
        else:
            print("   ⚠️  Could not list executions to get test ID")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    print()
    
    # Test 4: Check execution mapping
    print("4️⃣ Checking Local Execution Mapping")
    print("-" * 70)
    import json
    if os.path.exists('execution_mapping.json'):
        with open('execution_mapping.json', 'r') as f:
            mappings = json.load(f)
        if mappings:
            local_exec_id = list(mappings.keys())[0]
            print(f"   Local execution ID: {local_exec_id}")
            print(f"   Trying to fetch this execution...")
            try:
                detail_url = f"{BOLNA_API_BASE}/execution/{local_exec_id}"
                detail_response = requests.get(detail_url, headers=headers, timeout=10)
                print(f"   Status: {detail_response.status_code}")
                if detail_response.status_code == 200:
                    print(f"   ✅ Execution found in API")
                elif detail_response.status_code == 404:
                    print(f"   ⚠️  Execution not found (404)")
                    print(f"   Possible reasons:")
                    print(f"   - Execution expired or was deleted")
                    print(f"   - Execution ID format is incorrect")
                    print(f"   - Execution belongs to different account")
                else:
                    print(f"   ❌ Error: {detail_response.text}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        else:
            print("   ⚠️  No execution mappings found")
    else:
        print("   ⚠️  execution_mapping.json not found")
    print()
    
    print("="*70)
    print("📋 Summary")
    print("="*70)
    print("✅ API connection test complete")
    print()
    print("💡 If execution returns 404:")
    print("   - The execution may have expired")
    print("   - Use /execution endpoint to list recent executions")
    print("   - Webhook will still work for new calls")
    print()

if __name__ == "__main__":
    test_api_connection()

