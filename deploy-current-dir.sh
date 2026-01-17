#!/bin/bash

# Event Horizon AI - Deployment Script (Current Directory)
# This script deploys the AI service from the current directory

set -e  # Exit on error

echo "🚀 Starting Event Horizon AI deployment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
APP_DIR=$(pwd)
SERVICE_NAME="event-horizon-ai"
PORT=5000
USER=$(whoami)

echo -e "${BLUE}Current directory: $APP_DIR${NC}"
echo -e "${BLUE}User: $USER${NC}"

echo -e "${BLUE}📦 Step 1: Installing system dependencies...${NC}"
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

echo -e "${BLUE}🐍 Step 2: Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

echo -e "${BLUE}📚 Step 3: Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${BLUE}⚙️  Step 4: Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${RED}⚠️  Please edit .env file with your API keys${NC}"
    echo -e "${RED}    nano .env${NC}"
    echo -e "${RED}    Set: NEWS_API_KEY, API_HOST=127.0.0.1, API_PORT=5000${NC}"
fi

echo -e "${BLUE}📋 Step 5: Setting up systemd service...${NC}"
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

echo -e "${BLUE}🔄 Step 6: Reloading systemd and starting service...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

# Check if .env needs configuration
if grep -q "your_newsapi_key_here" .env 2>/dev/null || grep -q "0.0.0.0" .env 2>/dev/null; then
    echo -e "${RED}⚠️  .env file needs configuration!${NC}"
    echo -e "${RED}Please edit .env before starting the service:${NC}"
    echo -e "${BLUE}nano .env${NC}"
    echo ""
    echo -e "${BLUE}Required settings:${NC}"
    echo "NEWS_API_KEY=your_actual_key_here"
    echo "API_HOST=127.0.0.1"
    echo "API_PORT=5000"
    echo "LOG_LEVEL=INFO"
    echo ""
    echo -e "${BLUE}After configuring, run:${NC}"
    echo "sudo systemctl start event-horizon-ai"
    echo "sudo systemctl status event-horizon-ai"
    echo "curl http://localhost:5000/health"
else
    sudo systemctl restart $SERVICE_NAME
    echo -e "${BLUE}🔍 Step 7: Checking service status...${NC}"
    sleep 3
    sudo systemctl status $SERVICE_NAME --no-pager || true
fi

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${GREEN}App directory: $APP_DIR${NC}"
echo -e "${GREEN}Service name: $SERVICE_NAME${NC}"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo -e "  Start:   sudo systemctl start $SERVICE_NAME"
echo -e "  Stop:    sudo systemctl stop $SERVICE_NAME"
echo -e "  Restart: sudo systemctl restart $SERVICE_NAME"
echo -e "  Status:  sudo systemctl status $SERVICE_NAME"
echo -e "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo -e "  Test:    curl http://localhost:$PORT/health"
