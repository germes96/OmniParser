#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Creating virtualenv..."
python3 -m venv "$SCRIPT_DIR/.venv"
source "$SCRIPT_DIR/.venv/bin/activate"

echo "Installing PyTorch..."
pip install torch==2.2.2 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo "Installing dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

echo "Installing build tools..."
pip install ninja packaging

echo "Installing flash-attn..."
pip install flash_attn==2.5.8 --no-build-isolation

echo "Done!"
