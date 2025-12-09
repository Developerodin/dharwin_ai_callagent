"""
Migrate old temporary webhook logs from webhook_logs.json to permanent storage
in data/webhook_data.json
"""

import json
import os
from datetime import datetime

def migrate_webhook_logs():
    """
    Migrate old webhook logs from temporary storage to permanent storage
    """
    old_log_file = 'webhook_logs.json'
    new_data_file = 'data/webhook_data.json'
    
    # Check if old logs exist
    if not os.path.exists(old_log_file):
        print(f"❌ {old_log_file} not found")
        print("   No old logs to migrate.")
        return
    
    try:
        # Load old logs
        print(f"📖 Reading old logs from {old_log_file}...")
        with open(old_log_file, 'r', encoding='utf-8') as f:
            old_logs = json.load(f)
        
        if not old_logs or not isinstance(old_logs, list):
            print(f"⚠️  No valid logs found in {old_log_file}")
            return
        
        print(f"✅ Found {len(old_logs)} old log entries")
        
        # Load existing permanent storage
        webhook_data = {}
        if os.path.exists(new_data_file):
            try:
                with open(new_data_file, 'r', encoding='utf-8') as f:
                    webhook_data = json.load(f)
                print(f"✅ Loaded existing permanent storage with {len([k for k in webhook_data.keys() if k != 'all_webhooks'])} entries")
            except Exception as e:
                print(f"⚠️  Could not load existing storage: {e}")
                webhook_data = {}
        else:
            # Create data directory if needed
            os.makedirs('data', exist_ok=True)
            print(f"📁 Created data directory")
        
        # Initialize all_webhooks array if needed
        if 'all_webhooks' not in webhook_data:
            webhook_data['all_webhooks'] = []
        
        migrated_count = 0
        skipped_count = 0
        
        # Process each old log entry
        for i, log_entry in enumerate(old_logs, 1):
            try:
                payload = log_entry.get('payload', {})
                timestamp = log_entry.get('timestamp', datetime.now().isoformat())
                
                # Extract execution_id
                execution_id = (
                    payload.get('execution_id') or 
                    payload.get('executionId') or 
                    payload.get('id') or
                    payload.get('data', {}).get('execution_id') or
                    payload.get('data', {}).get('executionId')
                )
                
                if not execution_id:
                    print(f"⚠️  Log entry #{i}: No execution_id found, skipping")
                    skipped_count += 1
                    continue
                
                # Check if already exists in permanent storage
                if execution_id in webhook_data:
                    # Check if this is newer data
                    existing_timestamp = webhook_data[execution_id].get('timestamp', '')
                    if timestamp > existing_timestamp:
                        print(f"🔄 Log entry #{i}: Updating existing entry for {execution_id}")
                    else:
                        print(f"⏭️  Log entry #{i}: Entry {execution_id} already exists (newer), skipping")
                        skipped_count += 1
                        continue
                else:
                    print(f"📥 Log entry #{i}: Migrating {execution_id}...")
                
                # Try to find candidate_id from execution_mapping
                candidate_id = None
                mapping_file = 'execution_mapping.json'
                if os.path.exists(mapping_file):
                    try:
                        with open(mapping_file, 'r', encoding='utf-8') as f:
                            mappings = json.load(f)
                            mapping = mappings.get(execution_id)
                            if mapping:
                                candidate_id = mapping.get('candidate_id')
                    except:
                        pass
                
                # Create entry similar to save_webhook_data format
                entry = {
                    'execution_id': execution_id,
                    'candidate_id': candidate_id,
                    'timestamp': timestamp,
                    'received_at': timestamp.split('T')[0] + ' ' + timestamp.split('T')[1].split('.')[0] if 'T' in timestamp else timestamp,
                    'payload': payload,  # Complete payload
                    'extracted_data': (
                        payload.get('extracted_data') or
                        payload.get('data', {}).get('extracted_data') or
                        payload.get('execution', {}).get('extracted_data') or
                        {}
                    ),
                    'transcript': (
                        payload.get('transcript') or
                        payload.get('conversation_transcript') or
                        payload.get('data', {}).get('transcript') or
                        payload.get('execution', {}).get('transcript') or
                        ''
                    ),
                    'status': (
                        payload.get('status') or
                        payload.get('data', {}).get('status') or
                        payload.get('execution', {}).get('status') or
                        'unknown'
                    ),
                    'recipient_phone_number': (
                        payload.get('recipient_phone_number') or
                        payload.get('phone_number') or
                        payload.get('phone') or
                        payload.get('data', {}).get('recipient_phone_number') or
                        None
                    ),
                    'telephony_data': (
                        payload.get('telephony_data') or
                        payload.get('data', {}).get('telephony_data') or
                        payload.get('execution', {}).get('telephony_data') or
                        {}
                    )
                }
                
                # Store in permanent storage
                webhook_data[execution_id] = entry
                
                # Add to chronological list if not already there
                existing_in_index = any(
                    w.get('execution_id') == execution_id 
                    for w in webhook_data['all_webhooks']
                )
                
                if not existing_in_index:
                    webhook_data['all_webhooks'].insert(0, {
                        'execution_id': execution_id,
                        'candidate_id': candidate_id,
                        'timestamp': timestamp,
                        'status': entry['status']
                    })
                
                migrated_count += 1
                
            except Exception as e:
                print(f"❌ Error processing log entry #{i}: {e}")
                skipped_count += 1
                continue
        
        # Sort chronological list by timestamp (newest first)
        webhook_data['all_webhooks'].sort(
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )
        
        # Keep only last 1000 in chronological index
        webhook_data['all_webhooks'] = webhook_data['all_webhooks'][:1000]
        
        # Save to permanent storage
        print(f"\n💾 Saving migrated data to {new_data_file}...")
        with open(new_data_file, 'w', encoding='utf-8') as f:
            json.dump(webhook_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"✅ Migration Complete!")
        print(f"{'='*70}")
        print(f"📊 Statistics:")
        print(f"   Total old logs: {len(old_logs)}")
        print(f"   ✅ Migrated: {migrated_count}")
        print(f"   ⏭️  Skipped: {skipped_count}")
        print(f"   📁 Permanent storage now has: {len([k for k in webhook_data.keys() if k != 'all_webhooks'])} entries")
        print(f"\n💡 You can now view the migrated data with:")
        print(f"   python view_webhook_data.py")
        print(f"{'='*70}\n")
        
        # Ask if user wants to backup old logs
        print("💾 Backup old logs? (Optional)")
        print("   The old webhook_logs.json file has been preserved.")
        print("   You can delete it after verifying the migration.")
        
    except Exception as e:
        print(f"❌ Error migrating logs: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    migrate_webhook_logs()

