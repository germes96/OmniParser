#!/bin/bash
eval "$(conda shell.bash hook 2>/dev/null)"
conda activate /workspace/envs/omni310/

python -m omnitool.omniparserserver.omniparserserver \
  --port 7860 \
  --device cuda \
  --som_model_path /workspace/OmniParser/weights/icon_detect/model.pt \
  --caption_model_path /workspace/OmniParser/weights/icon_caption_florence
