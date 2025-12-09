"""
Test script for webhook endpoint
This script simulates a webhook payload from Bolna AI for testing purposes
"""

import requests
import json
import sys

# Webhook endpoint URL
WEBHOOK_URL = "http://localhost:5000/api/webhook"

def test_webhook(execution_id: str, candidate_id: int = None, status: str = "completed"):
    """
    Test the webhook endpoint with a simulated payload
    
    Args:
        execution_id: The execution ID to test with
        candidate_id: Optional candidate ID (will try to find by phone if not provided)
        status: Call status (completed, failed, in_progress, etc.)
    """
    
    # Sample webhook payload structure (based on Bolna AI format)
    payload = {
        "execution_id": execution_id,
        "status": status,
        "transcript": "Agent: Hello, this is Ava calling from Dharwin. I'm calling to confirm your interview scheduled for Friday, the 12th of December at 10:00 A.M. Candidate: Yes, I can confirm that. Agent: Great! Thank you for confirming. We'll see you then.",
        "extracted_data": {
            "status": "confirmed",
            "user_interested": True
        },
        "recipient_phone_number": "+918755887760",
        "telephony_data": {
            "duration": 120,
            "recording_url": "https://example.com/recording.mp3"
        },
        "data": {
            "execution_id": execution_id,
            "status": status,
            "transcript": "Agent: Hello, this is Ava calling from Dharwin..."
        }
    }
    
    print(f"📤 Sending test webhook to {WEBHOOK_URL}")
    print(f"📋 Payload:")
    print(json.dumps(payload, indent=2))
    print()
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Webhook test successful!")
        else:
            print(f"\n❌ Webhook test failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {WEBHOOK_URL}")
        print("   Make sure the Flask server is running: python api_server.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the webhook endpoint")
    parser.add_argument(
        "--execution-id",
        type=str,
        default="test_exec_1234567890",
        help="Execution ID to test with"
    )
    parser.add_argument(
        "--candidate-id",
        type=int,
        help="Candidate ID (optional, will try to find by phone if not provided)"
    )
    parser.add_argument(
        "--status",
        type=str,
        default="completed",
        choices=["completed", "failed", "in_progress", "initiated"],
        help="Call status"
    )
    
    args = parser.parse_args()
    
    print("🧪 Testing Webhook Endpoint")
    print("=" * 50)
    print()
    
    test_webhook(
        execution_id=args.execution_id,
        candidate_id=args.candidate_id,
        status=args.status
    )

