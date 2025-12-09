"""
Fetch historical call data from Bolna API
Retrieves transcripts, recordings, traces, logs, and raw data for all past calls
"""

import json
import os
import time
from datetime import datetime
from bolna_agent import BolnaAgent
from config import AGENT_ID

def fetch_all_executions(agent, agent_id=None, max_pages=10):
    """
    Fetch all executions from Bolna API
    
    Args:
        agent: BolnaAgent instance
        agent_id: Agent ID to filter by (optional)
        max_pages: Maximum number of pages to fetch
    
    Returns:
        List of all execution IDs
    """
    all_executions = []
    page_number = 1
    page_size = 50  # Maximum allowed
    
    print(f"📡 Fetching execution history from Bolna API...")
    print(f"   Agent ID: {agent_id or 'All agents'}")
    print(f"   Max pages: {max_pages}\n")
    
    while page_number <= max_pages:
        try:
            print(f"   Fetching page {page_number}...", end=" ")
            result = agent.list_executions(
                agent_id=agent_id,
                page_number=page_number,
                page_size=page_size
            )
            
            # Handle different response formats
            executions = []
            if isinstance(result, dict):
                if 'data' in result:
                    executions = result['data'] if isinstance(result['data'], list) else [result['data']]
                elif 'executions' in result:
                    executions = result['executions']
                else:
                    executions = [result]
            elif isinstance(result, list):
                executions = result
            
            if not executions:
                print(f"✅ Done (no more executions)")
                break
            
            # Extract execution IDs
            for exec_data in executions:
                exec_id = (
                    exec_data.get('execution_id') or 
                    exec_data.get('id') or 
                    exec_data.get('executionId')
                )
                if exec_id:
                    all_executions.append({
                        'execution_id': exec_id,
                        'status': exec_data.get('status', 'unknown'),
                        'created_at': exec_data.get('created_at', ''),
                        'agent_id': exec_data.get('agent_id', ''),
                        'summary': exec_data
                    })
            
            print(f"✅ Found {len(executions)} executions (total: {len(all_executions)})")
            
            # Check if there are more pages
            if len(executions) < page_size:
                break
            
            page_number += 1
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"❌ Error fetching page {page_number}: {e}")
            break
    
    return all_executions

def fetch_complete_execution_data(agent, execution_id):
    """
    Fetch complete data for a single execution:
    - Execution details (full)
    - Transcript
    - Recording URL
    - Execution logs/traces
    - Raw data
    
    Args:
        agent: BolnaAgent instance
        execution_id: Execution ID to fetch
    
    Returns:
        Dictionary with all execution data
    """
    data = {
        'execution_id': execution_id,
        'fetched_at': datetime.now().isoformat(),
        'execution_details': None,
        'transcript': None,
        'recording_url': None,
        'execution_logs': None,
        'raw_data': {}
    }
    
    try:
        # 1. Get execution details (includes most data)
        print(f"      📋 Fetching execution details...", end=" ")
        details = agent.get_execution_details(execution_id)
        data['execution_details'] = details
        
        # Extract transcript from details
        transcript = (
            details.get('transcript') or 
            details.get('conversation_transcript') or 
            details.get('call_transcript') or
            details.get('transcript_text') or
            ''
        )
        data['transcript'] = transcript if transcript else None
        
        # Extract recording URL
        telephony_data = details.get('telephony_data', {})
        if isinstance(telephony_data, dict):
            data['recording_url'] = telephony_data.get('recording_url') or telephony_data.get('recording')
        
        # Extract status, dates, etc.
        data['status'] = details.get('status', 'unknown')
        data['created_at'] = details.get('created_at', '')
        data['updated_at'] = details.get('updated_at', details.get('modified_at', ''))
        data['agent_id'] = details.get('agent_id', '')
        data['recipient_phone_number'] = (
            telephony_data.get('recipient_phone_number') if isinstance(telephony_data, dict) else None or
            details.get('recipient_phone_number')
        )
        data['extracted_data'] = details.get('extracted_data', {})
        data['cost_breakdown'] = details.get('cost_breakdown', {})
        
        print("✅")
        
        # 2. Get execution logs/traces (if available)
        try:
            print(f"      📊 Fetching execution logs...", end=" ")
            logs = agent.get_execution_logs(execution_id)
            data['execution_logs'] = logs
            print("✅")
        except Exception as e:
            print(f"⚠️  (logs not available: {str(e)[:50]})")
        
        # 3. Store raw data (complete response)
        data['raw_data'] = {
            'execution_details': details,
            'execution_logs': data.get('execution_logs'),
            'fetched_via': 'bolna_api',
            'api_endpoint': f'/execution/{execution_id}'
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        data['error'] = str(e)
        data['error_type'] = type(e).__name__
        # Still return data even on error so we can track failed fetches
        if not data.get('execution_details'):
            data['execution_details'] = {}
    
    return data

def save_to_permanent_storage(execution_data, candidate_id=None):
    """
    Save execution data to permanent storage in data/webhook_data.json
    Merges with existing data
    """
    webhook_data_file = 'data/webhook_data.json'
    os.makedirs('data', exist_ok=True)
    
    # Load existing data
    webhook_data = {}
    if os.path.exists(webhook_data_file):
        try:
            with open(webhook_data_file, 'r', encoding='utf-8') as f:
                webhook_data = json.load(f)
        except:
            pass
    
    if 'all_webhooks' not in webhook_data:
        webhook_data['all_webhooks'] = []
    
    execution_id = execution_data['execution_id']
    
    # Create/update entry
    entry = {
        'execution_id': execution_id,
        'candidate_id': candidate_id,
        'timestamp': execution_data.get('created_at', datetime.now().isoformat()),
        'received_at': execution_data.get('created_at', datetime.now().isoformat()).split('T')[0] + ' ' + execution_data.get('created_at', datetime.now().isoformat()).split('T')[1].split('.')[0] if 'T' in execution_data.get('created_at', '') else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'fetched_from': 'bolna_api',
        'fetched_at': execution_data.get('fetched_at', datetime.now().isoformat()),
        'payload': execution_data.get('raw_data', {}),
        'execution_details': execution_data.get('execution_details', {}),
        'transcript': execution_data.get('transcript', ''),
        'recording_url': execution_data.get('recording_url'),
        'execution_logs': execution_data.get('execution_logs'),
        'extracted_data': execution_data.get('extracted_data', {}),
        'status': execution_data.get('status', 'unknown'),
        'recipient_phone_number': execution_data.get('recipient_phone_number'),
        'telephony_data': (
            execution_data.get('execution_details', {}).get('telephony_data', {})
            if execution_data.get('execution_details') else {}
        ),
        'cost_breakdown': execution_data.get('cost_breakdown', {}),
        'agent_id': execution_data.get('agent_id', ''),
        'created_at': execution_data.get('created_at', ''),
        'updated_at': execution_data.get('updated_at', ''),
        'raw_data': execution_data.get('raw_data', {}),
        'error': execution_data.get('error'),
        'error_type': execution_data.get('error_type')
    }
    
    # Store by execution_id
    webhook_data[execution_id] = entry
    
    # Update chronological index
    existing_index = next(
        (i for i, w in enumerate(webhook_data['all_webhooks']) if w.get('execution_id') == execution_id),
        None
    )
    
    index_entry = {
        'execution_id': execution_id,
        'candidate_id': candidate_id,
        'timestamp': entry['timestamp'],
        'status': entry['status'],
        'fetched_from': 'bolna_api'
    }
    
    if existing_index is not None:
        webhook_data['all_webhooks'][existing_index] = index_entry
    else:
        webhook_data['all_webhooks'].insert(0, index_entry)
    
    # Sort by timestamp (newest first)
    webhook_data['all_webhooks'].sort(
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )
    
    # Keep only last 1000 in index
    webhook_data['all_webhooks'] = webhook_data['all_webhooks'][:1000]
    
    # Save
    with open(webhook_data_file, 'w', encoding='utf-8') as f:
        json.dump(webhook_data, f, indent=2, ensure_ascii=False)
    
    return True

def get_candidate_id_from_execution(execution_id):
    """Try to find candidate_id from execution_mapping.json"""
    try:
        mapping_file = 'execution_mapping.json'
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mappings = json.load(f)
                mapping = mappings.get(execution_id)
                if mapping:
                    return mapping.get('candidate_id')
    except:
        pass
    return None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fetch historical call data from Bolna API"
    )
    parser.add_argument(
        '--agent-id',
        type=str,
        default=AGENT_ID,
        help='Agent ID to filter executions (default: from config)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Maximum number of pages to fetch (default: 10)'
    )
    parser.add_argument(
        '--execution-id',
        type=str,
        help='Fetch specific execution ID only'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of executions to fetch (for testing)'
    )
    
    args = parser.parse_args()
    
    print(f"{'='*70}")
    print(f"📡 Fetching Historical Call Data from Bolna API")
    print(f"{'='*70}\n")
    
    try:
        # Initialize agent
        agent = BolnaAgent()
        if args.agent_id:
            agent.agent_id = args.agent_id
        
        if args.execution_id:
            # Fetch specific execution
            print(f"📋 Fetching execution: {args.execution_id}\n")
            execution_data = fetch_complete_execution_data(agent, args.execution_id)
            candidate_id = get_candidate_id_from_execution(args.execution_id)
            
            print(f"\n💾 Saving to permanent storage...")
            save_to_permanent_storage(execution_data, candidate_id)
            
            print(f"✅ Complete data fetched and saved for {args.execution_id}")
            
        else:
            # Fetch all executions
            executions = fetch_all_executions(agent, args.agent_id, args.max_pages)
            
            if not executions:
                print(f"\n❌ No executions found")
                return
            
            # Apply limit if specified
            if args.limit:
                executions = executions[:args.limit]
            
            print(f"\n{'='*70}")
            print(f"📥 Fetching Complete Data for {len(executions)} Executions")
            print(f"{'='*70}\n")
            
            fetched = 0
            errors = 0
            
            for i, exec_info in enumerate(executions, 1):
                exec_id = exec_info['execution_id']
                print(f"\n[{i}/{len(executions)}] {exec_id}")
                print(f"   Status: {exec_info.get('status', 'unknown')}")
                
                # Fetch complete data
                execution_data = fetch_complete_execution_data(agent, exec_id)
                
                # Find candidate_id
                candidate_id = get_candidate_id_from_execution(exec_id)
                
                # Save to permanent storage
                try:
                    save_to_permanent_storage(execution_data, candidate_id)
                    fetched += 1
                    print(f"   💾 Saved to permanent storage")
                except Exception as e:
                    print(f"   ❌ Error saving: {e}")
                    errors += 1
                
                # Rate limiting
                if i < len(executions):
                    time.sleep(0.3)
            
            print(f"\n{'='*70}")
            print(f"✅ Fetch Complete!")
            print(f"{'='*70}")
            print(f"📊 Statistics:")
            print(f"   Total executions found: {len(executions)}")
            print(f"   ✅ Successfully fetched: {fetched}")
            print(f"   ❌ Errors: {errors}")
            print(f"\n💡 View stored data:")
            print(f"   python view_webhook_data.py")
            print(f"{'='*70}\n")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

