#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/bopi/Desktop/tim-bot/brain"
SERVICE_NAME="tim-bot.service"
SERVICE_SRC="$PROJECT_DIR/startup/$SERVICE_NAME"
SERVICE_DEST="/etc/systemd/system/$SERVICE_NAME"
AUTOSTART_DIR="/home/bopi/.config/autostart"
AUTOSTART_SRC="$PROJECT_DIR/startup/tim-bot.desktop"
AUTOSTART_DEST="$AUTOSTART_DIR/tim-bot.desktop"

if [[ ! -f "$SERVICE_SRC" ]]; then
  echo "Missing service file: $SERVICE_SRC" >&2
  exit 1
fi

if [[ ! -f "$AUTOSTART_SRC" ]]; then
  echo "Missing desktop file: $AUTOSTART_SRC" >&2
  exit 1
fi

sudo install -m 0644 "$SERVICE_SRC" "$SERVICE_DEST"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

mkdir -p "$AUTOSTART_DIR"
install -m 0644 "$AUTOSTART_SRC" "$AUTOSTART_DEST"

echo "Installed $SERVICE_DEST"
echo "Installed $AUTOSTART_DEST"
echo "Boot service status:"
sudo systemctl --no-pager --full status "$SERVICE_NAME" || true
