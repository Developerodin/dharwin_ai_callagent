#!/bin/bash

# Quick diagnostic script for EC2 reset button issue

echo "=== EC2 Reset Button Diagnostic ==="
echo ""

cd ~/dharwin_ai_callagent || exit 1

echo "1. Checking Flask service status..."
sudo systemctl status bolna-flask --no-pager -l | head -15
echo ""

echo "2. Checking file permissions on data/candidates.json..."
ls -la data/candidates.json
echo ""

echo "3. Checking if Flask can write to data directory..."
touch data/test_write.tmp 2>/dev/null && rm data/test_write.tmp && echo "✅ Can write to data directory" || echo "❌ Cannot write to data directory (check permissions)"
echo ""

echo "4. Checking Flask logs for reset attempts..."
sudo journalctl -u bolna-flask -n 30 --no-pager | grep -i "reset\|candidate"
echo ""

echo "5. Testing Flask endpoint directly..."
curl -X POST http://localhost:5000/api/reset-statuses -H "Content-Type: application/json" 2>/dev/null | head -20
echo ""

echo "6. Checking current candidate statuses..."
cat data/candidates.json | grep -A 2 '"status"' | head -20
echo ""

echo "7. Checking Flask working directory..."
sudo systemctl show bolna-flask | grep WorkingDirectory
echo ""

echo "8. Testing if Flask can read/write JSON file..."
python3 << 'EOF'
import json
import os

try:
    json_path = 'data/candidates.json'
    print(f"File exists: {os.path.exists(json_path)}")
    print(f"File readable: {os.access(json_path, os.R_OK)}")
    print(f"File writable: {os.access(json_path, os.W_OK)}")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    print(f"✅ Can read file. Candidates: {len(data.get('candidates', []))}")
    
    # Try a test write
    test_path = 'data/test_write.json'
    with open(test_path, 'w') as f:
        json.dump(data, f, indent=2)
    os.remove(test_path)
    print("✅ Can write to data directory")
    
except Exception as e:
    print(f"❌ Error: {e}")
EOF

echo ""
echo "=== Diagnostic Complete ==="

