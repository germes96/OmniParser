#!/bin/bash
set -e

export LANG=C.UTF-8 LC_ALL=C.UTF-8

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> [1/4] Installing system dependencies..."
bash "$SCRIPT_DIR/1-install.sh"

echo "==> [2/4] Setting up Python venv..."
bash "$SCRIPT_DIR/3-setup.sh"

echo "==> [3/4] Downloading model weights..."
bash "$SCRIPT_DIR/2-omni-download.sh"

echo "==> [4/4] Starting OmniParser server..."
bash "$SCRIPT_DIR/4-run-server.sh" start

echo ""
echo "OmniParser is running on port 7860."
