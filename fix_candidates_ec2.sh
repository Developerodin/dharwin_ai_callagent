#!/bin/bash
# Script to fix missing candidates.json on EC2

echo "🔍 Checking candidates.json on EC2..."

cd ~/dharwin_ai_callagent || exit 1

# Check if file exists
if [ ! -f "data/candidates.json" ]; then
    echo "❌ File not found at data/candidates.json"
    echo "📝 Creating file from repo version..."
    
    # Ensure data directory exists
    mkdir -p data
    
    # Check if file exists in git
    if git show HEAD:data/candidates.json > /dev/null 2>&1; then
        echo "✅ Restoring from git..."
        git checkout HEAD -- data/candidates.json
    else
        echo "❌ File not in git. Creating default structure..."
        cat > data/candidates.json << 'EOF'
{
  "candidates": [
    {
      "id": 1,
      "name": "Prakhar Sharma",
      "phone": "+918755887760",
      "email": "prakhar.sharma@example.com",
      "position": "Software Engineer",
      "status": "pending",
      "scheduledInterview": {
        "day": "Friday",
        "date": "Friday, the 12th of December",
        "time": "11:00 A.M.",
        "datetime": "Friday, the 12th of December at 11:00 A.M."
      },
      "reschedulingSlots": [1, 3, 5],
      "applicationDate": "2024-11-25"
    },
    {
      "id": 2,
      "name": "Ronak Vaya",
      "phone": "+919694998693",
      "email": "Ronak.vaya@example.com",
      "position": "Frontend Developer",
      "status": "pending",
      "scheduledInterview": {
        "date": "Monday, the 15th of December",
        "time": "2:00 P.M.",
        "day": "Monday",
        "datetime": "Monday, the 15th of December at 2:00 P.M."
      },
      "reschedulingSlots": [2, 4, 6],
      "applicationDate": "2024-11-24"
    },
    {
      "id": 3,
      "name": "Priya Patel",
      "phone": "+919123456789",
      "email": "priya.patel@example.com",
      "position": "Backend Developer",
      "status": "pending",
      "scheduledInterview": {
        "date": "Tuesday, the 16th of December",
        "time": "11:00 A.M.",
        "day": "Tuesday",
        "datetime": "Tuesday, the 16th of December at 11:00 A.M."
      },
      "reschedulingSlots": [3, 6, 7],
      "applicationDate": "2024-11-23"
    },
    {
      "id": 4,
      "name": "Amit Kumar",
      "phone": "+919988776655",
      "email": "amit.kumar@example.com",
      "position": "Full Stack Developer",
      "status": "pending",
      "scheduledInterview": {
        "date": "Wednesday, the 17th of December",
        "time": "3:00 P.M.",
        "day": "Wednesday",
        "datetime": "Wednesday, the 17th of December at 3:00 P.M."
      },
      "reschedulingSlots": [4, 1, 5],
      "applicationDate": "2024-11-22"
    },
    {
      "id": 5,
      "name": "Sneha Singh",
      "phone": "+919765432109",
      "email": "sneha.singh@example.com",
      "position": "UI/UX Designer",
      "status": "pending",
      "scheduledInterview": {
        "date": "Thursday, the 18th of December",
        "time": "10:30 A.M.",
        "day": "Thursday",
        "datetime": "Thursday, the 18th of December at 10:30 A.M."
      },
      "reschedulingSlots": [5, 2, 7],
      "applicationDate": "2024-11-21"
    }
  ],
  "availableSlots": [
    {
      "id": 1,
      "date": "Monday, the 15th of December",
      "time": "2:00 P.M.",
      "day": "Monday",
      "datetime": "Monday, the 15th of December at 2:00 P.M."
    },
    {
      "id": 2,
      "date": "Tuesday, the 16th of December",
      "time": "11:00 A.M.",
      "day": "Tuesday",
      "datetime": "Tuesday, the 16th of December at 11:00 A.M."
    },
    {
      "id": 3,
      "date": "Wednesday, the 17th of December",
      "time": "3:00 P.M.",
      "day": "Wednesday",
      "datetime": "Wednesday, the 17th of December at 3:00 P.M."
    },
    {
      "id": 4,
      "date": "Thursday, the 18th of December",
      "time": "10:30 A.M.",
      "day": "Thursday",
      "datetime": "Thursday, the 18th of December at 10:30 A.M."
    },
    {
      "id": 5,
      "date": "Friday, the 19th of December",
      "time": "1:00 P.M.",
      "day": "Friday",
      "datetime": "Friday, the 19th of December at 1:00 P.M."
    },
    {
      "id": 6,
      "date": "Monday, the 22nd of December",
      "time": "9:00 A.M.",
      "day": "Monday",
      "datetime": "Monday, the 22nd of December at 9:00 A.M."
    },
    {
      "id": 7,
      "date": "Tuesday, the 23rd of December",
      "time": "2:30 P.M.",
      "day": "Tuesday",
      "datetime": "Tuesday, the 23rd of December at 2:30 P.M."
    }
  ]
}
EOF
        echo "✅ Created default candidates.json"
    fi
else
    echo "✅ File exists at data/candidates.json"
    
    # Check if file is empty or invalid JSON
    if [ ! -s "data/candidates.json" ]; then
        echo "❌ File is empty. Restoring..."
        git checkout HEAD -- data/candidates.json 2>/dev/null || echo "Could not restore from git"
    else
        # Try to validate JSON
        if python3 -m json.tool data/candidates.json > /dev/null 2>&1; then
            echo "✅ File contains valid JSON"
            # Count candidates
            CANDIDATES=$(python3 -c "import json; data=json.load(open('data/candidates.json')); print(len(data.get('candidates', [])))" 2>/dev/null || echo "0")
            echo "📊 Found $CANDIDATES candidates"
            if [ "$CANDIDATES" = "0" ]; then
                echo "⚠️  No candidates found. Restoring from git..."
                git checkout HEAD -- data/candidates.json 2>/dev/null || echo "Could not restore from git"
            fi
        else
            echo "❌ File contains invalid JSON. Restoring..."
            git checkout HEAD -- data/candidates.json 2>/dev/null || echo "Could not restore from git"
        fi
    fi
fi

# Check file permissions
chmod 644 data/candidates.json

# Check Flask service can read it
echo ""
echo "🔍 Verifying Flask can read the file..."
curl -s http://localhost:5000/api/candidates | python3 -m json.tool > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Flask API can read candidates.json"
else
    echo "⚠️  Flask API test failed. Check Flask service logs:"
    echo "   sudo journalctl -u bolna-flask -n 50"
fi

echo ""
echo "✅ Done! Restart Flask if needed:"
echo "   sudo systemctl restart bolna-flask"

