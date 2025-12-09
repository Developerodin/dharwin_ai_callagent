"""
Flask API Server for Bolna Calling Agent
Bridges Next.js frontend with Bolna AI Python backend
"""

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from bolna_agent import BolnaAgent
from update_candidate_status import update_candidate_in_json, parse_call_outcome
from config import BOLNA_API_KEY, AGENT_ID

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Bolna Agent
agent = None
if BOLNA_API_KEY:
    try:
        agent = BolnaAgent()
        if AGENT_ID:
            agent.agent_id = AGENT_ID
            print(f"✅ Using existing agent ID: {AGENT_ID}")
        else:
            print("⚠️  No AGENT_ID in config. Agent will be created on first call.")
    except Exception as e:
        print(f"⚠️  Error initializing Bolna Agent: {e}")
else:
    print("⚠️  BOLNA_API_KEY not found. Some features may not work.")


# ============================================================================
# Helper Functions
# ============================================================================

def save_execution_mapping(execution_id: str, candidate_id: int, phone: str):
    """Save execution_id to candidate_id mapping"""
    try:
        mapping_file = 'execution_mapping.json'
        mappings = {}
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
        
        mappings[execution_id] = {
            'candidate_id': candidate_id,
            'phone': phone,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved execution mapping: {execution_id} -> candidate {candidate_id}")
    except Exception as e:
        print(f"⚠️  Error saving execution mapping: {e}")

def get_execution_mapping(execution_id: str):
    """Get candidate_id from execution_id"""
    try:
        mapping_file = 'execution_mapping.json'
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
                return mappings.get(execution_id)
        return None
    except Exception as e:
        print(f"⚠️  Error reading execution mapping: {e}")
        return None

def save_webhook_data(execution_id: str, payload: dict, candidate_id: int = None):
    """
    Save complete webhook data to data/webhook_data.json
    Stores all payload data permanently organized by execution_id
    """
    try:
        data_dir = 'data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        webhook_data_file = os.path.join(data_dir, 'webhook_data.json')
        
        # Load existing webhook data
        webhook_data = {}
        if os.path.exists(webhook_data_file):
            try:
                with open(webhook_data_file, 'r', encoding='utf-8') as f:
                    webhook_data = json.load(f)
            except:
                webhook_data = {}
        
        # Extract candidate_id if not provided
        if candidate_id is None:
            mapping = get_execution_mapping(execution_id)
            if mapping:
                candidate_id = mapping.get('candidate_id')
        
        # Get execution details (could be nested in data/execution)
        execution_details = payload.get('data') or payload.get('execution') or payload
        
        # Extract telephony data
        telephony_data = (
            payload.get('telephony_data') or
            execution_details.get('telephony_data') or
            {}
        )
        
        # Extract recording URL from telephony_data
        recording_url = (
            telephony_data.get('recording_url') or
            payload.get('recording_url') or
            execution_details.get('recording_url') or
            ''
        )
        
        # Create/update entry for this execution with ALL extracted fields
        entry = {
            'execution_id': execution_id,
            'candidate_id': candidate_id,
            'timestamp': datetime.now().isoformat(),
            'received_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            
            # Complete payload (for reference)
            'payload': payload,
            
            # Core extracted fields (easily accessible)
            'status': (
                payload.get('status') or
                execution_details.get('status') or
                'unknown'
            ),
            'transcript': (
                payload.get('transcript') or
                payload.get('conversation_transcript') or
                execution_details.get('transcript') or
                execution_details.get('conversation_transcript') or
                ''
            ),
            'summary': (
                payload.get('summary') or
                execution_details.get('summary') or
                ''
            ),
            'extracted_data': (
                payload.get('extracted_data') or
                execution_details.get('extracted_data') or
                {}
            ),
            'recipient_phone_number': (
                payload.get('recipient_phone_number') or
                payload.get('phone_number') or
                payload.get('phone') or
                execution_details.get('recipient_phone_number') or
                telephony_data.get('to_number') or
                None
            ),
            'agent_phone_number': (
                payload.get('agent_phone_number') or
                telephony_data.get('from_number') or
                None
            ),
            'telephony_data': telephony_data,
            'recording_url': recording_url,
            'conversation_duration': (
                payload.get('conversation_duration') or
                execution_details.get('conversation_duration') or
                telephony_data.get('duration') or
                None
            ),
            'total_cost': (
                payload.get('total_cost') or
                execution_details.get('total_cost') or
                None
            ),
            'cost_breakdown': (
                payload.get('cost_breakdown') or
                execution_details.get('cost_breakdown') or
                {}
            ),
            'usage_breakdown': (
                payload.get('usage_breakdown') or
                execution_details.get('usage_breakdown') or
                {}
            ),
            'context_details': (
                payload.get('context_details') or
                execution_details.get('context_details') or
                {}
            ),
            'latency_data': (
                payload.get('latency_data') or
                execution_details.get('latency_data') or
                {}
            ),
            'agent_id': (
                payload.get('agent_id') or
                execution_details.get('agent_id') or
                None
            ),
            'batch_id': (
                payload.get('batch_id') or
                execution_details.get('batch_id') or
                None
            ),
            'created_at': (
                payload.get('created_at') or
                execution_details.get('created_at') or
                None
            ),
            'updated_at': (
                payload.get('updated_at') or
                execution_details.get('updated_at') or
                None
            ),
            'answered_by_voice_mail': (
                payload.get('answered_by_voice_mail') or
                execution_details.get('answered_by_voice_mail') or
                None
            ),
            'error_message': (
                payload.get('error_message') or
                execution_details.get('error_message') or
                None
            ),
            'agent_extraction': (
                payload.get('agent_extraction') or
                execution_details.get('agent_extraction') or
                None
            ),
            'provider': (
                payload.get('provider') or
                execution_details.get('provider') or
                telephony_data.get('provider') or
                None
            )
        }
        
        # Store by execution_id (allows updates to same execution)
        webhook_data[execution_id] = entry
        
        # Also maintain a chronological list
        if 'all_webhooks' not in webhook_data:
            webhook_data['all_webhooks'] = []
        
        # Add to chronological list (most recent first)
        webhook_data['all_webhooks'].insert(0, {
            'execution_id': execution_id,
            'candidate_id': candidate_id,
            'timestamp': entry['timestamp'],
            'status': entry['status']
        })
        
        # Remove duplicates from all_webhooks based on execution_id, keeping the most recent
        seen_execution_ids = set()
        unique_all_webhooks = []
        for webhook_entry in webhook_data['all_webhooks']:
            if webhook_entry['execution_id'] not in seen_execution_ids:
                unique_all_webhooks.append(webhook_entry)
                seen_execution_ids.add(webhook_entry['execution_id'])
        webhook_data['all_webhooks'] = unique_all_webhooks

        with open(webhook_data_file, 'w', encoding='utf-8') as f:
            json.dump(webhook_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved complete webhook data for execution {execution_id} to {webhook_data_file}")
        
        # Also save transcript separately with candidate info
        if entry.get('transcript'):
            save_transcript_separately(execution_id, entry['transcript'], candidate_id, payload)
        
        return True
    except Exception as e:
        import traceback
        print(f"⚠️  Error saving complete webhook data: {e}")
        traceback.print_exc()
        return False

def save_transcript_separately(execution_id: str, transcript: str, candidate_id: int = None, payload: dict = None):
    """
    Save transcript separately in data/transcripts.json
    Stores in data/transcripts.json organized by candidate_id and execution_id
    """
    try:
        data_dir = 'data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        transcripts_file = os.path.join(data_dir, 'transcripts.json')
        
        # Load existing transcripts
        transcripts_data = {}
        if os.path.exists(transcripts_file):
            try:
                with open(transcripts_file, 'r', encoding='utf-8') as f:
                    transcripts_data = json.load(f)
            except:
                transcripts_data = {}
        
        # Get candidate information
        candidate_info = {}
        if candidate_id:
            try:
                with open('data/candidates.json', 'r', encoding='utf-8') as f:
                    candidates_data = json.load(f)
                    candidate = next(
                        (c for c in candidates_data.get('candidates', []) if c.get('id') == candidate_id),
                        None
                    )
                    if candidate:
                        candidate_info = {
                            'candidate_id': candidate_id,
                            'name': candidate.get('name', 'Unknown'),
                            'position': candidate.get('position', 'Unknown'),
                            'phone': candidate.get('phone', 'Unknown'),
                            'email': candidate.get('email', 'Unknown')
                        }
            except:
                pass
        
        # Get phone numbers from payload
        telephony_data = (
            payload.get('telephony_data') or
            payload.get('data', {}).get('telephony_data') or
            payload.get('execution', {}).get('telephony_data') or
            {}
        ) if payload else {}
        
        caller_id = (
            telephony_data.get('from_number') or
            payload.get('agent_phone_number') if payload else None or
            payload.get('caller_id') if payload else None or
            None
        )
        
        recipient_phone = (
            telephony_data.get('to_number') or
            payload.get('recipient_phone_number') if payload else None or
            candidate_info.get('phone') if candidate_info else None or
            None
        )
        
        # Create transcript entry
        transcript_entry = {
            'execution_id': execution_id,
            'candidate_id': candidate_id,
            'candidate_name': candidate_info.get('name', 'Unknown'),
            'position': candidate_info.get('position', 'Unknown'),
            'candidate_phone': candidate_info.get('phone', 'Unknown'),
            'candidate_email': candidate_info.get('email', 'Unknown'),
            'caller_id': caller_id,
            'recipient_phone': recipient_phone,
            'transcript': transcript,
            'timestamp': datetime.now().isoformat(),
            'received_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': (
                payload.get('status') if payload else 'unknown' or
                payload.get('data', {}).get('status') if payload else None or
                'unknown'
            ),
            'call_duration': (
                telephony_data.get('duration') or
                payload.get('conversation_duration') if payload else None or
                None
            )
        }
        
        # Initialize structure if needed
        if 'by_candidate' not in transcripts_data:
            transcripts_data['by_candidate'] = {}
        
        # Organize by candidate_id, then by execution_id
        if candidate_id:
            candidate_key = str(candidate_id)
            if candidate_key not in transcripts_data['by_candidate']:
                transcripts_data['by_candidate'][candidate_key] = {
                    'candidate_id': candidate_id,
                    'candidate_name': candidate_info.get('name', 'Unknown'),
                    'position': candidate_info.get('position', 'Unknown'),
                    'phone': candidate_info.get('phone', 'Unknown'),
                    'email': candidate_info.get('email', 'Unknown'),
                    'transcripts': {}
                }
            
            transcripts_data['by_candidate'][candidate_key]['transcripts'][execution_id] = transcript_entry
        
        # Also maintain chronological list
        if 'all_transcripts' not in transcripts_data:
            transcripts_data['all_transcripts'] = []
        
        transcripts_data['all_transcripts'].insert(0, {
            'execution_id': execution_id,
            'candidate_id': candidate_id,
            'candidate_name': candidate_info.get('name', 'Unknown'),
            'position': candidate_info.get('position', 'Unknown'),
            'timestamp': transcript_entry['timestamp'],
            'caller_id': caller_id,
            'recipient_phone': recipient_phone
        })
        
        # Keep only last 1000 transcripts in chronological list
        transcripts_data['all_transcripts'] = transcripts_data['all_transcripts'][:1000]
        
        with open(transcripts_file, 'w', encoding='utf-8') as f:
            json.dump(transcripts_data, f, indent=2, ensure_ascii=False)
        print(f"📝 Saved transcript separately for execution {execution_id}")
    except Exception as e:
        import traceback
        print(f"⚠️  Error saving transcript separately: {e}")
        traceback.print_exc()

def validate_bolna_ip(func):
    """Decorator to validate requests come from Bolna AI IPs"""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Bolna AI authorized IP addresses
        authorized_ips = [
            '13.200.45.61',
            '65.2.44.157',
            '34.194.233.253',
            '13.204.98.4',
            '43.205.31.43',
            '107.20.118.52'
        ]
        
        # Get client IP
        client_ip = request.remote_addr
        
        # Check if request is forwarded through ngrok or proxy
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            # Extract original IP from X-Forwarded-For (first IP in chain)
            original_ip = forwarded_for.split(',')[0].strip()
            client_ip = original_ip
        
        # Check for ngrok forwarding indicators
        is_ngrok = (
            request.headers.get('X-Forwarded-Proto') or
            request.headers.get('Ngrok-Skip-Browser-Warning')
        )
        
        # Allow localhost/127.0.0.1 for local development
        if client_ip in ['127.0.0.1', 'localhost', '::1'] or request.remote_addr in ['127.0.0.1', 'localhost', '::1']:
            print(f"✅ Local request allowed from: {client_ip}")
            return func(*args, **kwargs)
        
        # Allow if IP is authorized OR if it's ngrok (we trust ngrok)
        if client_ip in authorized_ips or is_ngrok:
            if is_ngrok:
                print(f"✅ Ngrok request allowed (original IP: {client_ip})")
            else:
                print(f"✅ Authorized IP: {client_ip}")
            return func(*args, **kwargs)
        
        # Reject unauthorized requests
        print(f"❌ Unauthorized webhook request from IP: {client_ip}")
        if forwarded_for:
            print(f"   X-Forwarded-For: {forwarded_for}")
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Request not from authorized IP address'
        }), 403
    
    return wrapper


# ============================================================================
# API Routes
# ============================================================================

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """Get all candidates"""
    try:
        json_path = 'data/candidates.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'candidates': [],
            'availableSlots': []
        }), 500

@app.route('/api/reset-statuses', methods=['POST'])
def reset_candidate_statuses():
    """Reset ALL candidate statuses to 'pending'"""
    try:
        json_path = 'data/candidates.json'
        if not os.path.exists(json_path):
            print(f"⚠️  Candidates file not found: {json_path}")
            return jsonify({
                'success': False,
                'error': 'Candidates file not found'
            }), 404
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reset ALL statuses to 'pending' (not just 'calling')
        reset_count = 0
        for candidate in data['candidates']:
            old_status = candidate.get('status', 'unknown')
            if old_status != 'pending':
                candidate['status'] = 'pending'
                reset_count += 1
                print(f"  ✅ Reset candidate {candidate['id']} ({candidate.get('name', 'Unknown')}): {old_status} → pending")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reset {reset_count} candidate statuses to pending")
        return jsonify({
            'success': True,
            'message': f'Reset {reset_count} candidate statuses to pending',
            'reset_count': reset_count
        })
    except Exception as e:
        print(f"❌ Error resetting statuses: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/call', methods=['POST'])
def make_call():
    """Make a call using Bolna AI"""
    if not agent:
        return jsonify({
            'success': False,
            'error': 'Bolna Agent not initialized. Check your .env file.'
        }), 500

    try:
        data = request.json
        candidate_id = data.get('candidateId')
        phone = data.get('phone')
        name = data.get('name')
        interview_date = data.get('interviewDate')
        interview_time = data.get('interviewTime')

        # Read available slots from JSON
        with open('data/candidates.json', 'r', encoding='utf-8') as f:
            candidates_data = json.load(f)
        
        # Get candidate data and position
        candidate = next(
            (c for c in candidates_data['candidates'] if c['id'] == candidate_id),
            None
        )
        
        position = candidate.get('position', '') if candidate else ''
        
        alternative_slots = []
        if candidate:
            current_datetime = candidate['scheduledInterview']['datetime']
            
            # Check if candidate has specific rescheduling slots assigned
            if 'reschedulingSlots' in candidate and candidate['reschedulingSlots']:
                # Use candidate-specific rescheduling slots
                slot_ids = candidate['reschedulingSlots']
                
                # Create a map of slot IDs to slots for quick lookup
                slot_map = {slot['id']: slot for slot in candidates_data['availableSlots']}
                
                # Get the specific slots assigned to this candidate
                alternative_slots = [
                    slot_map[slot_id]['datetime']
                    for slot_id in slot_ids
                    if slot_id in slot_map and slot_map[slot_id]['datetime'] != current_datetime
                ]
                print(f"📅 Using candidate-specific rescheduling slots for candidate {candidate_id}: {slot_ids}")
            else:
                # Fallback: Use all available slots (excluding current)
                alternative_slots = [
                    slot['datetime']
                    for slot in candidates_data['availableSlots']
                    if slot['datetime'] != current_datetime
                ][:3]  # Limit to 3 slots
                print(f"⚠️  No reschedulingSlots assigned to candidate {candidate_id}, using default slots")

        # Get caller ID from environment (optional - Twilio can use default)
        caller_id = os.getenv('CALLER_ID', None)
        
        if caller_id:
            print(f"📞 Using caller ID from .env: {caller_id}")
        else:
            print("📞 No CALLER_ID set - Twilio will use your default registered number")

        # Make the call using the correct API structure
        try:
            result = agent.make_call(
                phone_number=phone,
                caller_id=caller_id,
                candidate_name=name,
                interview_date=interview_date,
                interview_time=interview_time,
                alternative_slots=alternative_slots,
                position=position
            )
        except ValueError as e:
            # Handle wallet balance and other API errors
            error_message = str(e)
            return jsonify({
                'success': False,
                'error': error_message,
                'error_type': 'wallet_balance' if 'wallet' in error_message.lower() or 'balance' in error_message.lower() else 'api_error'
            }), 402 if 'wallet' in error_message.lower() or 'balance' in error_message.lower() else 500

        execution_id = result.get('execution_id')
        
        # Save execution_id to candidate_id mapping for webhook processing
        if execution_id and candidate_id:
            save_execution_mapping(execution_id, candidate_id, phone)
        
        return jsonify({
            'success': True,
            'executionId': execution_id,
            'message': 'Call initiated successfully',
            'alternativeSlots': alternative_slots
        })
    except Exception as e:
        import traceback
        print(f"Error making call: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/call-status/<execution_id>', methods=['GET'])
def get_call_status(execution_id):
    """Get call execution status"""
    if not agent:
        return jsonify({
            'success': False,
            'error': 'Bolna Agent not initialized'
        }), 500
    
    try:
        details = agent.get_execution_details(execution_id)
        return jsonify({
            'success': True,
            'details': details
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/webhook', methods=['POST'])
@app.route('/', methods=['POST'])
@validate_bolna_ip
def webhook_handler():
    """
    Webhook endpoint to receive real-time call execution data from Bolna Voice AI
    """
    try:
        payload = request.json
        print(f"📨 Received webhook payload")
        print(f"   Payload keys: {list(payload.keys()) if isinstance(payload, dict) else 'Not a dict'}")
        
        # Extract execution_id from payload FIRST (needed for storage)
        execution_id = (
            payload.get('execution_id') or 
            payload.get('executionId') or 
            payload.get('data', {}).get('execution_id') or
            payload.get('data', {}).get('executionId')
        )
        
        if not execution_id:
            print(f"⚠️  No execution_id found in webhook payload")
            print(f"   Payload: {json.dumps(payload, indent=2)}")
            return jsonify({
                'success': False,
                'error': 'execution_id not found in payload'
            }), 400
        
        print(f"🔍 Processing webhook for execution_id: {execution_id}")
        
        # Find candidate mapping
        mapping = get_execution_mapping(execution_id)
        candidate_id = None
        
        if not mapping:
            # Try to find by phone number as fallback
            phone_number = (
                payload.get('recipient_phone_number') or
                payload.get('phone_number') or
                payload.get('phone') or
                payload.get('data', {}).get('recipient_phone_number') or
                None
            )
            
            if phone_number:
                try:
                    with open('data/candidates.json', 'r', encoding='utf-8') as f:
                        candidates_data = json.load(f)
                    candidate = next(
                        (c for c in candidates_data['candidates'] if c['phone'] == phone_number),
                        None
                    )
                    if candidate:
                        candidate_id = candidate['id']
                        # Save mapping for future use
                        save_execution_mapping(execution_id, candidate_id, phone_number)
                        print(f"✅ Found candidate by phone: {candidate_id}")
                except:
                    pass
            
            if not candidate_id:
                print(f"⚠️  No mapping found for execution_id: {execution_id}")
                # Still save webhook data even if no candidate mapping
                save_webhook_data(execution_id, payload, None)
                return jsonify({
                    'success': False,
                    'error': 'Could not determine candidate for this execution'
                }), 404
        else:
            candidate_id = mapping['candidate_id']
            print(f"✅ Found mapping: execution {execution_id} -> candidate {candidate_id}")
        
        # Save webhook data FIRST (before processing)
        save_webhook_data(execution_id, payload, candidate_id)
        
        # Extract execution details from payload
        execution_details = payload.get('data') or payload.get('execution') or payload
        
        # Extract status
        status = (
            execution_details.get('status') or
            payload.get('status') or
            'unknown'
        ).lower()
        
        print(f"📊 Call status: {status}")
        
        # Extract transcript if available
        transcript = (
            execution_details.get('transcript') or
            execution_details.get('conversation_transcript') or
            payload.get('transcript') or
            ''
        )
        
        # Extract extracted_data if available
        extracted_data = (
            execution_details.get('extracted_data') or
            payload.get('extracted_data') or
            {}
        )
        
        # Only process completed calls
        if status in ['completed', 'ended', 'stopped', 'finished']:
            print(f"✅ Call completed. Processing outcome...")
            
            # Parse the outcome
            outcome = parse_call_outcome(execution_details, transcript)
            print(f"📊 Parsed outcome: {outcome}")
            
            # Determine final status
            final_status = outcome['status'] if outcome['status'] != 'pending' else 'pending'
            
            # Log extracted data for debugging
            if extracted_data and extracted_data.get('call_outcome'):
                print(f"📋 Structured Extraction Data:")
                print(f"   Call Outcome: {extracted_data.get('call_outcome')}")
                print(f"   Original Slot: {extracted_data.get('original_slot')}")
                print(f"   Final Slot: {extracted_data.get('final_slot')}")
                print(f"   Notes: {extracted_data.get('notes', 'N/A')}")
            
            # Update candidate status
            success = update_candidate_in_json(
                candidate_id,
                final_status,
                outcome.get('updated_interview')
            )
            
            if success:
                print(f"✅ Candidate {candidate_id} updated: {final_status}")
                if final_status == 'rescheduled' and outcome.get('updated_interview'):
                    print(f"   📅 New interview slot: {outcome['updated_interview'].get('datetime', 'N/A')}")
                
                return jsonify({
                    'success': True,
                    'message': f'Candidate {candidate_id} updated successfully',
                    'status': final_status,
                    'execution_id': execution_id,
                    'extracted_data': extracted_data if extracted_data else None
                })
            else:
                print(f"❌ Failed to update candidate {candidate_id}")
                return jsonify({
                    'success': False,
                    'error': 'Failed to update candidate'
                }), 500
        
        elif status in ['no_answer', 'no-answer', 'no answer']:
            print(f"📞 Call status: NO ANSWER")
            # Set status to "no_answer" to display it
            update_candidate_in_json(candidate_id, 'no_answer')
            return jsonify({
                'success': True,
                'message': f'Call ended: No Answer',
                'status': 'no_answer',
                'execution_id': execution_id,
                'display_status': 'No Answer'
            })
        elif status in ['failed', 'error', 'cancelled', 'canceled', 'cut', 'terminated', 'hung_up', 'disconnected', 'busy', 'rejected']:
            print(f"❌ Call ended ({status}). Resetting candidate status...")
            update_candidate_in_json(candidate_id, 'pending')
            return jsonify({
                'success': True,
                'message': f'Call {status}. Candidate reset to pending',
                'status': 'pending',
                'execution_id': execution_id
            })
        
        else:
            # Call is still in progress (initiated, ringing, in_progress, etc.)
            print(f"⏳ Call status: {status} (still in progress)")
            # If status is unknown but we have a transcript, try to process it anyway
            if transcript and len(transcript) > 50:
                print(f"⚠️  Unknown status but transcript available. Attempting to process...")
                try:
                    outcome = parse_call_outcome(execution_details, transcript)
                    final_status = outcome['status'] if outcome['status'] != 'pending' else 'pending'
                    if final_status != 'pending':
                        update_candidate_in_json(candidate_id, final_status, outcome.get('updated_interview'))
                        return jsonify({
                            'success': True,
                            'message': f'Processed call with unknown status. Candidate updated to {final_status}',
                            'status': final_status,
                            'execution_id': execution_id
                        })
                except:
                    pass
            
            return jsonify({
                'success': True,
                'message': f'Call status received: {status}',
                'status': status,
                'execution_id': execution_id
            })
    
    except Exception as e:
        import traceback
        print(f"❌ Error processing webhook: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/webhook/status', methods=['GET'])
def webhook_status():
    """Check webhook configuration status"""
    try:
        # Check execution mappings
        mapping_count = 0
        if os.path.exists('execution_mapping.json'):
            with open('execution_mapping.json', 'r', encoding='utf-8') as f:
                mappings = json.load(f)
                mapping_count = len(mappings)
        
        return jsonify({
            'success': True,
            'webhook_configured': True,
            'execution_mappings': mapping_count,
            'message': 'Webhook endpoint is ready'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/call/<execution_id>/check-status', methods=['POST'])
def manually_check_call_status(execution_id):
    """Manually check and update call status (fallback if webhook doesn't fire)"""
    if not agent:
        return jsonify({
            'success': False,
            'error': 'Bolna Agent not initialized'
        }), 500
    
    try:
        # Get execution details from Bolna AI
        details = agent.get_execution_details(execution_id)
        status = details.get('status', '').lower()
        
        # Get candidate mapping
        mapping = get_execution_mapping(execution_id)
        if not mapping:
            return jsonify({
                'success': False,
                'error': 'No candidate mapping found for this execution'
            }), 404
        
        candidate_id = mapping['candidate_id']
        
        # Process based on status
        if status in ['completed', 'ended', 'stopped', 'finished']:
            transcript = agent.get_transcript(execution_id) or details.get('transcript', '')
            outcome = parse_call_outcome(details, transcript)
            final_status = outcome['status'] if outcome['status'] != 'pending' else 'pending'
            
            success = update_candidate_in_json(
                candidate_id,
                final_status,
                outcome.get('updated_interview')
            )
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Call completed. Candidate updated to {final_status}',
                    'status': final_status,
                    'execution_id': execution_id
                })
        
        elif status in ['no_answer', 'no-answer', 'no answer']:
            # Set status to "no_answer" to display it
            update_candidate_in_json(candidate_id, 'no_answer')
            return jsonify({
                'success': True,
                'message': f'Call ended: No Answer',
                'status': 'no_answer',
                'execution_id': execution_id,
                'display_status': 'No Answer'
            })
        elif status in ['failed', 'error', 'cancelled', 'canceled', 'cut', 'terminated']:
            update_candidate_in_json(candidate_id, 'pending')
            return jsonify({
                'success': True,
                'message': f'Call {status}. Candidate reset to pending',
                'status': 'pending',
                'execution_id': execution_id
            })
        
        else:
            return jsonify({
                'success': True,
                'message': f'Call status: {status} (still in progress)',
                'status': status,
                'execution_id': execution_id
            })
    
    except Exception as e:
        import traceback
        print(f"Error checking call status: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/candidate/<candidate_id>/reset', methods=['POST'])
def reset_candidate_status(candidate_id):
    """Reset a candidate's status to 'pending' ONLY - no other changes"""
    try:
        candidate_id_int = int(candidate_id)
        json_path = 'data/candidates.json'
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        candidate = next((c for c in data['candidates'] if c['id'] == candidate_id_int), None)
        if not candidate:
            return jsonify({
                'success': False,
                'error': 'Candidate not found'
            }), 404
        
        old_status = candidate.get('status', 'unknown')
        # ONLY change status to pending - preserve everything else
        candidate['status'] = 'pending'
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Reset candidate {candidate_id} status: {old_status} → pending")
        return jsonify({
            'success': True,
            'message': f'Candidate {candidate_id} status reset to pending'
        })
    except Exception as e:
        import traceback
        print(f"❌ Error resetting candidate status: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/candidate/<candidate_id>', methods=['DELETE'])
def delete_candidate(candidate_id):
    """Delete a candidate from the system"""
    try:
        candidate_id_int = int(candidate_id)
        json_path = 'data/candidates.json'
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        candidate = next((c for c in data['candidates'] if c['id'] == candidate_id_int), None)
        if not candidate:
            return jsonify({
                'success': False,
                'error': 'Candidate not found'
            }), 404
        
        candidate_name = candidate.get('name', 'Unknown')
        # Remove candidate from list
        data['candidates'] = [c for c in data['candidates'] if c['id'] != candidate_id_int]
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"🗑️  Deleted candidate {candidate_id} ({candidate_name})")
        return jsonify({
            'success': True,
            'message': f'Candidate {candidate_name} deleted successfully'
        })
    except Exception as e:
        import traceback
        print(f"❌ Error deleting candidate: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/candidate/add', methods=['POST'])
def add_candidate():
    """Add a new candidate"""
    try:
        json_path = 'data/candidates.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        candidate_data = request.json
        
        # Validate required fields
        required_fields = ['name', 'phone', 'email', 'position', 'scheduledInterview']
        for field in required_fields:
            if field not in candidate_data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Generate new ID
        max_id = max([c['id'] for c in data['candidates']], default=0)
        new_id = max_id + 1
        
        # Create new candidate
        new_candidate = {
            'id': new_id,
            'name': candidate_data['name'],
            'phone': candidate_data['phone'],
            'email': candidate_data['email'],
            'position': candidate_data['position'],
            'status': 'pending',
            'scheduledInterview': candidate_data['scheduledInterview'],
            'applicationDate': candidate_data.get('applicationDate', datetime.now().strftime('%Y-%m-%d')),
            'reschedulingSlots': candidate_data.get('reschedulingSlots', [])
        }
        
        data['candidates'].append(new_candidate)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Added new candidate: {new_candidate['name']} (ID: {new_id})")
        return jsonify({
            'success': True,
            'message': f'Candidate added successfully',
            'candidate_id': new_id
        })
    except Exception as e:
        import traceback
        print(f"❌ Error adding candidate: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/candidate/<candidate_id>/rescheduling-slots', methods=['PUT'])
def update_rescheduling_slots(candidate_id):
    """Update rescheduling slots for a candidate"""
    try:
        json_path = 'data/candidates.json'
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        candidate = next((c for c in data['candidates'] if c['id'] == int(candidate_id)), None)
        if not candidate:
            return jsonify({
                'success': False,
                'error': 'Candidate not found'
            }), 404
        
        slot_ids = request.json.get('reschedulingSlots', [])
        
        # Validate slot IDs exist
        available_slot_ids = [s['id'] for s in data.get('availableSlots', [])]
        invalid_ids = [sid for sid in slot_ids if sid not in available_slot_ids]
        if invalid_ids:
            return jsonify({
                'success': False,
                'error': f'Invalid slot IDs: {invalid_ids}'
            }), 400
        
        candidate['reschedulingSlots'] = slot_ids
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated rescheduling slots for candidate {candidate_id}: {slot_ids}")
        return jsonify({
            'success': True,
            'message': f'Rescheduling slots updated for candidate {candidate_id}',
            'reschedulingSlots': slot_ids
        })
    except Exception as e:
        import traceback
        print(f"❌ Error updating rescheduling slots: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/executions', methods=['GET'])
def get_batch_executions():
    """Get batch executions from Bolna AI"""
    if not agent:
        return jsonify({
            'success': False,
            'error': 'Bolna Agent not initialized'
        }), 500
    
    try:
        batch_id = request.args.get('batch_id')
        limit = request.args.get('limit', 10, type=int)
        
        # Use the list_executions method from BolnaAgent
        result = agent.list_executions(
            batch_id=batch_id,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'executions': result.get('executions', []),
            'total': result.get('total', 0)
        })
    except Exception as e:
        import traceback
        print(f"Error fetching batch executions: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Flask API Server...")
    print("📡 Server will run on http://localhost:5000")
    print("📝 Webhook endpoint: http://localhost:5000/api/webhook")
    app.run(debug=True, port=5000)

