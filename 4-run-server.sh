#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$SCRIPT_DIR/server.log"

source "$HOME/anaconda3/etc/profile.d/conda.sh"
conda activate omni310

case "${1:-start}" in
  start)
    echo "Starting server..."
    nohup python -m omnitool.omniparserserver.omniparserserver \
      --port 7860 \
      --device cuda \
      --som_model_path "$SCRIPT_DIR/weights/icon_detect/model.pt" \
      --caption_model_path "$SCRIPT_DIR/weights/icon_caption_florence" \
      > "$LOG_FILE" 2>&1 &
    echo $! > "$SCRIPT_DIR/server.pid"
    echo "Server started (PID: $!). Logs: $LOG_FILE"
    ;;
  stop)
    if [ -f "$SCRIPT_DIR/server.pid" ]; then
      kill "$(cat "$SCRIPT_DIR/server.pid")" && rm -f "$SCRIPT_DIR/server.pid"
      echo "Server stopped."
    else
      echo "No server running."
    fi
    ;;
  logs)
    tail -f "$LOG_FILE"
    ;;
  help)
    echo "Usage: $0 {start|stop|logs|help}"
    echo "  start  - Start the server in background (default)"
    echo "  stop   - Stop the server"
    echo "  logs   - Follow server logs"
    echo "  help   - Show this message"
    ;;
  *)
    echo "Unknown command: $1"
    "$0" help
    ;;
esac
