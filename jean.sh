#!/usr/bin/env bash
# Jean — launch the local AI agent.
# Usage: jean [text | voice | wake | status]
set -euo pipefail

AGENT_DIR="${JEAN_DIR:-$HOME/Personal-Ai-Agent/Model_Components}"
cd "$AGENT_DIR"

# NOTE: this used to unload the model from RAM on every exit (via `ollama
# stop`) to save memory. That directly fights OLLAMA_KEEP_ALIVE, which keeps
# the model warm between messages — every fresh `jean` launch was paying a
# full model reload from a cold unload the previous session left behind.
# Disabled by default now for speed (model stays resident, ~4.7GB RAM).
# Set JEAN_UNLOAD_ON_EXIT=true if you want the RAM back instead.
cleanup() {
    if [ "${JEAN_UNLOAD_ON_EXIT:-false}" = "true" ] && command -v ollama >/dev/null 2>&1 && ollama ps 2>/dev/null | grep -q .; then
        ollama ps 2>/dev/null | tail -n +2 | awk '{print $1}' | while read -r m; do
            ollama stop "$m" >/dev/null 2>&1 || true
        done
    fi
}
trap cleanup EXIT

MODE="${1:-text}"
case "$MODE" in
    text)   python3 agent.py ;;
    voice)  python3 agent.py --voice ;;
    wake)   python3 agent.py --wake ;;
    status) python3 agent.py --status ;;
    -h|--help|help)
        echo "Jean — your local AI agent"
        echo
        echo "Usage:"
        echo "  jean              start text chat"
        echo "  jean voice        start voice chat"
        echo "  jean wake         always-listening (say 'hey jarvis')"
        echo "  jean status       health check"
        ;;
    *) echo "Unknown mode: $MODE (use: text, voice, wake, status)"; exit 1 ;;
esac