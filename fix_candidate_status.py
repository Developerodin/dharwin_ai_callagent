"""
Quick script to fix candidate status if webhook didn't update it
"""

import json
import sys

def reset_candidate_status(candidate_id: int, new_status: str = 'pending'):
    """Reset a candidate's status"""
    try:
        json_path = 'data/candidates.json'
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        candidate = next((c for c in data['candidates'] if c['id'] == candidate_id), None)
        
        if candidate:
            old_status = candidate.get('status', 'unknown')
            candidate['status'] = new_status
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Candidate {candidate_id} ({candidate['name']})")
            print(f"   Status updated: {old_status} → {new_status}")
            return True
        else:
            print(f"❌ Candidate {candidate_id} not found")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Reset candidate 1 (Prakhar Sharma) to pending
    print("🔧 Fixing Candidate Status")
    print("=" * 50)
    
    if reset_candidate_status(1, 'pending'):
        print("\n✅ Status fixed! Candidate is now 'pending'")
    else:
        print("\n❌ Failed to fix status")
        sys.exit(1)


