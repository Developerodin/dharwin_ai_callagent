"""
Example script to make a call using the Bolna AI agent
API key is loaded from .env file
"""

from bolna_agent import BolnaAgent
import json

def make_interview_call():
    """Example function to make an interview scheduling call"""
    
    # Initialize the agent (API key loaded from .env file)
    try:
        agent = BolnaAgent()
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    # Use existing agent ID if available
    from config import AGENT_ID
    if AGENT_ID:
        agent.agent_id = AGENT_ID
        print(f"✅ Using existing agent ID: {AGENT_ID}")
    else:
        # Create the agent (only needed once, or if you want to recreate it)
        print("Creating agent...")
        try:
            agent.create_agent()
        except Exception as e:
            print(f"Note: {e}")
            print("Agent may already exist. Continuing...")
    
    # Example candidate information
    candidate_info = {
        "phone_number": "+919876543210",  # Replace with actual phone number (E.164 format)
        "caller_id": "+911234567890",      # Replace with your caller ID (E.164 format)
        "candidate_name": "Priya Sharma",
        "interview_date": "Friday, the 12th of December",
        "interview_time": "10:00 A.M.",
        "alternative_slots": [
            "Monday, the 15th of December, at 2:00 P.M.",
            "Tuesday, the 16th of December, at 11:00 A.M.",
            "Wednesday, the 17th of December, at 3:00 P.M."
        ]
    }
    
    # Make the call
    print(f"\n📞 Calling {candidate_info['candidate_name']}...")
    try:
        result = agent.make_call(
            phone_number=candidate_info["phone_number"],
            caller_id=candidate_info["caller_id"],
            candidate_name=candidate_info["candidate_name"],
            interview_date=candidate_info["interview_date"],
            interview_time=candidate_info["interview_time"],
            alternative_slots=candidate_info["alternative_slots"]
        )
        
        execution_id = result.get("execution_id")
        if execution_id:
            print(f"✅ Call initiated successfully!")
            print(f"Execution ID: {execution_id}")
            
            # Optionally, fetch call details after some time
            # import time
            # time.sleep(30)  # Wait 30 seconds
            # print("\n📊 Fetching call details...")
            # details = agent.get_execution_details(execution_id)
            # print(json.dumps(details, indent=2))
        else:
            print("⚠️  Call initiated but no execution ID returned")
            print(f"Response: {json.dumps(result, indent=2)}")
            
    except Exception as e:
        print(f"❌ Error making call: {e}")


if __name__ == "__main__":
    make_interview_call()

