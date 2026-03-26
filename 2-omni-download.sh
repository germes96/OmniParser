#!/bin/bash
set -e

echo "Cleaning old weights..."
rm -rf weights/icon_detect weights/icon_caption weights/icon_caption_florence

echo "Downloading OmniParser v2.0 models..."
hf download microsoft/OmniParser-v2.0 --local-dir weights

echo "Renaming icon_caption to icon_caption_florence..."
mv weights/icon_caption weights/icon_caption_florence

echo "Done!"
