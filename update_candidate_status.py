"""
Helper functions to update candidate status based on call outcomes
"""

import json
import re
from typing import Dict, Any, Optional
from slot_converter import convert_slot_to_interview_format

def parse_call_outcome(execution_details: Dict[str, Any], transcript: Optional[str] = None) -> Dict[str, Any]:
    """
    Parse call execution details to determine the outcome
    Supports new structured extraction format with call_outcome, original_slot, final_slot
    
    Args:
        execution_details: Execution details from Bolna AI
        transcript: Call transcript (optional)
    
    Returns:
        Dictionary with status and updated interview info
    """
    status = "pending"
    updated_interview = None
    
    # Get transcript if available
    if not transcript:
        transcript = execution_details.get('transcript', '')
    
    # Get extracted data if available (from structured output)
    extracted_data = execution_details.get('extracted_data', {})
    
    # Check extracted data first (most reliable) - NEW STRUCTURED FORMAT
    if extracted_data:
        print(f"📊 Checking extracted_data: {extracted_data}")
        
        # NEW: Check for structured extraction format (call_outcome, original_slot, final_slot)
        call_outcome = extracted_data.get('call_outcome')
        
        if call_outcome:
            print(f"✅ Found structured extraction: call_outcome = {call_outcome}")
            
            # Map call_outcome to status
            if call_outcome == "ACCEPTED":
                status = 'confirmed'
                print(f"✅ Call outcome: ACCEPTED → CONFIRMED")
                
                # For ACCEPTED, final_slot should match original_slot
                final_slot = extracted_data.get('final_slot')
                if final_slot:
                    updated_interview = convert_slot_to_interview_format(final_slot)
                    
            elif call_outcome == "REJECTED":
                status = 'declined'
                print(f"✅ Call outcome: REJECTED → DECLINED")
                # final_slot should be null for REJECTED
                
            elif call_outcome == "RESCHEDULED":
                status = 'rescheduled'
                print(f"✅ Call outcome: RESCHEDULED → RESCHEDULED")
                
                # For RESCHEDULED, use final_slot as the new interview time
                final_slot = extracted_data.get('final_slot')
                if final_slot:
                    updated_interview = convert_slot_to_interview_format(final_slot)
                    print(f"📅 New slot from extraction: {final_slot}")
                    
            # Log notes if available
            notes = extracted_data.get('notes')
            if notes:
                print(f"📝 Notes: {notes}")
        
        # OLD FORMAT: Check for explicit status field (backward compatibility)
        elif extracted_data.get('status'):
            status = extracted_data.get('status')
            print(f"✅ Found explicit status in extracted_data: {status}")
        
        # OLD FORMAT: Check for user_interested flag (backward compatibility)
        elif 'user_interested' in extracted_data:
            if extracted_data.get('user_interested') is True:
                status = 'confirmed'
                print(f"✅ User interested = True → CONFIRMED")
            elif extracted_data.get('user_interested') is False:
                status = 'declined'
                print(f"✅ User interested = False → DECLINED")
        
        # OLD FORMAT: Check for callback_user flag (backward compatibility)
        elif 'callback_user' in extracted_data:
            if extracted_data.get('callback_user') is True:
                status = 'rescheduled'
                print(f"✅ Callback requested → RESCHEDULED")
        
        # OLD FORMAT: Get new slot if rescheduled (backward compatibility)
        if status == 'rescheduled' and not updated_interview:
            new_slot = (
                extracted_data.get('new_slot') or 
                extracted_data.get('rescheduled_slot') or
                extracted_data.get('new_interview_slot') or
                extracted_data.get('preferred_slot')
            )
            if new_slot:
                updated_interview = parse_slot_string(new_slot)
                print(f"📅 Found new slot in extracted_data: {new_slot}")
    
    # Fallback: Parse transcript for keywords (more comprehensive)
    if status == "pending" and transcript:
        transcript_lower = transcript.lower()
        transcript_full = transcript  # Keep original for pattern matching
        
        print(f"📝 Parsing transcript (length: {len(transcript)} chars)...")
        print(f"📝 Transcript preview: {transcript[:200]}...")
        
        # Strong indicators for CONFIRMED
        confirmed_patterns = [
            r'\b(confirmed|confirm|confirmation)\b',
            r'\b(yes|yeah|sure|okay|ok|alright|sounds good|that works|perfect)\b.*\b(interview|slot|time)\b',
            r'\b(i will|i\'ll|i can).*\b(attend|come|be there)\b',
            r'\b(see you|looking forward|thank you).*\b(confirmation|confirm)\b'
        ]
        
        # Strong indicators for DECLINED
        # ⚠️ Be careful: Only mark as declined if candidate explicitly declined
        # Wrong person answering should NOT be marked as declined
        declined_patterns = [
            r'\b(declined|decline|not interested|no longer interested)\b',
            r'\b(i don\'t want|i do not want).*\b(interview|position|job)\b',
            r'\b(remove|withdraw|not pursuing).*\b(application|position)\b',
            r'\b(no thank you|no thanks).*\b(not interested|not pursuing)\b'
        ]
        
        # Patterns that indicate WRONG PERSON (NOT declined)
        wrong_person_patterns = [
            r'\b(i\'m|this is|i am)\s+[a-z]+\s*(?!{name})',  # Someone says "I'm [different name]"
            r'\b(wrong number|wrong person|not [name])\b',
            r'\b(trying to reach|looking for)\s+{name}'
        ]
        
        # Strong indicators for RESCHEDULED
        rescheduled_patterns = [
            r'\b(rescheduled|reschedule|change|different|another)\b.*\b(time|slot|date|day)\b',
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b.*\b(\d{1,2}(?:st|nd|rd|th)?)\b.*\b(december|january|february|march|april|may|june|july|august|september|october|november)\b',
            r'\b(new|different|another)\b.*\b(slot|time|date)\b',
            r'\b(change|switch|move).*\b(to|for)\b.*\b(monday|tuesday|wednesday|thursday|friday)\b'
        ]
        
        # Check for confirmed (highest priority)
        confirmed_score = sum(1 for pattern in confirmed_patterns if re.search(pattern, transcript_lower, re.IGNORECASE))
        declined_score = sum(1 for pattern in declined_patterns if re.search(pattern, transcript_lower, re.IGNORECASE))
        rescheduled_score = sum(1 for pattern in rescheduled_patterns if re.search(pattern, transcript_full, re.IGNORECASE))
        
        print(f"📊 Pattern scores - Confirmed: {confirmed_score}, Declined: {declined_score}, Rescheduled: {rescheduled_score}")
        
        # Determine status based on scores
        if rescheduled_score > 0 and rescheduled_score >= declined_score:
            status = 'rescheduled'
            updated_interview = extract_slot_from_transcript(transcript_full)
            print(f"✅ Detected RESCHEDULED - New slot: {updated_interview}")
        elif declined_score > 0 and declined_score > confirmed_score:
            status = 'declined'
            print(f"✅ Detected DECLINED")
        elif confirmed_score > 0:
            status = 'confirmed'
            print(f"✅ Detected CONFIRMED")
        else:
            # Fallback: Look for specific phrases
            if re.search(r'\b(great|perfect|thank you|sounds good)\b.*\b(confirmation|confirm|confirmed)\b', transcript_lower):
                status = 'confirmed'
                print(f"✅ Detected CONFIRMED (fallback)")
            elif re.search(r'\b(not|no|decline|cancel|withdraw)\b', transcript_lower) and not re.search(r'\b(yes|sure|okay|confirm)\b', transcript_lower):
                status = 'declined'
                print(f"✅ Detected DECLINED (fallback)")
            else:
                # Default to confirmed if we see positive language
                if re.search(r'\b(yes|sure|okay|alright|perfect|great|thank you)\b', transcript_lower):
                    status = 'confirmed'
                    print(f"✅ Detected CONFIRMED (default positive)")
                else:
                    status = 'pending'
                    print(f"⚠️  Could not determine status, keeping as PENDING")
    
    return {
        'status': status,
        'updated_interview': updated_interview
    }

def parse_slot_string(slot_string: str) -> Optional[Dict[str, str]]:
    """
    Parse a slot string like "Monday, the 15th of December at 2:00 P.M."
    into structured format
    """
    if not slot_string:
        return None
    
    # Try to extract day, date, and time
    # This is a simple parser - you may need to enhance it
    try:
        # Look for day of week
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day = None
        for d in days:
            if d in slot_string.lower():
                day = d.capitalize()
                break
        
        # Look for time patterns (e.g., "2:00 P.M.", "10:00 A.M.")
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*(A\.M\.|P\.M\.)', slot_string, re.IGNORECASE)
        time = None
        if time_match:
            hour = time_match.group(1)
            minute = time_match.group(2)
            period = time_match.group(3).upper()
            time = f"{hour}:{minute} {period}"
        
        # Extract date part (everything between day and time)
        date_part = slot_string
        if day:
            date_part = date_part.split(day, 1)[-1] if day in date_part else date_part
        if time:
            date_part = date_part.split(time, 1)[0] if time in date_part else date_part
        
        return {
            'day': day or 'Monday',
            'date': date_part.strip(),
            'time': time or '10:00 A.M.',
            'datetime': slot_string
        }
    except Exception as e:
        print(f"Error parsing slot: {e}")
        return None

def extract_slot_from_transcript(transcript: str) -> Optional[Dict[str, str]]:
    """
    Extract rescheduled slot information from transcript
    """
    # Look for patterns like "Monday, the 15th of December at 2:00 P.M."
    slot_pattern = r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)[,\s]+(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)?\s+of\s+(\w+)[,\s]+at\s+(\d{1,2}):(\d{2})\s+(A\.M\.|P\.M\.)'
    match = re.search(slot_pattern, transcript, re.IGNORECASE)
    
    if match:
        day = match.group(1)
        date_num = match.group(2)
        month = match.group(3)
        hour = match.group(4)
        minute = match.group(5)
        period = match.group(6).upper()
        
        return {
            'day': day,
            'date': f"{day}, the {date_num}th of {month}",
            'time': f"{hour}:{minute} {period}",
            'datetime': f"{day}, the {date_num}th of {month} at {hour}:{minute} {period}"
        }
    
    return None

def update_candidate_in_json(candidate_id: int, status: str, updated_interview: Optional[Dict[str, str]] = None):
    """
    Update candidate status and interview info in candidates.json
    
    Args:
        candidate_id: ID of the candidate
        status: New status (confirmed, declined, rescheduled)
        updated_interview: Updated interview details if rescheduled
    """
    try:
        import os
        # Use absolute path to ensure we're always using the same file
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, 'data', 'candidates.json')
        
        # Fallback to relative path if absolute doesn't exist
        if not os.path.exists(json_path):
            json_path = 'data/candidates.json'
            if not os.path.exists(json_path):
                # Try from current working directory
                current_dir = os.getcwd()
                json_path = os.path.join(current_dir, 'data', 'candidates.json')
        
        # Normalize the path to ensure consistency
        json_path = os.path.abspath(json_path)
        
        print(f"📁 Updating candidate status - Using path: {json_path}")
        print(f"   Candidate ID: {candidate_id}, Status: {old_status} → {status}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Find the candidate
        candidate = next((c for c in data['candidates'] if c['id'] == candidate_id), None)
        
        if candidate:
            old_status = candidate.get('status', 'unknown')
            candidate['status'] = status
            
            print(f"📝 Updating candidate {candidate_id}: {old_status} → {status}")
            
            # Update interview details if rescheduled
            if status == 'rescheduled' and updated_interview:
                # Preserve original interview if not already stored
                if 'originalInterview' not in candidate:
                    candidate['originalInterview'] = candidate['scheduledInterview'].copy()
                    print(f"💾 Saved original interview: {candidate['originalInterview']['datetime']}")
                
                # Update to new scheduled interview
                old_interview = candidate['scheduledInterview'].copy()
                candidate['scheduledInterview'] = {
                    'day': updated_interview.get('day', candidate['scheduledInterview']['day']),
                    'date': updated_interview.get('date', candidate['scheduledInterview']['date']),
                    'time': updated_interview.get('time', candidate['scheduledInterview']['time']),
                    'datetime': updated_interview.get('datetime', candidate['scheduledInterview']['datetime'])
                }
                print(f"📅 Updated interview: {old_interview['datetime']} → {candidate['scheduledInterview']['datetime']}")
            
            # Write back to file with proper error handling
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Verify write was successful
                with open(json_path, 'r', encoding='utf-8') as f:
                    verify_data = json.load(f)
                    verify_candidate = next((c for c in verify_data.get('candidates', []) if c['id'] == candidate_id), None)
                    if verify_candidate and verify_candidate.get('status') == status:
                        print(f"✅ Successfully updated candidate {candidate_id} in {json_path}")
                        print(f"   Status: {old_status} → {status}")
                        return True
                    else:
                        print(f"⚠️  Status update verification failed. Expected {status}, got {verify_candidate.get('status') if verify_candidate else 'candidate not found'}")
                        return False
            except PermissionError as pe:
                print(f"❌ Permission error writing to {json_path}: {pe}")
                return False
            except Exception as write_error:
                print(f"❌ Error writing to {json_path}: {write_error}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print(f"❌ Candidate {candidate_id} not found in candidates.json")
            print(f"   Available IDs: {[c['id'] for c in data['candidates']]}")
            return False
    except Exception as e:
        import traceback
        print(f"❌ Error updating candidate: {e}")
        traceback.print_exc()
        return False

