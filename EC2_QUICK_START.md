# Quick Start: Deploy to AWS EC2

## Step 1: Connect to EC2

```bash
ssh -i "odin_dec24.pem" ubuntu@ec2-65-2-5-37.ap-south-1.compute.amazonaws.com
```

## Step 2: Run Setup Script

```bash
# Clone repository (if not already done)
git clone https://github.com/Developerodin/dharwin_ai_callagent.git
cd dharwin_ai_callagent

# Make scripts executable
chmod +x ec2-setup.sh ec2-deploy.sh

# Run initial setup
./ec2-setup.sh
```

## Step 3: Configure ngrok

```bash
# Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
```

## Step 4: Create .env File

```bash
nano .env
```

Add:
```env
BOLNA_API_KEY=your_bolna_api_key_here
AGENT_ID=your_agent_id_here
```

## Step 5: Deploy

```bash
./ec2-deploy.sh
```

## Step 6: Get ngrok URL

```bash
# Wait a few seconds for ngrok to start, then:
curl http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4
```

## Step 7: Configure Bolna AI Webhook

1. Copy the ngrok URL from Step 6
2. Go to: https://platform.bolna.ai/ → Settings → Webhooks
3. Set webhook URL to: `https://your-ngrok-url.ngrok-free.app/api/webhook`

## Done! 🎉

Access your application:
- **Frontend:** http://YOUR_EC2_PUBLIC_IP:3000
- **Backend API:** http://YOUR_EC2_PUBLIC_IP:5000
- **ngrok Dashboard:** http://localhost:4040 (on EC2)

## Useful Commands

```bash
# View logs
sudo journalctl -u bolna-flask -f
sudo journalctl -u bolna-nextjs -f
sudo journalctl -u bolna-ngrok -f

# Restart services
sudo systemctl restart bolna-flask bolna-nextjs bolna-ngrok

# Check status
sudo systemctl status bolna-flask
sudo systemctl status bolna-nextjs
sudo systemctl status bolna-ngrok

# Stop services
sudo systemctl stop bolna-flask bolna-nextjs bolna-ngrok
```

## Troubleshooting

If something doesn't work:
1. Check service status: `sudo systemctl status bolna-flask`
2. Check logs: `sudo journalctl -u bolna-flask -n 50`
3. Verify .env file: `cat .env`
4. Test manually: `source venv/bin/activate && python api_server.py`

For detailed instructions, see [DEPLOY_EC2.md](./DEPLOY_EC2.md)

