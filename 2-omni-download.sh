#!/bin/bash
set -e

echo "Cleaning old weights..."
rm -rf weights/icon_detect weights/icon_detect_v3 weights/icon_caption weights/icon_caption_florence

# YOLOv9-E detector (MIT) lives in an unmerged HF PR. Once PR #37 is merged,
# drop --revision (and the weight can also auto-download on first use).
echo "Downloading OmniParser icon_detect_v3 (HF PR #37)..."
hf download microsoft/OmniParser-v2.0 icon_detect_v3/model.pt \
  --revision refs/pr/37 --local-dir weights

echo "Downloading Florence-2 icon caption model..."
hf download microsoft/OmniParser-v2.0 \
  icon_caption/config.json icon_caption/generation_config.json icon_caption/model.safetensors \
  --local-dir weights

echo "Renaming icon_caption to icon_caption_florence..."
mv weights/icon_caption weights/icon_caption_florence

test -f weights/icon_detect_v3/model.pt || { echo "Error: icon_detect_v3/model.pt missing after download" >&2; exit 1; }
echo "Done!"
