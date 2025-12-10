# Nginx Reverse Proxy Setup

This guide shows how to set up Nginx as a reverse proxy for the Bolna Calling Agent application.

## Benefits

- Single entry point (port 80) for both frontend and backend
- Better security (don't expose multiple ports)
- SSL/TLS support (HTTPS)
- Load balancing (if needed in future)
- Better production setup

## Setup Steps

### 1. Install Nginx

```bash
sudo apt update
sudo apt install nginx -y
```

### 2. Copy Configuration

```bash
cd ~/dharwin_ai_callagent
sudo cp nginx/bolna-agent.conf /etc/nginx/sites-available/bolna-agent
sudo ln -s /etc/nginx/sites-available/bolna-agent /etc/nginx/sites-enabled/
```

### 3. Remove Default Site (Optional)

```bash
sudo rm /etc/nginx/sites-enabled/default
```

### 4. Test Configuration

```bash
sudo nginx -t
```

If you see "syntax is ok" and "test is successful", you're good to go!

### 5. Start/Restart Nginx

```bash
# Start nginx
sudo systemctl start nginx

# Enable nginx to start on boot
sudo systemctl enable nginx

# Restart nginx
sudo systemctl restart nginx
```

### 6. Update Security Group

Make sure your EC2 Security Group allows:
- **Port 80** (HTTP) - for nginx
- **Port 443** (HTTPS) - if you add SSL later

You can now **close ports 3000 and 5000** in Security Group since nginx handles everything.

## Access Points

After setup:
- **Frontend**: `http://YOUR_EC2_IP/` or `http://YOUR_EC2_IP:80`
- **Backend API**: `http://YOUR_EC2_IP/api/...`
- **Health Check**: `http://YOUR_EC2_IP/api/health`

## Configuration Details

The nginx config:
- Routes `/` → Next.js frontend (port 3000)
- Routes `/api/*` → Flask backend (port 5000)
- Routes `/health` and `/api/health` → Flask health check
- Includes CORS headers for API requests
- Supports WebSocket connections (for future features)
- Handles preflight OPTIONS requests

## Troubleshooting

### Check Nginx Status

```bash
sudo systemctl status nginx
```

### View Nginx Logs

```bash
# Error logs
sudo tail -f /var/log/nginx/error.log

# Access logs
sudo tail -f /var/log/nginx/access.log
```

### Test Configuration

```bash
sudo nginx -t
```

### Reload Configuration (without downtime)

```bash
sudo nginx -s reload
```

### Common Issues

**Issue**: 502 Bad Gateway
- **Cause**: Flask or Next.js not running
- **Fix**: `sudo systemctl status bolna-flask` and `sudo systemctl status bolna-nextjs`

**Issue**: 504 Gateway Timeout
- **Cause**: Backend taking too long to respond
- **Fix**: Increase timeouts in nginx config or check backend performance

**Issue**: CORS errors
- **Cause**: CORS headers not being forwarded
- **Fix**: The config already includes CORS headers, but check Flask CORS settings too

## Adding SSL/HTTPS (Optional but Recommended)

For production, you should add SSL:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

Then update nginx config to redirect HTTP to HTTPS.

## Auto-Setup via Deployment Script

The `ec2-deploy.sh` script automatically sets up nginx if:
- Nginx is installed
- The config file exists at `nginx/bolna-agent.conf`

To use it:
```bash
./ec2-deploy.sh
```

## Manual Setup

If you prefer to set up manually, use the configuration provided above and follow the steps.

