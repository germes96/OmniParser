#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Creating virtualenv..."
python3 -m venv "$SCRIPT_DIR/.venv"
source "$SCRIPT_DIR/.venv/bin/activate"

echo "Installing PyTorch..."
pip install torch==2.2.2 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo "Verifying CUDA is actually usable..."
python -c "import torch, sys; sys.exit(0 if torch.cuda.is_available() else 1)" || {
    echo "Error: torch.cuda.is_available() is False. nvidia-smi may show a GPU while CUDA context init still fails (broken host GPU passthrough) — this host is bad, terminate this pod and try again." >&2
    exit 1
}

echo "Installing dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

echo "Installing build tools..."
pip install ninja packaging wheel

echo "Installing flash-attn..."
pip install flash_attn==2.5.8 --no-build-isolation

echo "Done!"
