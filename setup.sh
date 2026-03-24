#!/bin/bash

set -e

ENV_PATH="/workspace/envs/omni310"

echo "🚀 Creating conda env in /workspace..."
conda create --prefix $ENV_PATH python=3.10 -y

echo "🔁 Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_PATH

echo "⚙️ Installing PyTorch..."
pip install torch==2.2.2 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo "📦 Installing dependencies..."
cd /workspace/OmniParser
pip install -r requirements.txt

echo "🧩 Installing build tools..."
pip install ninja packaging

echo "⚡ Installing flash-attn..."
pip install flash_attn==2.5.8 --no-build-isolation


# Source conda
source "$INSTALL_PATH/etc/profile.d/conda.sh"

# Initialize conda for bash (adds required shell functions)
conda init bash

source ~/.bashrc

echo "✅ Done!"
