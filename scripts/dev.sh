#!/usr/bin/env bash
# Run Spenzo locally and give WhatsApp a public URL to reach it.
#   ./scripts/dev.sh
# Needs: .env filled in, and cloudflared (brew install cloudflared).
set -euo pipefail
cd "$(dirname "$0")/.."

command -v cloudflared >/dev/null || { echo "Install cloudflared first: brew install cloudflared"; exit 1; }
[ -f .env ] || { echo "Create .env first: cp .env.example .env"; exit 1; }

if lsof -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Something is already running on port 8000 (probably Spenzo). Stop it first, or keep using it."
  exit 1
fi

uv run uvicorn server.bot:app --port 8000 &
BOT=$!
sleep 3
kill -0 $BOT 2>/dev/null || { echo "The bot didn't start; see the error above."; exit 1; }
trap 'kill $BOT 2>/dev/null' EXIT

LOG=$(mktemp)
cloudflared tunnel --no-autoupdate --url http://localhost:8000 >"$LOG" 2>&1 &
TUNNEL=$!
trap 'kill $BOT $TUNNEL 2>/dev/null; rm -f "$LOG"' EXIT

for _ in $(seq 1 30); do
  URL=$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$LOG" | head -1 || true)
  [ -n "$URL" ] && break
  sleep 1
done
[ -n "${URL:-}" ] || { echo "Tunnel didn't start:"; cat "$LOG"; exit 1; }

echo
echo "  Spenzo is running."
echo "  Paste this into Meta → WhatsApp → Configuration → Webhook → Callback URL:"
echo
echo "      $URL/webhook"
echo
echo "  Verify token: the WHATSAPP_VERIFY_TOKEN from your .env"
echo "  Press Ctrl+C to stop."
wait $BOT
