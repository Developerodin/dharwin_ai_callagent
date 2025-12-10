# AWS EC2 Deployment Guide

This guide will help you deploy the Bolna Calling Agent project to AWS EC2 with ngrok, Python Flask backend, and Next.js frontend all running as services.

## Prerequisites

- AWS EC2 instance running Ubuntu (20.04 or 22.04 LTS recommended)
- SSH access to your EC2 instance (you have the PEM key)
- Domain name or ngrok account (for webhook URLs)
- Bolna AI API key

## Step 1: Connect to EC2 Instance

```bash
ssh -i "odin_dec24.pem" ubuntu@ec2-65-2-5-37.ap-south-1.compute.amazonaws.com
```

**Important:** Replace `odin_dec24.pem` with the actual path to your PEM file if it's in a different location.

## Step 2: Initial Server Setup

Once connected, run the setup script:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required dependencies
sudo apt install -y python3 python3-pip python3-venv nodejs npm git nginx

# Install ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

Or use the provided setup script:

```bash
chmod +x ec2-setup.sh
./ec2-setup.sh
```

## Step 3: Clone Your Repository

```bash
cd /home/ubuntu
git clone https://github.com/Developerodin/dharwin_ai_callagent.git
cd dharwin_ai_callagent
```

## Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
nano .env
```

Add your configuration:

```env
BOLNA_API_KEY=your_bolna_api_key_here
AGENT_ID=your_agent_id_here  # Optional, will be created if not provided
```

Save and exit (Ctrl+X, then Y, then Enter).

## Step 5: Configure ngrok

### Option A: Using ngrok Free (Reserved Domain - Recommended for Production)

1. Sign up at https://dashboard.ngrok.com/
2. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
3. Configure ngrok:

```bash
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
```

4. Create a static domain (requires paid plan) or use the free dynamic domain:

```bash
# For free plan (URL changes on restart)
ngrok http 5000

# For paid plan with reserved domain
ngrok http 5000 --domain=your-domain.ngrok-free.app
```

### Option B: Create ngrok Configuration File

```bash
mkdir -p ~/.config/ngrok
nano ~/.config/ngrok/ngrok.yml
```

Add:

```yaml
version: "2"
authtoken: YOUR_NGROK_AUTHTOKEN
tunnels:
  flask:
    addr: 5000
    proto: http
    # domain: your-domain.ngrok-free.app  # Uncomment for reserved domain
```

## Step 6: Install Python Dependencies

```bash
cd /home/ubuntu/dharwin_ai_callagent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 7: Install Node.js Dependencies

```bash
cd /home/ubuntu/dharwin_ai_callagent
npm install
npm run build  # Build Next.js for production
```

## Step 8: Create Systemd Service Files

### Flask Backend Service

```bash
sudo nano /etc/systemd/system/bolna-flask.service
```

Add:

```ini
[Unit]
Description=Bolna Flask API Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/dharwin_ai_callagent
Environment="PATH=/home/ubuntu/dharwin_ai_callagent/venv/bin"
ExecStart=/home/ubuntu/dharwin_ai_callagent/venv/bin/python api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Next.js Frontend Service

```bash
sudo nano /etc/systemd/system/bolna-nextjs.service
```

Add:

```ini
[Unit]
Description=Bolna Next.js Frontend
After=network.target bolna-flask.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/dharwin_ai_callagent
Environment="PORT=3000"
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### ngrok Service

```bash
sudo nano /etc/systemd/system/bolna-ngrok.service
```

Add:

```ini
[Unit]
Description=Bolna ngrok Tunnel
After=network.target bolna-flask.service
Requires=bolna-flask.service

[Service]
Type=simple
User=ubuntu
ExecStart=/usr/bin/ngrok http 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**For reserved domain, use:**

```ini
[Unit]
Description=Bolna ngrok Tunnel
After=network.target bolna-flask.service
Requires=bolna-flask.service

[Service]
Type=simple
User=ubuntu
ExecStart=/usr/bin/ngrok http 5000 --domain=your-domain.ngrok-free.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Step 9: Update Flask Server for Production

The Flask server needs to bind to `0.0.0.0` (all interfaces) instead of `localhost` to be accessible externally.

Update `api_server.py`:

```python
# At the end of api_server.py, change:
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

## Step 10: Configure Security Groups

In AWS EC2 Console:

1. Go to **Security Groups** → Select your instance's security group
2. Add inbound rules:
   - **Type:** Custom TCP, **Port:** 5000, **Source:** 0.0.0.0/0 (for Flask)
   - **Type:** Custom TCP, **Port:** 3000, **Source:** 0.0.0.0/0 (for Next.js)
   - **Type:** SSH, **Port:** 22, **Source:** Your IP (for security)

## Step 11: Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable bolna-flask
sudo systemctl enable bolna-nextjs
sudo systemctl enable bolna-ngrok

# Start services
sudo systemctl start bolna-flask
sudo systemctl start bolna-nextjs
sudo systemctl start bolna-ngrok

# Check status
sudo systemctl status bolna-flask
sudo systemctl status bolna-nextjs
sudo systemctl status bolna-ngrok
```

## Step 12: Get ngrok URL

```bash
# Get ngrok URL via API
curl http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | grep -o 'https://[^"]*'
```

Or check the ngrok dashboard: http://localhost:4040 (if accessible)

Save this URL - you'll need it for the webhook configuration.

## Step 13: Configure Bolna AI Webhook

1. Log in to Bolna AI Dashboard: https://platform.bolna.ai/
2. Go to **Settings** → **Webhooks**
3. Set webhook URL to: `https://your-ngrok-url.ngrok-free.app/api/webhook`
4. Save the configuration

## Step 14: Verify Everything Works

### Check Flask Backend:
```bash
curl http://localhost:5000/api/health
# or
curl http://ec2-public-ip:5000/api/health
```

### Check Next.js Frontend:
```bash
curl http://localhost:3000
# or open in browser: http://ec2-public-ip:3000
```

### Check ngrok Tunnel:
```bash
curl http://localhost:4040/api/tunnels
```

### View Logs:
```bash
# Flask logs
sudo journalctl -u bolna-flask -f

# Next.js logs
sudo journalctl -u bolna-nextjs -f

# ngrok logs
sudo journalctl -u bolna-ngrok -f
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status bolna-flask

# Check logs
sudo journalctl -u bolna-flask -n 50

# Test manually
cd /home/ubuntu/dharwin_ai_callagent
source venv/bin/activate
python api_server.py
```

### Port Already in Use

```bash
# Check what's using port 5000
sudo lsof -i :5000

# Kill process if needed
sudo kill -9 <PID>
```

### ngrok Not Working

```bash
# Check ngrok status
sudo systemctl status bolna-ngrok

# Test ngrok manually
ngrok http 5000

# Check if authtoken is set
ngrok config check
```

### Can't Access from Browser

1. Check Security Group rules
2. Check if services are running: `sudo systemctl status bolna-flask bolna-nextjs`
3. Check firewall: `sudo ufw status`
4. Test locally first: `curl http://localhost:5000`

## Quick Commands Reference

```bash
# Start all services
sudo systemctl start bolna-flask bolna-nextjs bolna-ngrok

# Stop all services
sudo systemctl stop bolna-flask bolna-nextjs bolna-ngrok

# Restart all services
sudo systemctl restart bolna-flask bolna-nextjs bolna-ngrok

# View logs
sudo journalctl -u bolna-flask -f
sudo journalctl -u bolna-nextjs -f
sudo journalctl -u bolna-ngrok -f

# Check status
sudo systemctl status bolna-flask
sudo systemctl status bolna-nextjs
sudo systemctl status bolna-ngrok
```

## Updating the Application

```bash
cd /home/ubuntu/dharwin_ai_callagent
git pull
source venv/bin/activate
pip install -r requirements.txt
npm install
npm run build
sudo systemctl restart bolna-flask
sudo systemctl restart bolna-nextjs
```

## Optional: Use Nginx as Reverse Proxy

For better production setup, use Nginx to proxy requests:

```bash
sudo nano /etc/nginx/sites-available/bolna-agent
```

Add:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/bolna-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Security Recommendations

1. **Use HTTPS**: Configure SSL certificate (Let's Encrypt) for production
2. **Firewall**: Only open necessary ports
3. **SSH**: Use key-based authentication, disable password login
4. **Updates**: Regularly update system packages
5. **Monitoring**: Set up log monitoring and alerts

## Support

For issues:
- Check service logs: `sudo journalctl -u service-name -f`
- Verify environment variables: `cat .env`
- Test components individually
- Check AWS Security Groups

