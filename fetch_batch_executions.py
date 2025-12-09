"""
Fetch batch executions from Bolna AI API
Retrieve all executions for specific batches with detailed call outcomes and metrics
"""

import requests
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List
from config import BOLNA_API_BASE, BOLNA_API_KEY

def fetch_batch_executions(
    batch_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    page_number: int = 1,
    page_size: int = 50
) -> Optional[Dict[str, Any]]:
    """
    Fetch batch executions from Bolna AI API
    
    Args:
        batch_id: Optional batch ID to filter by
        agent_id: Optional agent ID to filter by
        page_number: Page number for pagination (default: 1)
        page_size: Number of results per page (default: 50, max: 100)
    
    Returns:
        Dictionary containing batch execution data with pagination info
    """
    if not BOLNA_API_KEY:
        print("❌ BOLNA_API_KEY not found in .env file")
        print("   Please set BOLNA_API_KEY in your .env file")
        return None
    
    url = f"{BOLNA_API_BASE}/execution"
    headers = {
        "Authorization": f"Bearer {BOLNA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    params = {
        "page_number": page_number,
        "page_size": min(page_size, 100)  # Max 100 per page
    }
    
    if batch_id:
        params["batch_id"] = batch_id
    if agent_id:
        params["agent_id"] = agent_id
    
    try:
        print(f"📡 Fetching batch executions...")
        if batch_id:
            print(f"   Batch ID: {batch_id}")
        if agent_id:
            print(f"   Agent ID: {agent_id}")
        print(f"   Page: {page_number}, Size: {page_size}")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        return result
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"Response: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Response: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def format_batch_executions(data: Dict[str, Any], show_details: bool = False):
    """Format batch executions for display"""
    if not data:
        return "No data available"
    
    output = []
    output.append("="*70)
    output.append("📊 Batch Executions")
    output.append("="*70)
    output.append("")
    
    # Pagination Info
    if isinstance(data, dict):
        page_number = data.get('page_number', 1)
        page_size = data.get('page_size', 0)
        total = data.get('total', 0)
        has_more = data.get('has_more', False)
        
        output.append("📋 Pagination Info:")
        output.append(f"   Page: {page_number}")
        output.append(f"   Page Size: {page_size}")
        output.append(f"   Total Executions: {total}")
        output.append(f"   Has More: {has_more}")
        output.append("")
        
        executions = data.get('data', [])
    elif isinstance(data, list):
        executions = data
        output.append(f"📋 Found {len(executions)} execution(s)")
        output.append("")
    else:
        return "Invalid data format"
    
    if not executions:
        output.append("⚠️  No executions found")
        output.append("")
        output.append("="*70)
        return "\n".join(output)
    
    # Summary Statistics
    status_counts = {}
    total_duration = 0
    completed_count = 0
    
    for exec_data in executions:
        status = exec_data.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
        
        telephony = exec_data.get('telephony_data', {})
        duration = telephony.get('duration', 0)
        if duration:
            total_duration += duration
        
        if status.lower() in ['completed', 'ended', 'stopped']:
            completed_count += 1
    
    output.append("📈 Summary Statistics:")
    output.append(f"   Total Executions: {len(executions)}")
    output.append(f"   Completed: {completed_count}")
    output.append(f"   Status Breakdown:")
    for status, count in sorted(status_counts.items()):
        output.append(f"     - {status}: {count}")
    if total_duration > 0:
        avg_duration = total_duration / len(executions) if executions else 0
        output.append(f"   Average Duration: {avg_duration:.1f} seconds")
    output.append("")
    
    # Execution Details
    output.append("="*70)
    output.append("📋 Execution Details")
    output.append("="*70)
    output.append("")
    
    for i, exec_data in enumerate(executions, 1):
        exec_id = exec_data.get('execution_id') or exec_data.get('id', 'N/A')
        status = exec_data.get('status', 'N/A')
        created_at = exec_data.get('created_at', 'N/A')
        
        telephony = exec_data.get('telephony_data', {})
        duration = telephony.get('duration', 'N/A')
        recipient = telephony.get('recipient_phone_number', 'N/A')
        
        output.append(f"{i}. Execution ID: {exec_id}")
        output.append(f"   Status: {status}")
        output.append(f"   Created: {created_at}")
        output.append(f"   Duration: {duration} seconds")
        output.append(f"   Recipient: {recipient}")
        
        if show_details:
            transcript = (
                exec_data.get('transcript') or 
                exec_data.get('conversation_transcript') or
                ''
            )
            if transcript:
                output.append(f"   Transcript: {transcript[:100]}...")
            
            extracted_data = exec_data.get('extracted_data', {})
            if extracted_data:
                output.append(f"   Extracted Data: {json.dumps(extracted_data)[:100]}...")
        
        output.append("")
    
    output.append("="*70)
    return "\n".join(output)

def get_agent_id_from_config():
    """Get agent ID from config"""
    try:
        from config import AGENT_ID
        return AGENT_ID
    except:
        return None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fetch batch executions from Bolna AI API"
    )
    parser.add_argument(
        '--batch-id',
        type=str,
        help='Batch ID to filter executions (optional)'
    )
    parser.add_argument(
        '--agent-id',
        type=str,
        help='Agent ID to filter executions (optional, uses config if not provided)'
    )
    parser.add_argument(
        '--page',
        type=int,
        default=1,
        help='Page number (default: 1)'
    )
    parser.add_argument(
        '--page-size',
        type=int,
        default=50,
        help='Page size (default: 50, max: 100)'
    )
    parser.add_argument(
        '--details',
        action='store_true',
        help='Show detailed information including transcripts'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output raw JSON instead of formatted text'
    )
    parser.add_argument(
        '--all-pages',
        action='store_true',
        help='Fetch all pages automatically'
    )
    
    args = parser.parse_args()
    
    # Get agent ID
    agent_id = args.agent_id or get_agent_id_from_config()
    
    # Fetch executions
    if args.all_pages:
        all_executions = []
        page = 1
        while True:
            print(f"📄 Fetching page {page}...")
            data = fetch_batch_executions(
                batch_id=args.batch_id,
                agent_id=agent_id,
                page_number=page,
                page_size=args.page_size
            )
            
            if not data:
                break
            
            if isinstance(data, dict):
                executions = data.get('data', [])
                has_more = data.get('has_more', False)
                all_executions.extend(executions)
                
                if not has_more:
                    break
                page += 1
            else:
                all_executions = data
                break
        
        # Create combined result
        result = {
            'data': all_executions,
            'total': len(all_executions),
            'page_number': 1,
            'page_size': len(all_executions),
            'has_more': False
        }
    else:
        result = fetch_batch_executions(
            batch_id=args.batch_id,
            agent_id=agent_id,
            page_number=args.page,
            page_size=args.page_size
        )
    
    if result:
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_batch_executions(result, show_details=args.details))
    else:
        print("❌ Failed to fetch batch executions")
        sys.exit(1)

if __name__ == "__main__":
    main()

