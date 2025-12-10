#!/bin/bash

# AWS EC2 Deployment Script for Bolna Calling Agent
# This script deploys the application and sets up systemd services

set -e  # Exit on error

PROJECT_DIR="/home/ubuntu/dharwin_ai_callagent"
SERVICE_USER="ubuntu"

echo "🚀 Starting Deployment for Bolna Calling Agent..."
echo ""

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env file template..."
    cat > "$PROJECT_DIR/.env" << EOF
BOLNA_API_KEY=your_bolna_api_key_here
AGENT_ID=your_agent_id_here
EOF
    echo "✅ Created .env file. Please edit it with your actual API keys:"
    echo "   nano $PROJECT_DIR/.env"
    echo ""
    read -p "Press Enter after you've updated .env file..."
fi

# Create Python virtual environment
echo "🐍 Setting up Python virtual environment..."
cd "$PROJECT_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install
npm run build
echo "✅ Node.js dependencies installed and built"

# Update Flask server for production (bind to 0.0.0.0)
echo "🔧 Configuring Flask server for production..."
if grep -q "app.run(debug=True, port=5000)" api_server.py; then
    sed -i "s/app.run(debug=True, port=5000)/app.run(debug=False, host='0.0.0.0', port=5000)/" api_server.py
    echo "✅ Flask server configured for production"
elif ! grep -q "host='0.0.0.0'" api_server.py; then
    echo "⚠️  Could not find Flask run configuration. Please manually update api_server.py"
fi

# Get EC2 public IP for Flask backend URL
EC2_PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "localhost")
FLASK_BACKEND_URL="http://${EC2_PUBLIC_IP}:5000"

echo ""
echo "📝 Setting Flask backend URL for Next.js: ${FLASK_BACKEND_URL}"
echo ""

# Create/update .env.local for Next.js
if [ -f .env.local ]; then
    # Update existing NEXT_PUBLIC_FLASK_BACKEND_URL or add it
    if grep -q "NEXT_PUBLIC_FLASK_BACKEND_URL" .env.local; then
        sed -i "s|NEXT_PUBLIC_FLASK_BACKEND_URL=.*|NEXT_PUBLIC_FLASK_BACKEND_URL=${FLASK_BACKEND_URL}|" .env.local
    else
        echo "NEXT_PUBLIC_FLASK_BACKEND_URL=${FLASK_BACKEND_URL}" >> .env.local
    fi
else
    echo "NEXT_PUBLIC_FLASK_BACKEND_URL=${FLASK_BACKEND_URL}" > .env.local
fi

echo "✅ Next.js environment configured"

# Create systemd service files
echo "⚙️  Creating systemd service files..."

# Flask Backend Service
sudo tee /etc/systemd/system/bolna-flask.service > /dev/null << EOF
[Unit]
Description=Bolna Flask API Server
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python api_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Next.js Frontend Service
sudo tee /etc/systemd/system/bolna-nextjs.service > /dev/null << EOF
[Unit]
Description=Bolna Next.js Frontend
After=network.target bolna-flask.service

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR
Environment="PORT=3000"
Environment="NODE_ENV=production"
Environment="NEXT_PUBLIC_FLASK_BACKEND_URL=${FLASK_BACKEND_URL}"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# ngrok Service (using dynamic URL - update if you have a reserved domain)
sudo tee /etc/systemd/system/bolna-ngrok.service > /dev/null << EOF
[Unit]
Description=Bolna ngrok Tunnel
After=network.target bolna-flask.service
Requires=bolna-flask.service

[Service]
Type=simple
User=$SERVICE_USER
ExecStart=/usr/bin/ngrok http 5000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service files created"

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Enable services
echo "🔌 Enabling services..."
sudo systemctl enable bolna-flask
sudo systemctl enable bolna-nextjs
sudo systemctl enable bolna-ngrok

# Start services
echo "▶️  Starting services..."
sudo systemctl restart bolna-flask
sleep 3
sudo systemctl restart bolna-nextjs
sleep 3
sudo systemctl restart bolna-ngrok

# Wait a bit for services to start
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
echo ""
sudo systemctl status bolna-flask --no-pager -l
echo ""
sudo systemctl status bolna-nextjs --no-pager -l
echo ""
sudo systemctl status bolna-ngrok --no-pager -l

# Get ngrok URL
echo ""
echo "🔗 Getting ngrok URL..."
sleep 3
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$NGROK_URL" ]; then
    echo "⚠️  Could not retrieve ngrok URL automatically."
    echo "   Check manually: curl http://localhost:4040/api/tunnels"
else
    echo "✅ ngrok URL: $NGROK_URL"
    echo "📝 Webhook URL: $NGROK_URL/api/webhook"
    echo ""
    echo "⚠️  IMPORTANT: Update your Bolna AI webhook URL to:"
    echo "   $NGROK_URL/api/webhook"
fi

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "Useful commands:"
echo "  View Flask logs:    sudo journalctl -u bolna-flask -f"
echo "  View Next.js logs:  sudo journalctl -u bolna-nextjs -f"
echo "  View ngrok logs:    sudo journalctl -u bolna-ngrok -f"
echo "  Restart all:        sudo systemctl restart bolna-flask bolna-nextjs bolna-ngrok"
echo "  Stop all:           sudo systemctl stop bolna-flask bolna-nextjs bolna-ngrok"
echo ""

