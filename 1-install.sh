#!/bin/bash
set -e

ANACONDA_VERSION="2024.10-1"
ANACONDA_INSTALLER="Anaconda3-${ANACONDA_VERSION}-Linux-x86_64.sh"
ANACONDA_URL="https://repo.anaconda.com/archive/${ANACONDA_INSTALLER}"

# Download and install Anaconda if not already installed
if [ ! -d "$HOME/anaconda3" ]; then
    wget -q --show-progress "$ANACONDA_URL" -O "/tmp/$ANACONDA_INSTALLER"
    bash "/tmp/$ANACONDA_INSTALLER" -b
    rm -f "/tmp/$ANACONDA_INSTALLER"
    "$HOME/anaconda3/bin/conda" init bash
fi

source "$HOME/anaconda3/etc/profile.d/conda.sh"

# Install Hugging Face CLI
curl -LsSf https://hf.co/cli/install.sh | bash

# Install Claude Code
curl -fsSL https://claude.ai/install.sh | bash

# Install Vim
apt update
apt install -y vim

source "$HOME/anaconda3/etc/profile.d/conda.sh"

echo "Installation complete."
echo "Activate conda with: 'conda activate base'"
echo "Use Hugging Face CLI with: 'hf auth login'"
