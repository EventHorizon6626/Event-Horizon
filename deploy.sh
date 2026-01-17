#!/bin/bash

# Event Horizon AI - Deployment Script for VPS
# This script deploys the AI service on Ubuntu/Debian VPS

set -e  # Exit on error

echo "🚀 Starting Event Horizon AI deployment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/var/www/event-horizon-ai"
SERVICE_NAME="event-horizon-ai"
PORT=5000

echo -e "${BLUE}📦 Step 1: Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

echo -e "${BLUE}📂 Step 2: Setting up application directory...${NC}"
if [ ! -d "$APP_DIR" ]; then
    sudo mkdir -p $APP_DIR
    sudo chown $USER:$USER $APP_DIR
fi

cd $APP_DIR

echo -e "${BLUE}🔄 Step 3: Pulling latest code...${NC}"
if [ -d ".git" ]; then
    git pull origin main
else
    echo "Git repository not initialized. Please clone first."
    exit 1
fi

echo -e "${BLUE}🐍 Step 4: Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

echo -e "${BLUE}📚 Step 5: Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${BLUE}⚙️  Step 6: Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${RED}⚠️  Please edit .env file with your API keys${NC}"
fi

echo -e "${BLUE}📋 Step 7: Setting up systemd service...${NC}"
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Event Horizon AI Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${BLUE}🔄 Step 8: Reloading systemd and starting service...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo -e "${BLUE}🔍 Step 9: Checking service status...${NC}"
sleep 3
sudo systemctl status $SERVICE_NAME --no-pager

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${GREEN}Service is running on port $PORT${NC}"
echo -e "${GREEN}Check logs: sudo journalctl -u $SERVICE_NAME -f${NC}"
echo -e "${GREEN}Test API: curl http://localhost:$PORT/health${NC}"
