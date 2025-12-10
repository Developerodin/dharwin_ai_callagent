"""
Flask API Server for Bolna Calling Agent
Bridges Next.js frontend with Bolna AI Python backend
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import subprocess
from bolna_agent import BolnaAgent
from update_candidate_status import update_candidate_in_json, parse_call_outcome
from config import BOLNA_API_KEY, AGENT_ID

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up logging to file
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, 'flask.log')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()  # Also log to console
    ]
)

# Create logger
logger = logging.getLogger(__name__)
app.logger.setLevel(logging.INFO)

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

@app.route('/api/', methods=['GET'])
@app.route('/api/logs', methods=['GET'])
def show_logs():
    """Display recent Flask backend logs"""
    try:
        # Get number of lines from query parameter (default 100)
        lines = request.args.get('lines', 100, type=int)
        lines = min(lines, 1000)  # Limit to 1000 lines max
        
        logs = ""
        log_source = ""
        
        # First, try to read from Flask log file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(base_dir, 'logs', 'flask.log')
        
        if os.path.exists(log_file):
            try:
                # Read last N lines from file
                with open(log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                    logs = ''.join(recent_lines)
                    log_source = f"Flask log file: {log_file}"
            except Exception as e:
                logs = f"⚠️ Error reading log file: {str(e)}\n\n"
        
        # If log file is empty or doesn't exist, try systemd journal as fallback
        if not logs or len(logs.strip()) == 0:
            try:
                # Try both service names (bolna-backend and bolna-flask)
                service_names = ['bolna-backend', 'bolna-flask']
                result = None
                used_service = None
                
                for service_name in service_names:
                    try:
                        # Test if service exists
                        test_result = subprocess.run(
                            ['journalctl', '-u', service_name, '-n', '1', '--no-pager'],
                            capture_output=True,
                            text=True,
                            timeout=2
                        )
                        if test_result.returncode == 0:
                            # Service exists, get logs
                            result = subprocess.run(
                                ['journalctl', '-u', service_name, '-n', str(lines), '--no-pager', '--no-hostname'],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            used_service = service_name
                            break
                    except FileNotFoundError:
                        # journalctl not found, skip
                        continue
                    except (subprocess.TimeoutExpired, PermissionError) as e:
                        continue
                
                if result and result.returncode == 0 and result.stdout:
                    logs = result.stdout
                    log_source = f"systemd service: {used_service}"
                else:
                    logs = "⚠️ No logs available.\n\n"
                    logs += "Log file not found and systemd journal not accessible.\n"
                    logs += f"Log file location: {log_file}\n"
                    logs += f"Try accessing logs manually:\n"
                    logs += f"  - Log file: tail -f {log_file}\n"
                    logs += f"  - Systemd: sudo journalctl -u bolna-backend -f"
            except Exception as e:
                logs = f"⚠️ Error retrieving logs: {str(e)}\n\n"
                logs += f"Log file location: {log_file}\n"
                logs += f"Try: tail -f {log_file}"
        
        # Add log source info at the top
        if log_source:
            logs = f"📋 Logs from {log_source}\n" + "=" * 80 + "\n\n" + logs
        
        # Return as HTML for easy viewing in browser
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Backend Logs - Bolna Calling Agent</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: #1e1e1e;
            color: #d4d4d4;
            margin: 0;
            padding: 20px;
        }}
        h1 {{
            color: #4ec9b0;
            border-bottom: 2px solid #4ec9b0;
            padding-bottom: 10px;
        }}
        .info {{
            background: #252526;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #007acc;
        }}
        .logs {{
            background: #252526;
            padding: 15px;
            border-radius: 5px;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 80vh;
            overflow-y: auto;
            font-size: 13px;
            line-height: 1.5;
        }}
        .refresh-btn {{
            background: #007acc;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px 5px;
            font-size: 14px;
        }}
        .refresh-btn:hover {{
            background: #005a9e;
        }}
        .endpoint-links {{
            margin: 15px 0;
        }}
        .endpoint-links a {{
            color: #4ec9b0;
            text-decoration: none;
            margin-right: 20px;
        }}
        .endpoint-links a:hover {{
            text-decoration: underline;
        }}
    </style>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <h1>📋 Backend Logs</h1>
    
    <div class="info">
        <strong>Service:</strong> Bolna Flask API Server<br>
        <strong>Showing last {lines} lines</strong><br>
        <strong>Auto-refresh:</strong> Every 30 seconds
    </div>
    
    <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Now</button>
    <a href="/api/health" class="refresh-btn" style="display: inline-block; text-decoration: none;">🏥 Health Check</a>
    
    <div class="endpoint-links">
        <a href="/api/health">/api/health</a> - Health check endpoint<br>
        <a href="/api/candidates">/api/candidates</a> - Get candidates<br>
        <a href="/api/logs?lines=50">Last 50 lines</a> | 
        <a href="/api/logs?lines=100">Last 100 lines</a> | 
        <a href="/api/logs?lines=500">Last 500 lines</a>
    </div>
    
    <div class="logs">{logs}</div>
    
    <script>
        // Auto-scroll to bottom
        window.onload = function() {{
            const logsDiv = document.querySelector('.logs');
            logsDiv.scrollTop = logsDiv.scrollHeight;
        }};
    </script>
</body>
</html>
        """
        
        return Response(html_content, mimetype='text/html')
        
    except Exception as e:
        error_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Error - Backend Logs</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .error {{ background: #fee; color: #c00; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Error</h1>
    <div class="error">Could not retrieve logs: {str(e)}</div>
</body>
</html>
        """
        return Response(error_html, mimetype='text/html'), 500

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
        
        # Check if request wants HTML (browser) or JSON (API)
        accept_header = request.headers.get('Accept', '')
        wants_html = 'text/html' in accept_header or 'html' in accept_header.lower()
        
        # If no Accept header or browser-like, return HTML
        if not accept_header or wants_html or request.headers.get('User-Agent', '').startswith(('Mozilla', 'Chrome', 'Safari', 'Firefox', 'Edge')):
            return generate_health_html(health_status, status_code), status_code
        
        # Otherwise return JSON for API clients
        return jsonify(health_status), status_code
        
    except Exception as e:
        import traceback
        print(f"❌ Health check error: {e}")
        traceback.print_exc()
        error_response = {
            'status': 'unhealthy',
            'service': 'Bolna Calling Agent API',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }
        
        # Return HTML error page if browser
        accept_header = request.headers.get('Accept', '')
        if 'text/html' in accept_header or not accept_header:
            return generate_health_html(error_response, 500), 500
        
        return jsonify(error_response), 500

def generate_health_html(health_data, status_code):
    """Generate HTML page for health check"""
    status = health_data.get('status', 'unknown')
    status_color = {
        'healthy': '#4caf50',
        'degraded': '#ff9800',
        'unhealthy': '#f44336'
    }.get(status, '#757575')
    
    status_icon = {
        'healthy': '✅',
        'degraded': '⚠️',
        'unhealthy': '❌'
    }.get(status, '❓')
    
    checks = health_data.get('checks', {})
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Health Check - Bolna Calling Agent</title>
    <meta http-equiv="refresh" content="30">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: {status_color};
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .status-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 1.1em;
            margin-top: 10px;
        }}
        .content {{
            padding: 30px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .info-card {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .info-card .label {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 8px;
        }}
        .info-card .value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}
        .checks-section {{
            margin-top: 30px;
        }}
        .checks-section h2 {{
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .check-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin-bottom: 10px;
            background: #f9f9f9;
            border-radius: 8px;
            border-left: 4px solid #ddd;
        }}
        .check-item.pass {{
            border-left-color: #4caf50;
            background: #f1f8f4;
        }}
        .check-item.fail {{
            border-left-color: #f44336;
            background: #fff5f5;
        }}
        .check-item .label {{
            font-weight: 500;
            color: #333;
        }}
        .check-item .status {{
            font-size: 1.2em;
        }}
        .timestamp {{
            text-align: center;
            color: #999;
            margin-top: 20px;
            font-size: 0.9em;
        }}
        .actions {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
        .btn {{
            display: inline-block;
            padding: 12px 24px;
            margin: 5px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: background 0.3s;
        }}
        .btn:hover {{
            background: #5568d3;
        }}
        .btn-secondary {{
            background: #764ba2;
        }}
        .btn-secondary:hover {{
            background: #5d3d7a;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{status_icon} {health_data.get('service', 'Bolna Calling Agent API')}</h1>
            <div class="status-badge">
                Status: <strong>{status.upper()}</strong>
            </div>
        </div>
        
        <div class="content">
            <div class="info-grid">
                <div class="info-card">
                    <div class="label">Version</div>
                    <div class="value">{health_data.get('version', '1.0.0')}</div>
                </div>
                <div class="info-card">
                    <div class="label">Candidates</div>
                    <div class="value">{checks.get('candidates_count', 0)}</div>
                </div>
                <div class="info-card">
                    <div class="label">Available Slots</div>
                    <div class="value">{checks.get('available_slots_count', 0)}</div>
                </div>
            </div>
            
            <div class="checks-section">
                <h2>System Checks</h2>
                {generate_check_items(checks)}
            </div>
            
            <div class="timestamp">
                Last checked: {health_data.get('timestamp', 'Unknown')}<br>
                Auto-refresh: Every 30 seconds
            </div>
            
            <div class="actions">
                <a href="/api/health" class="btn">🔄 Refresh</a>
                <a href="/api/" class="btn btn-secondary">📋 View Logs</a>
                <a href="/api/candidates" class="btn btn-secondary">👥 Candidates</a>
            </div>
        </div>
    </div>
</body>
</html>
    """
    return html

def generate_check_items(checks):
    """Generate HTML for check items"""
    items = []
    check_labels = {
        'api_server': 'API Server',
        'bolna_agent': 'Bolna AI Agent',
        'candidates_file': 'Candidates File',
        'candidates_file_readable': 'File Readable',
        'candidates_file_writable': 'File Writable',
        'candidates_file_valid': 'File Valid JSON',
    }
    
    for key, value in checks.items():
        if key in ['candidates_count', 'available_slots_count']:
            continue
        
        label = check_labels.get(key, key.replace('_', ' ').title())
        status_class = 'pass' if value else 'fail'
        status_icon = '✅' if value else '❌'
        
        items.append(f"""
                <div class="check-item {status_class}">
                    <span class="label">{label}</span>
                    <span class="status">{status_icon}</span>
                </div>
        """)
    
    return ''.join(items)

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """Get all candidates"""
    try:
        # Use absolute path to ensure consistency with update operations
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, 'data', 'candidates.json')
        
        # Fallback to relative if absolute doesn't exist
        if not os.path.exists(json_path):
            json_path = 'data/candidates.json'
        
        # Normalize to absolute path
        json_path = os.path.abspath(json_path)
        
        # Ensure file exists
        if not os.path.exists(json_path):
            print(f"❌ Candidates file not found at: {json_path}")
            # Try alternative locations
            alt_paths = [
                'data/candidates.json',
                os.path.join(os.getcwd(), 'data', 'candidates.json')
            ]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    json_path = os.path.abspath(alt_path)
                    print(f"✅ Found candidates file at alternative location: {json_path}")
                    break
            else:
                raise FileNotFoundError(f"Candidates file not found at any location")
        
        # Check file modification time
        file_mtime = os.path.getmtime(json_path)
        mtime_str = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Log current status counts for debugging
        status_counts = {}
        for candidate in data.get('candidates', []):
            status = candidate.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Log file path, modification time, and status breakdown  
        # This helps debug if read/write operations are using different files
        print(f"📖 [GET /api/candidates] Reading from: {json_path}")
        print(f"   File last modified: {mtime_str}")
        print(f"📊 Status breakdown: {status_counts}")
        print(f"   Total candidates: {len(data.get('candidates', []))}")
        
        response = jsonify(data)
        # Add aggressive cache-busting headers
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        response.headers['ETag'] = f'"{hash(json.dumps(data, sort_keys=True))}"'
        return response
    except Exception as e:
        import traceback
        print(f"❌ Error reading candidates: {e}")
        traceback.print_exc()
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

        # Read available slots from JSON using absolute path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, 'data', 'candidates.json')
        if not os.path.exists(json_path):
            json_path = 'data/candidates.json'
        json_path = os.path.abspath(json_path)
        
        with open(json_path, 'r', encoding='utf-8') as f:
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
            # Update candidate status to "calling" immediately
            try:
                update_candidate_in_json(candidate_id, 'calling')
                print(f"✅ Updated candidate {candidate_id} status to 'calling'")
            except Exception as status_error:
                print(f"⚠️  Error updating candidate status to 'calling': {status_error}")
        
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

