#!/usr/bin/env bash
set -Eeuo pipefail

REPO_URL="https://github.com/EventHorizon6626/Event-Horizon-AI.git"
APP_DIR="/home/vytrieu/EventHorizon/Event-Horizon-AI"
BRANCH="main"

BASE_DIR="/home/vytrieu/EventHorizon"
LOG_DIR="$BASE_DIR/.deploy_logs"
LOG_FILE="$LOG_DIR/deploy_ai_loop.log"
SLEEP_SECONDS=120

VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="evth-ai"

mkdir -p "$LOG_DIR"

trap 'echo "[$(date -Is)] ERROR at line $LINENO" | tee -a "$LOG_FILE"' ERR

echo "[$(date -Is)] AI deploy loop started. interval=${SLEEP_SECONDS}s" | tee -a "$LOG_FILE"

while true; do
  echo "[$(date -Is)] ---- deploy tick ----" | tee -a "$LOG_FILE"

  if [ ! -d "$APP_DIR/.git" ]; then
    mkdir -p "$(dirname "$APP_DIR")"
    git clone "$REPO_URL" "$APP_DIR" 2>&1 | tee -a "$LOG_FILE"
  fi

  cd "$APP_DIR"

  git fetch origin 2>&1 | tee -a "$LOG_FILE"
  git checkout "$BRANCH" 2>&1 | tee -a "$LOG_FILE" || true
  git reset --hard "origin/$BRANCH" 2>&1 | tee -a "$LOG_FILE"

  # Create/update Python virtual environment
  if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR" 2>&1 | tee -a "$LOG_FILE"
  fi

  source "$VENV_DIR/bin/activate"

  pip install --upgrade pip 2>&1 | tee -a "$LOG_FILE"
  pip install -r requirements.txt 2>&1 | tee -a "$LOG_FILE"

  # Restart the FastAPI service
  sudo systemctl restart "$SERVICE_NAME" 2>&1 | tee -a "$LOG_FILE" || true

  echo "[$(date -Is)] ---- done ----" | tee -a "$LOG_FILE"
  sleep "$SLEEP_SECONDS"
done
