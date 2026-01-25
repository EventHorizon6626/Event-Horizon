#!/usr/bin/env bash
set -Eeuo pipefail

REPO_URL="https://github.com/EventHorizon6626/Event-Horizon-AI.git"
APP_DIR="/home/vytrieu/EventHorizon/Event-Horizon-AI"
BRANCH="main"

BASE_DIR="/home/vytrieu/EventHorizon"
LOG_DIR="$BASE_DIR/.deploy_logs"
LOG_FILE="$LOG_DIR/deploy_ai_docker.log"
SLEEP_SECONDS=120

CONTAINER_NAME="event-horizon-ai"

mkdir -p "$LOG_DIR"

trap 'echo "[$(date -Is)] ERROR at line $LINENO" | tee -a "$LOG_FILE"' ERR

echo "[$(date -Is)] AI Docker deploy loop started. interval=${SLEEP_SECONDS}s" | tee -a "$LOG_FILE"

while true; do
  echo "[$(date -Is)] ---- deploy tick ----" | tee -a "$LOG_FILE"

  # Clone repo if not exists
  if [ ! -d "$APP_DIR/.git" ]; then
    mkdir -p "$(dirname "$APP_DIR")"
    git clone "$REPO_URL" "$APP_DIR" 2>&1 | tee -a "$LOG_FILE"
  fi

  cd "$APP_DIR"

  # Pull latest code
  git fetch origin 2>&1 | tee -a "$LOG_FILE"
  git checkout "$BRANCH" 2>&1 | tee -a "$LOG_FILE" || true
  git reset --hard "origin/$BRANCH" 2>&1 | tee -a "$LOG_FILE"

  # Build and deploy with Docker Compose
  echo "[$(date -Is)] Building Docker image..." | tee -a "$LOG_FILE"
  docker-compose build 2>&1 | tee -a "$LOG_FILE"

  echo "[$(date -Is)] Stopping old container..." | tee -a "$LOG_FILE"
  docker-compose down 2>&1 | tee -a "$LOG_FILE" || true

  echo "[$(date -Is)] Starting new container..." | tee -a "$LOG_FILE"
  docker-compose up -d 2>&1 | tee -a "$LOG_FILE"

  # Wait for health check
  echo "[$(date -Is)] Waiting for container to be healthy..." | tee -a "$LOG_FILE"
  sleep 10

  # Check container status
  if docker ps | grep -q "$CONTAINER_NAME"; then
    echo "[$(date -Is)] ✓ Container is running" | tee -a "$LOG_FILE"

    # Test health endpoint
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
      echo "[$(date -Is)] ✓ Health check passed" | tee -a "$LOG_FILE"
    else
      echo "[$(date -Is)] ⚠ Health check failed (container may still be starting)" | tee -a "$LOG_FILE"
    fi
  else
    echo "[$(date -Is)] ✗ Container failed to start" | tee -a "$LOG_FILE"
    docker-compose logs --tail=50 2>&1 | tee -a "$LOG_FILE"
  fi

  # Clean up old images
  echo "[$(date -Is)] Cleaning up old Docker images..." | tee -a "$LOG_FILE"
  docker image prune -f 2>&1 | tee -a "$LOG_FILE" || true

  echo "[$(date -Is)] ---- done ----" | tee -a "$LOG_FILE"
  sleep "$SLEEP_SECONDS"
done
