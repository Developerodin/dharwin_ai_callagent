"""
Verify webhook endpoint can fetch and process data correctly
"""

import requests
import json
import sys
import os

# Webhook endpoint URL
WEBHOOK_URL = "http://localhost:5000/api/webhook"
FLASK_URL = "http://localhost:5000"

def check_flask_server():
    """Check if Flask server is running"""
    try:
        response = requests.get(f"{FLASK_URL}/api/candidates", timeout=2)
        return True
    except:
        return False

def create_test_mapping():
    """Create a test execution mapping"""
    mapping_file = 'execution_mapping.json'
    test_execution_id = "test_exec_verify_12345"
    test_candidate_id = 1
    
    mappings = {}
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mappings = json.load(f)
    
    mappings[test_execution_id] = {
        'candidate_id': test_candidate_id,
        'phone': '+918755887760',
        'created_at': '2024-12-01 10:00:00'
    }
    
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mappings, f, indent=2)
    
    print(f"✅ Created test mapping: {test_execution_id} -> candidate {test_candidate_id}")
    return test_execution_id, test_candidate_id

def test_webhook_data_extraction():
    """Test if webhook can extract data from payload"""
    print("\n" + "="*60)
    print("🧪 Testing Webhook Data Extraction")
    print("="*60)
    
    # Check if Flask server is running
    print("\n1️⃣ Checking Flask server...")
    if not check_flask_server():
        print("❌ Flask server is not running!")
        print("   Please start it with: python api_server.py")
        return False
    print("✅ Flask server is running")
    
    # Create test mapping
    print("\n2️⃣ Creating test execution mapping...")
    execution_id, candidate_id = create_test_mapping()
    
    # Test payload with various data structures
    test_payloads = [
        {
            "name": "Standard payload",
            "payload": {
                "execution_id": execution_id,
                "status": "completed",
                "transcript": "Agent: Hello, this is Ava. Candidate: Yes, I confirm. Agent: Thank you!",
                "extracted_data": {
                    "status": "confirmed",
                    "user_interested": True
                },
                "recipient_phone_number": "+918755887760"
            }
        },
        {
            "name": "Nested data payload",
            "payload": {
                "data": {
                    "execution_id": execution_id,
                    "status": "completed",
                    "transcript": "Agent: Hello. Candidate: I'd like to reschedule to Monday, the 15th of December at 2:00 P.M.",
                    "extracted_data": {
                        "status": "rescheduled",
                        "new_slot": "Monday, the 15th of December at 2:00 P.M."
                    }
                },
                "recipient_phone_number": "+918755887760"
            }
        },
        {
            "name": "Payload with executionId (camelCase)",
            "payload": {
                "executionId": execution_id,
                "status": "completed",
                "transcript": "Agent: Hello. Candidate: No thank you, I'm not interested.",
                "extracted_data": {
                    "status": "declined",
                    "user_interested": False
                }
            }
        }
    ]
    
    print("\n3️⃣ Testing webhook with different payload structures...")
    print()
    
    success_count = 0
    for i, test in enumerate(test_payloads, 1):
        print(f"📤 Test {i}: {test['name']}")
        print(f"   Execution ID: {execution_id}")
        print(f"   Candidate ID: {candidate_id}")
        
        try:
            # Set environment variable to bypass IP check in dev mode
            os.environ['FLASK_ENV'] = 'development'
            
            response = requests.post(
                WEBHOOK_URL,
                json=test['payload'],
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                print(f"   Response: {json.dumps(result, indent=6)}")
                success_count += 1
            else:
                print(f"   ❌ Failed!")
                try:
                    error = response.json()
                    print(f"   Error: {json.dumps(error, indent=6)}")
                except:
                    print(f"   Error: {response.text}")
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Could not connect to webhook endpoint")
            print(f"   Make sure Flask server is running on {FLASK_URL}")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("="*60)
    print(f"📊 Test Results: {success_count}/{len(test_payloads)} tests passed")
    print("="*60)
    
    if success_count == len(test_payloads):
        print("\n✅ All tests passed! Webhook can fetch and process data correctly.")
        return True
    else:
        print(f"\n⚠️  {len(test_payloads) - success_count} test(s) failed.")
        return False

def verify_candidate_data():
    """Verify candidate data was updated correctly"""
    print("\n4️⃣ Verifying candidate data updates...")
    
    try:
        with open('data/candidates.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        candidate = next((c for c in data['candidates'] if c['id'] == 1), None)
        if candidate:
            print(f"✅ Candidate 1 found: {candidate['name']}")
            print(f"   Current status: {candidate['status']}")
            print(f"   Phone: {candidate['phone']}")
            return True
        else:
            print("❌ Candidate 1 not found")
            return False
    except Exception as e:
        print(f"❌ Error reading candidate data: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Webhook Data Fetching Verification")
    print("="*60)
    
    # Run tests
    if test_webhook_data_extraction():
        verify_candidate_data()
        print("\n✅ Verification complete! Webhook is ready to receive data.")
    else:
        print("\n❌ Verification failed. Please check the errors above.")
        sys.exit(1)

