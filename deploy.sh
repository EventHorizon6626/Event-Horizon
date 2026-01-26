#!/usr/bin/env bash
set -Eeuo pipefail

# Event Horizon AI - Unified Deployment Script
# Usage: ./deploy.sh [docker|systemd] [--once]
#
# Modes:
#   docker  - Deploy using Docker Compose
#   systemd - Deploy using Python venv + systemd service
#
# Options:
#   --once  - Run deployment once and exit (no loop)

DEPLOYMENT_MODE="${1:-docker}"
RUN_ONCE=false

if [[ "${2:-}" == "--once" ]]; then
  RUN_ONCE=true
fi

# Configuration
REPO_URL="https://github.com/EventHorizon6626/Event-Horizon-AI.git"
APP_DIR="/home/vytrieu/EventHorizon/Event-Horizon-AI"
BRANCH="main"

BASE_DIR="/home/vytrieu/EventHorizon"
LOG_DIR="$BASE_DIR/.deploy_logs"
LOG_FILE="$LOG_DIR/deploy_${DEPLOYMENT_MODE}.log"
SLEEP_SECONDS=120

# Mode-specific configuration
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="evth-ai"
CONTAINER_NAME="event-horizon-ai"

mkdir -p "$LOG_DIR"

trap 'echo "[$(date -Is)] ERROR at line $LINENO" | tee -a "$LOG_FILE"' ERR

# Functions
git_sync() {
  echo "[$(date -Is)] Syncing repository..." | tee -a "$LOG_FILE"

  if [ ! -d "$APP_DIR/.git" ]; then
    echo "[$(date -Is)] Cloning repository..." | tee -a "$LOG_FILE"
    mkdir -p "$(dirname "$APP_DIR")"
    git clone "$REPO_URL" "$APP_DIR" 2>&1 | tee -a "$LOG_FILE"
  fi

  cd "$APP_DIR"
  git fetch origin 2>&1 | tee -a "$LOG_FILE"
  git checkout "$BRANCH" 2>&1 | tee -a "$LOG_FILE" || true
  git reset --hard "origin/$BRANCH" 2>&1 | tee -a "$LOG_FILE"
}

deploy_docker() {
  echo "[$(date -Is)] Deploying with Docker Compose..." | tee -a "$LOG_FILE"

  echo "[$(date -Is)] Building Docker image..." | tee -a "$LOG_FILE"
  docker-compose build 2>&1 | tee -a "$LOG_FILE"

  echo "[$(date -Is)] Stopping old container..." | tee -a "$LOG_FILE"
  docker-compose down 2>&1 | tee -a "$LOG_FILE" || true

  echo "[$(date -Is)] Starting new container..." | tee -a "$LOG_FILE"
  docker-compose up -d 2>&1 | tee -a "$LOG_FILE"

  # Health check
  echo "[$(date -Is)] Waiting for container to be healthy..." | tee -a "$LOG_FILE"
  sleep 10

  if docker ps | grep -q "$CONTAINER_NAME"; then
    echo "[$(date -Is)] ✓ Container is running" | tee -a "$LOG_FILE"

    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
      echo "[$(date -Is)] ✓ Health check passed" | tee -a "$LOG_FILE"
    else
      echo "[$(date -Is)] ⚠ Health check failed (container may still be starting)" | tee -a "$LOG_FILE"
    fi
  else
    echo "[$(date -Is)] ✗ Container failed to start" | tee -a "$LOG_FILE"
    docker-compose logs --tail=50 2>&1 | tee -a "$LOG_FILE"
  fi

  # Cleanup
  echo "[$(date -Is)] Cleaning up old Docker images..." | tee -a "$LOG_FILE"
  docker image prune -f 2>&1 | tee -a "$LOG_FILE" || true
}

deploy_systemd() {
  echo "[$(date -Is)] Deploying with systemd service..." | tee -a "$LOG_FILE"

  # Create/update Python virtual environment
  if [ ! -d "$VENV_DIR" ]; then
    echo "[$(date -Is)] Creating virtual environment..." | tee -a "$LOG_FILE"
    python3 -m venv "$VENV_DIR" 2>&1 | tee -a "$LOG_FILE"
  fi

  source "$VENV_DIR/bin/activate"

  echo "[$(date -Is)] Installing dependencies..." | tee -a "$LOG_FILE"
  pip install --upgrade pip 2>&1 | tee -a "$LOG_FILE"
  pip install -r requirements.txt 2>&1 | tee -a "$LOG_FILE"

  # Restart the FastAPI service
  echo "[$(date -Is)] Restarting systemd service..." | tee -a "$LOG_FILE"
  sudo systemctl restart "$SERVICE_NAME" 2>&1 | tee -a "$LOG_FILE" || true

  # Check service status
  if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "[$(date -Is)] ✓ Service is running" | tee -a "$LOG_FILE"
  else
    echo "[$(date -Is)] ✗ Service failed to start" | tee -a "$LOG_FILE"
    sudo systemctl status "$SERVICE_NAME" 2>&1 | tee -a "$LOG_FILE" || true
  fi
}

deploy() {
  echo "[$(date -Is)] ---- deploy tick ----" | tee -a "$LOG_FILE"

  git_sync

  case "$DEPLOYMENT_MODE" in
    docker)
      deploy_docker
      ;;
    systemd)
      deploy_systemd
      ;;
    *)
      echo "[$(date -Is)] ERROR: Unknown deployment mode: $DEPLOYMENT_MODE" | tee -a "$LOG_FILE"
      echo "Usage: $0 [docker|systemd] [--once]" | tee -a "$LOG_FILE"
      exit 1
      ;;
  esac

  echo "[$(date -Is)] ---- done ----" | tee -a "$LOG_FILE"
}

# Main execution
echo "[$(date -Is)] Event Horizon AI deployment started" | tee -a "$LOG_FILE"
echo "[$(date -Is)] Mode: $DEPLOYMENT_MODE" | tee -a "$LOG_FILE"
echo "[$(date -Is)] Run once: $RUN_ONCE" | tee -a "$LOG_FILE"

if [ "$RUN_ONCE" = true ]; then
  deploy
  echo "[$(date -Is)] Single deployment completed" | tee -a "$LOG_FILE"
else
  echo "[$(date -Is)] Starting deployment loop (interval=${SLEEP_SECONDS}s)" | tee -a "$LOG_FILE"
  while true; do
    deploy
    sleep "$SLEEP_SECONDS"
  done
fi
