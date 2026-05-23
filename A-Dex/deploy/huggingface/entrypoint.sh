#!/usr/bin/env bash
set -euo pipefail

# Ensure port is 7860 for Hugging Face
export PORT="${PORT:-7860}"
export HOST="0.0.0.0"

# Use a local path for DB to avoid permission issues in /data if it's a mount
export DB_PATH="${DB_PATH:-./adex.db}"
export MEDIA_DIR="${MEDIA_DIR:-./media}"

mkdir -p "$(dirname "$DB_PATH")" "$MEDIA_DIR"

echo "Node version:"
node -v

echo "Starting A-Dex Backend..."
cd /app/backend
npm start &
BACKEND_PID=$!

echo "Starting A-Dex Discord Bot..."
cd /app/discord-bot
if [ -n "${DISCORD_BOT_TOKEN:-}" ]; then
  python3 -m bot.main &
else
  echo "DISCORD_BOT_TOKEN not set, skipping bot."
fi

# Keep script alive as long as backend is running
wait "$BACKEND_PID"
