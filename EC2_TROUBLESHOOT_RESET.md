# EC2 Reset Button Troubleshooting Guide

Since reset works locally but not on EC2, run these checks on your EC2 instance:

## Step 1: Check if Latest Code is Deployed

```bash
cd ~/dharwin_ai_callagent

# Pull latest code
git pull origin master

# Check if lib/config.ts exists and has the auto-detect code
grep -A 5 "Auto-detect" lib/config.ts

# Check if components use getFlaskBackendUrl
grep -r "getFlaskBackendUrl" components/
```

## Step 2: Verify Next.js Was Rebuilt

```bash
# The build is IMPORTANT - must rebuild to include new code
npm run build

# Verify the build succeeded
ls -la .next/standalone 2>/dev/null || echo "Build output exists"

# Check when Next.js was last built
ls -lth .next/ | head -5
```

## Step 3: Check Flask Backend is Running

```bash
# Check if Flask is running
sudo systemctl status bolna-flask

# Check if port 5000 is listening
sudo netstat -tlnp | grep 5000

# Test Flask backend directly from EC2
curl http://localhost:5000/api/candidates
```

## Step 4: Check Flask Backend is Accessible from Browser

```bash
# Get your EC2 public IP
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "EC2 IP: $EC2_IP"

# Test from EC2 itself (should work)
curl http://localhost:5000/api/reset-statuses -X POST

# Test from EC2 public IP (this is what browser uses)
curl http://${EC2_IP}:5000/api/candidates
```

**If the public IP test fails**, the issue is likely:
- Security Group doesn't allow port 5000
- Flask is binding to localhost instead of 0.0.0.0

## Step 5: Verify Flask Binds to 0.0.0.0

```bash
# Check Flask is binding to all interfaces
grep "host=" api_server.py | grep -v "#"

# Should show: host='0.0.0.0' or host=os.getenv('FLASK_HOST', '0.0.0.0')
# If it shows 'localhost', that's the problem!
```

## Step 6: Check Security Group (AWS Console)

1. Go to EC2 Console → Security Groups
2. Select your instance's security group
3. Check Inbound Rules:
   - Should have: Custom TCP, Port 5000, Source: 0.0.0.0/0
   - If missing, add it!

## Step 7: Check Browser Console

1. Open your app: `http://YOUR_EC2_IP:3000`
2. Open Browser DevTools (F12)
3. Go to Console tab
4. Click the reset button
5. Look for errors - they'll tell you what URL it's trying

Expected behavior:
- Should try: `http://YOUR_EC2_IP:5000/api/reset-statuses`
- If it tries `http://localhost:5000`, the auto-detect isn't working

## Step 8: Debug the URL Detection

Add this to your browser console on EC2:

```javascript
// Check what URL the frontend is using
fetch('/api/debug').then(r => r.text()).then(console.log)
```

Or visit: `http://YOUR_EC2_IP:3000/debug` (I created a debug page)

## Step 9: Manual Fix - Set Environment Variable

If auto-detect isn't working, set it manually:

```bash
# Get EC2 IP
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_FLASK_BACKEND_URL=http://${EC2_IP}:5000
EOF

# Rebuild Next.js
npm run build

# Restart Next.js
sudo systemctl restart bolna-nextjs
```

## Step 10: Check Next.js Logs

```bash
# View recent logs
sudo journalctl -u bolna-nextjs -n 50 --no-pager

# Follow logs in real-time
sudo journalctl -u bolna-nextjs -f
```

## Step 11: Check Flask Logs

```bash
# View recent logs
sudo journalctl -u bolna-flask -n 50 --no-pager

# Follow logs in real-time (open in another terminal)
sudo journalctl -u bolna-flask -f
```

When you click reset, you should see a request in Flask logs. If you don't, the request isn't reaching Flask.

## Quick All-in-One Test Script

Run this script on EC2 to check everything at once:

```bash
#!/bin/bash
cd ~/dharwin_ai_callagent

echo "=== Checking Deployment ==="
git pull origin master
echo ""

echo "=== Checking Flask Backend ==="
sudo systemctl is-active bolna-flask && echo "✅ Flask is running" || echo "❌ Flask is NOT running"
curl -s http://localhost:5000/api/candidates > /dev/null && echo "✅ Flask responds on localhost:5000" || echo "❌ Flask NOT responding"
echo ""

echo "=== Checking EC2 Access ==="
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "EC2 IP: $EC2_IP"
curl -s http://${EC2_IP}:5000/api/candidates > /dev/null && echo "✅ Flask accessible via public IP" || echo "❌ Flask NOT accessible via public IP (check Security Group!)"
echo ""

echo "=== Checking Flask Binding ==="
grep -q "host='0.0.0.0'" api_server.py && echo "✅ Flask binds to 0.0.0.0" || echo "❌ Flask NOT binding to 0.0.0.0"
echo ""

echo "=== Rebuilding Next.js ==="
npm run build
echo ""

echo "=== Restarting Services ==="
sudo systemctl restart bolna-nextjs bolna-flask
sleep 3
echo ""

echo "=== Service Status ==="
sudo systemctl is-active bolna-nextjs && echo "✅ Next.js is running" || echo "❌ Next.js is NOT running"
sudo systemctl is-active bolna-flask && echo "✅ Flask is running" || echo "❌ Flask is NOT running"
echo ""

echo "=== Next Steps ==="
echo "1. Test in browser: http://${EC2_IP}:3000"
echo "2. Open browser console (F12) and check for errors"
echo "3. Try reset button and see what URL it uses"
echo "4. Visit debug page: http://${EC2_IP}:3000/debug"
```

Save as `check-ec2.sh`, make executable (`chmod +x check-ec2.sh`), and run it.

## Most Common Issues & Solutions

### Issue 1: Security Group Blocks Port 5000
**Solution**: Add inbound rule for port 5000 in EC2 Security Group

### Issue 2: Next.js Not Rebuilt
**Solution**: Run `npm run build` and restart Next.js

### Issue 3: Flask Binding to localhost Only
**Solution**: Verify `api_server.py` uses `host='0.0.0.0'`

### Issue 4: Auto-detect Not Working
**Solution**: Manually set `NEXT_PUBLIC_FLASK_BACKEND_URL` in `.env.local` and rebuild

### Issue 5: CORS Issue
**Solution**: CORS is already enabled with `CORS(app)`, but if issues persist, check Flask logs

## Still Not Working?

1. Share the browser console error (F12 → Console)
2. Share Flask logs: `sudo journalctl -u bolna-flask -n 100`
3. Share what URL the browser is trying to use
4. Confirm Security Group allows port 5000

