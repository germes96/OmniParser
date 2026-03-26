#!/bin/bash
set -e

WORKSPACE="/workspace"
ANACONDA_VERSION="2024.10-1"
ANACONDA_INSTALLER="Anaconda3-${ANACONDA_VERSION}-Linux-x86_64.sh"
ANACONDA_URL="https://repo.anaconda.com/archive/${ANACONDA_INSTALLER}"
INSTALL_PATH="$WORKSPACE/anaconda3"

# Download and install Anaconda if not already installed
if [ ! -d "$INSTALL_PATH" ]; then
    wget -q --show-progress "$ANACONDA_URL" -O "$WORKSPACE/$ANACONDA_INSTALLER"
    bash "$WORKSPACE/$ANACONDA_INSTALLER" -b -p "$INSTALL_PATH"
    rm -f "$WORKSPACE/$ANACONDA_INSTALLER"
fi

# Source conda
source "$INSTALL_PATH/etc/profile.d/conda.sh"

# Update PATH for future sessions
if ! grep -q "$INSTALL_PATH/bin" "$WORKSPACE/.bashrc"; then
    echo "export PATH=\"$INSTALL_PATH/bin:\$PATH\"" >> "$WORKSPACE/.bashrc"
fi

# Install Hugging Face CLI in the workspace environment
curl -LsSf https://hf.co/cli/install.sh | bash

# Reload PATH immediately
source "$WORKSPACE/.bashrc"

source /workspace/.bashrc

echo "Installation complete."
echo "Activate conda with: 'conda activate base'"
echo "Use Hugging Face CLI with: 'hf login'"
