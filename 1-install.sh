#!/bin/bash
set -e

# Install Hugging Face CLI
curl -LsSf https://hf.co/cli/install.sh | bash

echo "Installation complete."
echo "Use Hugging Face CLI with: 'hf auth login'"
