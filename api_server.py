"""
Flask API Server for Bolna Calling Agent
Bridges Next.js frontend with Bolna AI Python backend
"""

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
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
                payload.get('user_number') or  # Bolna AI webhook format uses "user_number"
                payload.get('recipient_phone_number') or
                payload.get('phone_number') or
                payload.get('phone') or
                execution_details.get('user_number') or
                execution_details.get('recipient_phone_number') or
                telephony_data.get('to_number') or
                None
            ),
            'agent_phone_number': (
                payload.get('agent_number') or  # Bolna AI webhook format uses "agent_number"
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

@app.route('/api/health', methods=['GET'])
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify Flask backend is running"""
    try:
        # Check if candidates file exists and is readable
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, 'data', 'candidates.json')
        
        health_status = {
            'status': 'healthy',
            'service': 'Bolna Calling Agent API',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'checks': {
                'api_server': True,
                'bolna_agent': agent is not None,
                'candidates_file': os.path.exists(json_path),
                'candidates_file_readable': os.access(json_path, os.R_OK) if os.path.exists(json_path) else False,
                'candidates_file_writable': os.access(json_path, os.W_OK) if os.path.exists(json_path) else False
            }
        }
        
        # Try to read candidates file to verify it's valid JSON
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    health_status['checks']['candidates_count'] = len(data.get('candidates', []))
                    health_status['checks']['available_slots_count'] = len(data.get('availableSlots', []))
            except Exception as e:
                health_status['checks']['candidates_file_valid'] = False
                health_status['checks']['candidates_file_error'] = str(e)
        
        # Determine overall health status
        all_checks_pass = (
            health_status['checks']['api_server'] and
            health_status['checks']['candidates_file'] and
            health_status['checks']['candidates_file_readable']
        )
        
        if not all_checks_pass:
            health_status['status'] = 'degraded'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        import traceback
        print(f"❌ Health check error: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'unhealthy',
            'service': 'Bolna Calling Agent API',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

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
        # Use absolute path to ensure we're writing to the correct location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, 'data', 'candidates.json')
        
        print(f"📝 Reset statuses - Using path: {json_path}")
        
        if not os.path.exists(json_path):
            print(f"⚠️  Candidates file not found: {json_path}")
            return jsonify({
                'success': False,
                'error': f'Candidates file not found: {json_path}'
            }), 404
        
        # Check file permissions
        if not os.access(json_path, os.W_OK):
            print(f"⚠️  No write permission for file: {json_path}")
            return jsonify({
                'success': False,
                'error': f'No write permission for file: {json_path}'
            }), 403
            
        # Read current data
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reset ALL statuses to 'pending' and restore original interviews if rescheduled
        reset_count = 0
        changes = []
        for candidate in data['candidates']:
            old_status = candidate.get('status', 'unknown')
            if old_status != 'pending':
                # If candidate was rescheduled, restore original interview
                if 'originalInterview' in candidate and candidate['originalInterview']:
                    candidate['scheduledInterview'] = candidate['originalInterview'].copy()
                    del candidate['originalInterview']
                    changes.append(f"{candidate.get('name', 'Unknown')}: {old_status} → pending (original interview restored)")
                else:
                    changes.append(f"{candidate.get('name', 'Unknown')}: {old_status} → pending")
                
                candidate['status'] = 'pending'
                reset_count += 1
                print(f"  ✅ Reset candidate {candidate['id']} ({candidate.get('name', 'Unknown')}): {old_status} → pending")
        
        # Write back to file
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Successfully wrote {reset_count} changes to {json_path}")
        except PermissionError as pe:
            print(f"❌ Permission error writing file: {pe}")
            return jsonify({
                'success': False,
                'error': f'Permission denied writing to file: {str(pe)}'
            }), 403
        except Exception as write_error:
            print(f"❌ Error writing file: {write_error}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Error writing file: {str(write_error)}'
            }), 500
        
        # Verify the file was written correctly
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                verify_data = json.load(f)
            verify_pending = sum(1 for c in verify_data.get('candidates', []) if c.get('status') == 'pending')
            print(f"✅ Verified: {verify_pending} candidates now have 'pending' status")
        except Exception as verify_error:
            print(f"⚠️  Could not verify file write: {verify_error}")
        
        print(f"✅ Reset {reset_count} candidate statuses to pending")
        return jsonify({
            'success': True,
            'message': f'Reset {reset_count} candidate statuses to pending',
            'reset_count': reset_count,
            'changes': changes
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
                # Use candidate-specific rescheduling slots ONLY
                slot_ids = candidate['reschedulingSlots']
                
                # Create a map of slot IDs to slots for quick lookup
                slot_map = {slot['id']: slot for slot in candidates_data['availableSlots']}
                
                # Validate and filter: ONLY include slots that:
                # 1. Exist in the slot_map (valid slot ID)
                # 2. Are not the current scheduled interview datetime
                valid_slots = []
                invalid_slot_ids = []
                
                for slot_id in slot_ids:
                    if slot_id not in slot_map:
                        invalid_slot_ids.append(slot_id)
                        print(f"⚠️  Slot ID {slot_id} not found in availableSlots for candidate {candidate_id}")
                        continue
                    
                    slot_datetime = slot_map[slot_id]['datetime']
                    if slot_datetime == current_datetime:
                        print(f"⚠️  Skipping slot ID {slot_id} (same as current interview) for candidate {candidate_id}")
                        continue
                    
                    valid_slots.append(slot_datetime)
                
                alternative_slots = valid_slots
                
                if invalid_slot_ids:
                    print(f"⚠️  Invalid slot IDs for candidate {candidate_id}: {invalid_slot_ids}")
                
                print(f"📅 Using candidate-specific rescheduling slots for candidate {candidate_id}:")
                print(f"   Requested slot IDs: {slot_ids}")
                print(f"   Valid slot datetimes: {alternative_slots}")
                
                if not alternative_slots:
                    print(f"❌ WARNING: No valid alternative slots found for candidate {candidate_id} after filtering!")
            else:
                # Fallback: Use all available slots (excluding current)
                alternative_slots = [
                    slot['datetime']
                    for slot in candidates_data['availableSlots']
                    if slot['datetime'] != current_datetime
                ][:3]  # Limit to 3 slots
                print(f"⚠️  No reschedulingSlots assigned to candidate {candidate_id}, using default slots: {alternative_slots}")

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

        # Bolna AI API may return "id" or "execution_id" in response
        execution_id = result.get('id') or result.get('execution_id') or result.get('executionId')
        
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
    """Get call execution status - checks local webhook data first, then Bolna API"""
    # First, check if we have webhook data locally (faster and more reliable)
    try:
        webhook_data_file = os.path.join('data', 'webhook_data.json')
        if os.path.exists(webhook_data_file):
            with open(webhook_data_file, 'r', encoding='utf-8') as f:
                webhook_data = json.load(f)
                if execution_id in webhook_data:
                    stored_data = webhook_data[execution_id]
                    print(f"✅ Found execution {execution_id} in local webhook data")
                    return jsonify({
                        'success': True,
                        'details': {
                            'execution_id': execution_id,
                            'status': stored_data.get('status', 'unknown'),
                            'transcript': stored_data.get('transcript', ''),
                            'extracted_data': stored_data.get('extracted_data', {}),
                            'summary': stored_data.get('summary', ''),
                            'conversation_duration': stored_data.get('conversation_duration'),
                            'total_cost': stored_data.get('total_cost'),
                            'recording_url': stored_data.get('recording_url'),
                            'telephony_data': stored_data.get('telephony_data', {}),
                            'from_webhook': True  # Flag to indicate this is from webhook data
                        }
                    })
    except Exception as e:
        print(f"⚠️  Error reading local webhook data: {e}")
    
    # If not found locally, try Bolna API (for active calls)
    if not agent:
        return jsonify({
            'success': False,
            'error': 'Bolna Agent not initialized'
        }), 500
    
    try:
        details = agent.get_execution_details(execution_id)
        return jsonify({
            'success': True,
            'details': details,
            'from_webhook': False  # Flag to indicate this is from API
        })
    except requests.exceptions.RequestException as e:
        # Handle 404 specifically - execution may not exist or may have expired
        # 404s are expected for expired executions, so we handle them gracefully without error logging
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
            print(f"⚠️  Execution {execution_id} not found or expired (404) - this is expected for expired executions")
            return jsonify({
                'success': False,
                'error': 'Execution not found or expired',
                'execution_id': execution_id,
                'status_code': 404,
                'message': 'This execution ID may have expired or does not exist in Bolna AI system'
            }), 404
        # Handle other HTTP errors (non-404)
        error_msg = str(e)
        status_code = 500
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            try:
                error_data = e.response.json()
                error_msg = error_data.get('detail', error_data.get('message', str(e)))
            except:
                error_msg = e.response.text or str(e)
        print(f"❌ Error fetching execution details: {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg,
            'status_code': status_code
        }), status_code
    except Exception as e:
        import traceback
        print(f"❌ Unexpected error fetching call status: {e}")
        traceback.print_exc()
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
        # Bolna AI uses "id" as the field name in webhook payloads
        execution_id = (
            payload.get('id') or  # Bolna AI webhook format uses "id"
            payload.get('execution_id') or 
            payload.get('executionId') or 
            payload.get('data', {}).get('id') or
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
            # Bolna AI uses "user_number" as the field name
            phone_number = (
                payload.get('user_number') or  # Bolna AI webhook format uses "user_number"
                payload.get('recipient_phone_number') or
                payload.get('phone_number') or
                payload.get('phone') or
                payload.get('telephony_data', {}).get('to_number') or
                payload.get('data', {}).get('user_number') or
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
        # Bolna AI sends flat payload, so use payload directly if no nested structure
        execution_details = payload.get('data') or payload.get('execution') or payload
        
        # Extract status (Bolna AI uses "status" directly in payload)
        status = (
            payload.get('status') or
            execution_details.get('status') or
            'unknown'
        ).lower()
        
        print(f"📊 Call status: {status}")
        
        # Extract transcript if available
        transcript = (
            payload.get('transcript') or
            payload.get('conversation_transcript') or
            execution_details.get('transcript') or
            execution_details.get('conversation_transcript') or
            ''
        )
        
        # Extract extracted_data if available
        extracted_data = (
            payload.get('extracted_data') or
            execution_details.get('extracted_data') or
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
    
    except requests.exceptions.RequestException as e:
        # Handle 404 specifically - execution may not exist or may have expired
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
            print(f"⚠️  Execution {execution_id} not found or expired (404)")
            return jsonify({
                'success': False,
                'error': 'Execution not found or expired',
                'execution_id': execution_id,
                'status_code': 404,
                'message': 'This execution ID may have expired or does not exist in Bolna AI system'
            }), 404
        # Handle other HTTP errors
        error_msg = str(e)
        status_code = 500
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            try:
                error_data = e.response.json()
                error_msg = error_data.get('detail', error_data.get('message', str(e)))
            except:
                error_msg = e.response.text or str(e)
        import traceback
        print(f"❌ Error checking call status: {error_msg}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': error_msg,
            'status_code': status_code
        }), status_code
    except Exception as e:
        import traceback
        print(f"❌ Unexpected error checking call status: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/candidate/<candidate_id>/reset', methods=['POST'])
def reset_candidate_status(candidate_id):
    """Reset a candidate's status to 'pending' and restore original interview if rescheduled"""
    try:
        candidate_id_int = int(candidate_id)
        # Use absolute path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, 'data', 'candidates.json')
        
        print(f"📝 Reset candidate {candidate_id} - Using path: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        candidate = next((c for c in data['candidates'] if c['id'] == candidate_id_int), None)
        if not candidate:
            return jsonify({
                'success': False,
                'error': 'Candidate not found'
            }), 404
        
        old_status = candidate.get('status', 'unknown')
        had_original = 'originalInterview' in candidate and candidate['originalInterview']
        
        # If candidate was rescheduled, restore original interview
        if had_original:
            print(f"🔄 Restoring original interview for candidate {candidate_id}")
            original_interview = candidate['originalInterview'].copy()
            candidate['scheduledInterview'] = original_interview
            # Remove the originalInterview field since we're resetting
            del candidate['originalInterview']
            print(f"   Restored interview: {candidate['scheduledInterview']['datetime']}")
        
        # Set status to pending
        candidate['status'] = 'pending'
        
        # Write back to file
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            message = f'Candidate {candidate_id} status reset to pending'
            if had_original:
                message += ' and original interview restored'
            print(f"✅ {message}")
        except Exception as write_error:
            print(f"❌ Error writing file: {write_error}")
            return jsonify({
                'success': False,
                'error': f'Error writing file: {str(write_error)}'
            }), 500
        
        return jsonify({
            'success': True,
            'message': message
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
    """
    Get All Voice AI Agent Executions API
    Retrieve all executions performed by a specific agent using Bolna APIs.
    Supports pagination with page_number and page_size query parameters.
    
    Query Parameters:
        - agent_id (optional): Filter executions for a specific agent
        - page_number (optional, default: 1): Page number for pagination
        - page_size (optional, default: 10): Number of results per page
        - all_pages (optional, default: false): If true, fetch all pages automatically
    
    Returns:
        JSON response with:
        - success: Boolean indicating if the request was successful
        - data: List of execution objects
        - page_number: Current page number
        - page_size: Number of results per page
        - total: Total number of executions
        - has_more: Boolean indicating if there are more pages
    """
    if not agent:
        return jsonify({
            'success': False,
            'error': 'Bolna Agent not initialized'
        }), 500
    
    try:
        # Get query parameters
        agent_id = request.args.get('agent_id', None)
        page_number = request.args.get('page_number', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        all_pages = request.args.get('all_pages', 'false').lower() == 'true'
        
        # Validate page_size (max typically 100)
        page_size = min(page_size, 100)
        
        if all_pages:
            # Fetch all pages automatically
            executions = agent.list_all_executions(
                agent_id=agent_id,
                page_size=page_size
            )
            
            return jsonify({
                'success': True,
                'data': executions,
                'total': len(executions),
                'page_number': 1,
                'page_size': len(executions),
                'has_more': False,
                'all_pages': True
            })
        else:
            # Fetch single page
            result = agent.list_executions(
                agent_id=agent_id,
                page_number=page_number,
                page_size=page_size
            )
            
            if not result:
                return jsonify({
                    'success': False,
                    'error': 'Failed to fetch executions'
                }), 500
            
            # Handle different response formats
            if isinstance(result, dict):
                return jsonify({
                    'success': True,
                    'data': result.get('data', []),
                    'page_number': result.get('page_number', page_number),
                    'page_size': result.get('page_size', page_size),
                    'total': result.get('total', 0),
                    'has_more': result.get('has_more', False)
                })
            elif isinstance(result, list):
                return jsonify({
                    'success': True,
                    'data': result,
                    'total': len(result),
                    'page_number': 1,
                    'page_size': len(result),
                    'has_more': False
                })
            else:
                return jsonify({
                    'success': True,
                    'data': [],
                    'total': 0,
                    'page_number': page_number,
                    'page_size': page_size,
                    'has_more': False
                })
    except requests.exceptions.RequestException as e:
        # Handle HTTP errors (404, 500, etc.)
        status_code = 500
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            try:
                error_data = e.response.json()
                error_msg = error_data.get('detail', error_data.get('message', str(e)))
            except:
                error_msg = e.response.text or str(e)
        
        print(f"❌ Error fetching executions: {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg,
            'status_code': status_code
        }), status_code
    except Exception as e:
        import traceback
        print(f"Error fetching batch executions: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    import os
    # Check if running in production (EC2)
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0' if not debug_mode else 'localhost')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print("🚀 Starting Flask API Server...")
    print(f"📡 Server will run on http://{host}:{port}")
    print(f"📝 Webhook endpoint: http://{host}:{port}/api/webhook")
    print(f"🔧 Debug mode: {debug_mode}")
    app.run(debug=debug_mode, host=host, port=port)

