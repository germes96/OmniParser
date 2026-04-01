#!/bin/bash
set -e

export LANG=C.UTF-8 LC_ALL=C.UTF-8

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> [1/3] Installing system dependencies..."
bash "$SCRIPT_DIR/1-install.sh"

echo "==> [2/3] Setting up conda environment..."
bash "$SCRIPT_DIR/3-setup.sh"

echo "==> [3/3] Starting OmniParser server..."
bash "$SCRIPT_DIR/4-run-server.sh" start

echo ""
echo "OmniParser is running on port 7860."
