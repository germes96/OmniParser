#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

source "$HOME/anaconda3/etc/profile.d/conda.sh"

echo "Creating conda environment..."
conda create -n omni310 python=3.10 -y
conda activate omni310

echo "Installing PyTorch..."
pip install torch==2.2.2 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo "Installing dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

echo "Installing build tools..."
pip install ninja packaging

echo "Installing flash-attn..."
pip install flash_attn==2.5.8 --no-build-isolation

echo "Done!"
