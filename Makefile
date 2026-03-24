SHELL := /bin/bash
CONDA_ENV := omni
PYTHON_VERSION := 3.12
WEIGHTS_DIR := weights
CONDA_ACTIVATE := eval "$$(conda shell.bash hook 2>/dev/null)" && conda activate $(CONDA_ENV)

.PHONY: check-conda check-hf setup install weights run clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

check-conda: ## Check if conda is installed
	@command -v conda >/dev/null 2>&1 || { echo "Error: conda is not installed. Install Miniconda or Anaconda first."; exit 1; }
	@echo "conda found: $$(conda --version)"

check-hf: ## Check if huggingface-cli is installed
	@command -v huggingface-cli >/dev/null 2>&1 || { echo "Error: huggingface-cli is not installed. Run: pip install huggingface_hub"; exit 1; }
	@echo "huggingface-cli found: $$(huggingface-cli version 2>/dev/null || echo 'ok')"

setup: check-conda ## Create conda environment
	@if conda env list | grep -q "^$(CONDA_ENV) "; then \
		echo "Conda env '$(CONDA_ENV)' already exists. Skipping creation."; \
	else \
		echo "Creating conda env '$(CONDA_ENV)' with Python $(PYTHON_VERSION)..."; \
		conda create -n $(CONDA_ENV) python==$(PYTHON_VERSION) -y; \
	fi

install: setup ## Install pip dependencies into conda env
	$(CONDA_ACTIVATE) && pip install -r requirements.txt

weights: check-hf ## Download model weights from HuggingFace
	@mkdir -p $(WEIGHTS_DIR)
	@for f in icon_detect/train_args.yaml icon_detect/model.pt icon_detect/model.yaml icon_caption/config.json icon_caption/generation_config.json icon_caption/model.safetensors; do \
		echo "Downloading $$f..."; \
		huggingface-cli download microsoft/OmniParser-v2.0 "$$f" --local-dir $(WEIGHTS_DIR); \
	done
	@if [ -d "$(WEIGHTS_DIR)/icon_caption" ] && [ ! -d "$(WEIGHTS_DIR)/icon_caption_florence" ]; then \
		mv $(WEIGHTS_DIR)/icon_caption $(WEIGHTS_DIR)/icon_caption_florence; \
		echo "Renamed icon_caption -> icon_caption_florence"; \
	fi
	@echo "Weights downloaded to $(WEIGHTS_DIR)/"

run: ## Run the Gradio demo (auto-creates env if missing)
	@if ! conda env list | grep -q "^$(CONDA_ENV) "; then \
		echo "Conda env '$(CONDA_ENV)' not found. Creating..."; \
		conda create -n $(CONDA_ENV) python==$(PYTHON_VERSION) -y; \
		$(CONDA_ACTIVATE) && pip install -r requirements.txt; \
	fi
	$(CONDA_ACTIVATE) && python gradio_demo.py

all: install weights ## Full setup: create env, install deps, download weights

clean: ## Remove conda environment
	@echo "Removing conda env '$(CONDA_ENV)'..."
	conda env remove -n $(CONDA_ENV) -y
