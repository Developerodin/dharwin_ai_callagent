"""
View transcripts stored separately from webhook data
Organized by candidate with metadata (name, position, caller ID)
"""

import json
import os
import sys
from datetime import datetime

def load_transcripts():
    """Load transcripts from data/transcripts.json"""
    transcripts_file = 'data/transcripts.json'
    
    if not os.path.exists(transcripts_file):
        print("❌ Transcripts file not found: data/transcripts.json")
        return None
    
    try:
        with open(transcripts_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading transcripts: {e}")
        return None

def view_all_transcripts():
    """View all transcripts"""
    data = load_transcripts()
    if not data:
        return
    
    all_transcripts = data.get('all_transcripts', [])
    by_candidate = data.get('by_candidate', {})
    
    print("="*70)
    print("📝 All Transcripts")
    print("="*70)
    print(f"\nTotal transcripts: {len(all_transcripts)}")
    print(f"Candidates with transcripts: {len(by_candidate)}\n")
    
    if all_transcripts:
        print("Recent Transcripts (last 10):")
        print("-"*70)
        for i, entry in enumerate(all_transcripts[:10], 1):
            print(f"\n{i}. Execution ID: {entry.get('execution_id', 'N/A')}")
            print(f"   Candidate: {entry.get('candidate_name', 'Unknown')} (ID: {entry.get('candidate_id', 'N/A')})")
            print(f"   Position: {entry.get('position', 'Unknown')}")
            print(f"   Caller ID: {entry.get('caller_id', 'N/A')}")
            print(f"   Recipient: {entry.get('recipient_phone', 'N/A')}")
            print(f"   Timestamp: {entry.get('timestamp', 'N/A')}")
    
    print("\n" + "="*70)

def view_candidate_transcripts(candidate_id: int):
    """View all transcripts for a specific candidate"""
    data = load_transcripts()
    if not data:
        return
    
    by_candidate = data.get('by_candidate', {})
    candidate_key = str(candidate_id)
    
    if candidate_key not in by_candidate:
        print(f"❌ No transcripts found for candidate ID {candidate_id}")
        return
    
    candidate_data = by_candidate[candidate_key]
    transcripts = candidate_data.get('transcripts', {})
    
    print("="*70)
    print(f"📝 Transcripts for {candidate_data.get('candidate_name', 'Unknown')}")
    print("="*70)
    print(f"\nCandidate ID: {candidate_id}")
    print(f"Name: {candidate_data.get('candidate_name', 'Unknown')}")
    print(f"Position: {candidate_data.get('position', 'Unknown')}")
    print(f"Phone: {candidate_data.get('phone', 'Unknown')}")
    print(f"Email: {candidate_data.get('email', 'Unknown')}")
    print(f"Total transcripts: {len(transcripts)}\n")
    
    for execution_id, transcript_entry in transcripts.items():
        print("-"*70)
        print(f"\nExecution ID: {execution_id}")
        print(f"Timestamp: {transcript_entry.get('received_at', 'N/A')}")
        print(f"Status: {transcript_entry.get('status', 'N/A')}")
        print(f"Caller ID: {transcript_entry.get('caller_id', 'N/A')}")
        print(f"Duration: {transcript_entry.get('call_duration', 'N/A')} seconds")
        print(f"\nTranscript:")
        print(transcript_entry.get('transcript', 'No transcript available'))
        print()

def view_transcript_by_execution(execution_id: str):
    """View transcript for a specific execution"""
    data = load_transcripts()
    if not data:
        return
    
    by_candidate = data.get('by_candidate', {})
    
    # Search through all candidates
    for candidate_key, candidate_data in by_candidate.items():
        transcripts = candidate_data.get('transcripts', {})
        if execution_id in transcripts:
            transcript_entry = transcripts[execution_id]
            
            print("="*70)
            print(f"📝 Transcript for Execution: {execution_id}")
            print("="*70)
            print(f"\nCandidate:")
            print(f"  ID: {candidate_data.get('candidate_id', 'N/A')}")
            print(f"  Name: {candidate_data.get('candidate_name', 'Unknown')}")
            print(f"  Position: {candidate_data.get('position', 'Unknown')}")
            print(f"  Phone: {candidate_data.get('phone', 'N/A')}")
            print(f"  Email: {candidate_data.get('email', 'N/A')}")
            print(f"\nCall Details:")
            print(f"  Caller ID: {transcript_entry.get('caller_id', 'N/A')}")
            print(f"  Recipient: {transcript_entry.get('recipient_phone', 'N/A')}")
            print(f"  Status: {transcript_entry.get('status', 'N/A')}")
            print(f"  Duration: {transcript_entry.get('call_duration', 'N/A')} seconds")
            print(f"  Timestamp: {transcript_entry.get('received_at', 'N/A')}")
            print(f"\nTranscript:")
            print("-"*70)
            print(transcript_entry.get('transcript', 'No transcript available'))
            print("="*70)
            return
    
    print(f"❌ No transcript found for execution ID: {execution_id}")

def list_candidates():
    """List all candidates who have transcripts"""
    data = load_transcripts()
    if not data:
        return
    
    by_candidate = data.get('by_candidate', {})
    
    print("="*70)
    print("📋 Candidates with Transcripts")
    print("="*70)
    print()
    
    if not by_candidate:
        print("No candidates with transcripts found.")
        return
    
    for candidate_key, candidate_data in by_candidate.items():
        transcript_count = len(candidate_data.get('transcripts', {}))
        print(f"ID: {candidate_data.get('candidate_id', 'N/A')}")
        print(f"  Name: {candidate_data.get('candidate_name', 'Unknown')}")
        print(f"  Position: {candidate_data.get('position', 'Unknown')}")
        print(f"  Phone: {candidate_data.get('phone', 'N/A')}")
        print(f"  Transcripts: {transcript_count}")
        print()

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == '--list' or arg == '-l':
            list_candidates()
        elif arg.startswith('--candidate=') or arg.startswith('-c='):
            try:
                candidate_id = int(arg.split('=')[1])
                view_candidate_transcripts(candidate_id)
            except (ValueError, IndexError):
                print("❌ Invalid candidate ID. Use: --candidate=ID or -c=ID")
        elif arg.startswith('--execution=') or arg.startswith('-e='):
            execution_id = arg.split('=')[1]
            view_transcript_by_execution(execution_id)
        else:
            print("Usage:")
            print("  python view_transcripts.py                    # View all transcripts")
            print("  python view_transcripts.py --list            # List candidates")
            print("  python view_transcripts.py --candidate=ID    # View candidate transcripts")
            print("  python view_transcripts.py --execution=ID    # View specific transcript")
    else:
        view_all_transcripts()

if __name__ == '__main__':
    main()

