# Fix Reset Button on EC2 - Step by Step

## Issue
The reset button shows "Failed to fetch" error because the frontend can't reach the Flask backend.

## Solution

Run these commands on your EC2 instance:

```bash
# 1. Navigate to project directory
cd ~/dharwin_ai_callagent

# 2. Pull latest code
git pull origin master

# 3. Get your EC2 public IP
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "Your EC2 IP: $EC2_IP"

# 4. Create/update .env.local file with Flask backend URL
cat > .env.local << EOF
NEXT_PUBLIC_FLASK_BACKEND_URL=http://${EC2_IP}:5000
EOF

# 5. Verify the file was created correctly
cat .env.local

# 6. Rebuild Next.js (this is IMPORTANT - must rebuild to pick up the new code)
npm run build

# 7. Restart services
sudo systemctl restart bolna-nextjs
sudo systemctl restart bolna-flask

# 8. Check service status
sudo systemctl status bolna-nextjs --no-pager -l | head -20
sudo systemctl status bolna-flask --no-pager -l | head -20

# 9. Check if services are running on correct ports
netstat -tlnp | grep -E ':(3000|5000)'

# 10. Test Flask backend directly
curl http://localhost:5000/api/candidates

# 11. Test from browser (replace with your EC2 IP)
# Open: http://YOUR_EC2_IP:3000
```

## Verify Environment Variable is Set

Check if the environment variable is being used:

```bash
# Check Next.js service environment
sudo systemctl show bolna-nextjs | grep Environment

# Check .env.local file
cat .env.local

# View Next.js logs to see if it's using the correct backend URL
sudo journalctl -u bolna-nextjs -n 50 --no-pager | grep -i flask
```

## Troubleshooting

If it still doesn't work:

### 1. Check Security Group
Make sure port 5000 is open in EC2 Security Group:
- Go to EC2 Console → Security Groups
- Add inbound rule: Custom TCP, Port 5000, Source: 0.0.0.0/0

### 2. Check Flask is accessible
```bash
# From EC2 itself
curl http://localhost:5000/api/candidates

# Should return JSON data, not connection refused
```

### 3. Check Next.js build included the new code
```bash
# Search for getFlaskBackendUrl in the built files
grep -r "getFlaskBackendUrl" .next/ || echo "Not found - rebuild required"
```

### 4. Manual environment variable check
Open browser console on EC2 (F12) and check:
```javascript
console.log(process.env.NEXT_PUBLIC_FLASK_BACKEND_URL)
```

If it shows `undefined`, the environment variable isn't set correctly.

### 5. Alternative: Use relative URL (if both are on same domain)
If you're accessing via EC2 IP for both frontend and backend, you could modify `lib/config.ts` to use relative URLs instead:

```typescript
export const getFlaskBackendUrl = (): string => {
  if (typeof window !== 'undefined') {
    // If we're on EC2 and accessing via same origin, use relative URL
    const hostname = window.location.hostname;
    if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `http://${hostname}:5000`;
    }
    return process.env.NEXT_PUBLIC_FLASK_BACKEND_URL || 'http://localhost:5000'
  }
  return process.env.FLASK_BACKEND_URL || process.env.NEXT_PUBLIC_FLASK_BACKEND_URL || 'http://localhost:5000'
}
```

## Quick Fix Script

Run this all-in-one script on EC2:

```bash
#!/bin/bash
cd ~/dharwin_ai_callagent
git pull origin master
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "NEXT_PUBLIC_FLASK_BACKEND_URL=http://${EC2_IP}:5000" > .env.local
npm run build
sudo systemctl restart bolna-nextjs bolna-flask
echo "✅ Done! Check http://${EC2_IP}:3000"
```

Save as `fix-reset-button.sh`, make executable (`chmod +x fix-reset-button.sh`), and run it.

