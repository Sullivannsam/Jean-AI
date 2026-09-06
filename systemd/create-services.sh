#!/usr/bin/env bash
# Installs the agent's systemd user units so the AI starts automatically at
# login. Run as the normal (non-root) user.
#
#   ./create-services.sh            # install + enable + start
#   ./create-services.sh --disable  # stop + disable only
#   ./create-services.sh --server   # install only the API server service
#   ./create-services.sh --terminal # install only presence + wake services
#
set -euo pipefail

MODEL_COMPONENTS="$(cd "$(dirname "$0")" && pwd)"
SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
UNIT_DIR="${SYSTEMD_USER_DIR}"
mkdir -p "${UNIT_DIR}"

UNITS="jarvis-server.service jarvis-presence.service jarvis-wake.service"
case "${1:-}" in
  --disable)
    systemctl --user disable ${UNITS}
    systemctl --user stop ${UNITS}
    echo "Services stopped and disabled."
    exit 0
    ;;
  --server)
    UNITS="jarvis-server.service"
    ;;
  --terminal)
    UNITS="jarvis-presence.service jarvis-wake.service"
    ;;
  *) ;;

esac

# Make paths absolute and stable regardless of where the repo actually lives.
for unit in ${UNITS}; do
  sed -e "s|/home/samm/Personal-Ai-Agent/Model_Components|${MODEL_COMPONENTS}|g" \
      "${MODEL_COMPONENTS}/systemd/${unit}" > "${UNIT_DIR}/${unit}"
done

systemctl --user daemon-reload
systemctl --user enable ${UNITS}
systemctl --user restart ${UNITS}

echo "Installed and started:"
for unit in ${UNITS}; do
  systemctl --user status "${unit}" --no-pager | head -n 3
done
echo
echo "Check logs with, e.g.:"
echo "  journalctl --user -u jarvis-server.service -f"