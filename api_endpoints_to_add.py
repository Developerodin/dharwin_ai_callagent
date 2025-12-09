# Add these endpoints to your api_server.py file
# These endpoints handle candidate reset (status only) and deletion

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

