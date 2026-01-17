# GitHub Actions CI/CD for AI Service

This workflow automatically deploys the Event Horizon AI Service to your VPS when you push to the `main` branch.

## Setup Instructions

### 1. Add GitHub Secrets

Go to: `https://github.com/EventHorizon6626/Event-Horizon/settings/secrets/actions`

Add these secrets (same as FE repo):

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SSH_HOST` | Your VPS IP address | `123.45.67.89` |
| `SSH_USERNAME` | SSH username | `vytrieu` |
| `SSH_PRIVATE_KEY` | SSH private key | Content from `~/.ssh/github_actions` |
| `SSH_PORT` | SSH port | `22` |
| `DEPLOY_PATH` | Path to EventHorizon directory | `/home/vytrieu/EventHorizon` |

### 2. How It Works

**Triggers:**
- Push to `main` branch
- Manual trigger via GitHub Actions UI

**What it does:**
1. Connects to VPS via SSH
2. Navigates to `Event-Horizon-AI` directory
3. Pulls latest code from `main` branch
4. Stops existing AI container
5. Rebuilds and starts AI service on port 5000
6. Tests health endpoint
7. Cleans up old Docker images

### 3. Verify Deployment

After deployment completes:
- AI API: `http://your-vps-ip:5000`
- Health check: `http://your-vps-ip:5000/health`
- API docs: `http://your-vps-ip:5000/docs`

### 4. Monitor

View deployment logs:
1. Go to `https://github.com/EventHorizon6626/Event-Horizon/actions`
2. Click on the latest workflow run
3. View real-time deployment logs

## Troubleshooting

**SSH Connection Failed:**
- Verify secrets are set correctly
- Check server firewall allows SSH

**Port 5000 in use:**
- Workflow stops existing container first
- If issue persists, manually stop: `docker stop eventhorizon-backend`

**Build failed:**
- Check Python dependencies in `requirements.txt`
- Verify `.env` file exists on server
- Check logs: `docker-compose logs backend`
