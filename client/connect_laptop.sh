#!/usr/bin/env bash
#
# Connects a SEPARATE laptop to your personal AI server via SSH, so the server
# can control that laptop. Run this on the MACHINE THAT RUNS THE SERVER.
#
# What it does:
#   1. Generates an SSH keypair for laptop control (if none exists).
#   2. Prints the PUBLIC key to copy onto the laptop's ~/.ssh/authorized_keys
#      (or uses ssh-copy-id if the laptop is reachable now).
#   3. Reminds you to fill in SSH_* settings in .env.
#
set -euo pipefail

SERVER_KEY="${SSH_KEY:-$HOME/.ssh/laptop_control}"

if [[ ! -f "$SERVER_KEY" ]]; then
  echo "Generating an ed25519 key for laptop control at $SERVER_KEY"
  ssh-keygen -t ed25519 -f "$SERVER_KEY" -N "" -C "personal-ai-laptop-control"
fi

echo
echo "STEP 1 — put this public key on the laptop:"
echo "  cat '${SERVER_KEY}.pub' and append it to the laptop's"
echo "  ~/.ssh/authorized_keys  (create if needed, chmod 600)."
echo
cat "${SERVER_KEY}.pub"
echo

if command -v ssh-copy-id >/dev/null 2>&1; then
  echo "STEP 2 (optional) — if the laptop is already reachable, run:"
  echo "  ssh-copy-id -i '${SERVER_KEY}.pub' USER@LAPTOP_IP"
fi

echo
echo "STEP 3 — in Model_Components/.env set:"
echo "  SSH_TARGET=USER@LAPTOP_IP"
echo "  SSH_KEY=${SERVER_KEY}"
echo "  SSH_PORT=22"
echo "  SSH_ALLOWED_DIRS=/home/USER   (or /path/you/allow)"
echo
echo "Then restart the server service so it picks up the config."
echo "  systemctl --user restart jarvis-server.service"