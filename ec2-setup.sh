#!/bin/bash

# AWS EC2 Setup Script for Bolna Calling Agent
# This script sets up the EC2 instance with all required dependencies

set -e  # Exit on error

echo "🚀 Starting EC2 Setup for Bolna Calling Agent..."
echo ""

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    git \
    curl \
    build-essential \
    nginx

# Verify installations
echo ""
echo "✅ Verifying installations..."
python3 --version
nodejs --version
npm --version
git --version

# Install ngrok
echo ""
echo "📦 Installing ngrok..."
if ! command -v ngrok &> /dev/null; then
    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
    sudo apt update && sudo apt install ngrok -y
    echo "✅ ngrok installed successfully"
else
    echo "✅ ngrok already installed"
fi

# Check ngrok version
ngrok version

echo ""
echo "✅ EC2 Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Clone your repository: git clone https://github.com/Developerodin/dharwin_ai_callagent.git"
echo "2. Create .env file with BOLNA_API_KEY"
echo "3. Run: cd dharwin_ai_callagent && ./ec2-deploy.sh"
echo ""

