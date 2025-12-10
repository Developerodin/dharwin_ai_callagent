# EC2 Rebuild Instructions

If you're still seeing `localhost:5000` errors after pulling the latest code, you need to rebuild the Next.js application.

## Quick Fix

```bash
# SSH into EC2
ssh -i "odin_dec24.pem" ubuntu@ec2-65-2-5-37.ap-south-1.compute.amazonaws.com

# Navigate to project directory
cd ~/dharwin_ai_callagent

# Pull latest code
git pull origin master

# Clean build (important - removes old cached bundles)
rm -rf .next
rm -rf node_modules/.cache

# Rebuild Next.js with fresh environment
npm run build

# Restart services
sudo systemctl restart bolna-flask
sudo systemctl restart bolna-nextjs

# Check service status
sudo systemctl status bolna-nextjs
sudo systemctl status bolna-flask

# View logs to verify
sudo journalctl -u bolna-nextjs -n 50 -f
```

## Verify It's Working

1. Open browser DevTools (F12)
2. Go to Console tab
3. Refresh the page
4. Look for log messages like:
   - `[Config] Auto-detected backend URL: http://65.2.5.37:5000`
   
5. Try clicking the reset button
6. Check Network tab - the request should go to `http://65.2.5.37:5000/api/candidate/1/reset`, NOT `localhost:5000`

## If Still Not Working

### Clear Browser Cache
- Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Or clear browser cache completely

### Check Environment Variables
```bash
# On EC2, check if environment variable is set
cat ~/dharwin_ai_callagent/.env.local | grep FLASK_BACKEND_URL

# Should show:
# NEXT_PUBLIC_FLASK_BACKEND_URL=http://65.2.5.37:5000
```

### Manual Check of Built Code
```bash
# Check if the config helper is in the build
grep -r "Auto-detected backend URL" ~/dharwin_ai_callagent/.next/static/chunks/ 2>/dev/null | head -5
```

If you see the grep output, the new code is built. If not, the build might have failed silently.

## Force Complete Rebuild

```bash
cd ~/dharwin_ai_callagent

# Stop services
sudo systemctl stop bolna-nextjs
sudo systemctl stop bolna-flask

# Clean everything
rm -rf .next
rm -rf node_modules
rm -rf .env.local

# Reinstall dependencies
npm install

# Set environment variable (adjust IP if different)
echo "NEXT_PUBLIC_FLASK_BACKEND_URL=http://65.2.5.37:5000" > .env.local

# Rebuild
npm run build

# Restart services
sudo systemctl start bolna-flask
sudo systemctl start bolna-nextjs
```

