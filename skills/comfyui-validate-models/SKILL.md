---
name: comfyui-validate-models
description: >
  List available models on the ComfyUI server and validate whether specific
  models exist. Use this skill when the user asks what models, LoRAs, or
  checkpoints are available, or before using a specific model to verify it
  exists on the server. Can filter by model group (checkpoints, vae, clip,
  lora, unet) and check for specific model names.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
metadata.clawdbot.tags: ["models", "validation", "lora", "checkpoint", "utility", "comfyui"]
metadata.clawdbot.category: "utility"
metadata.clawdbot.input_type: "text"
metadata.clawdbot.output_type: "text/json"
metadata.clawdbot.output_can_feed_into: []
metadata.clawdbot.accepts_input_from: []
metadata.clawdbot.priority: 50
---

# ComfyUI Validate Models

List available models on the ComfyUI server and validate whether specific models exist.

## When to use this skill

- User asks "what models are available?" or "do you have [model name]?"
- Before using a specific LoRA, checkpoint, or VAE to verify it exists
- Discovering what capabilities the server has
- User wants to browse available models for a generation task

## When NOT to use this skill

- You want to check **server health** → use `comfyui-server-status`
- You want to **generate** an image (just use the generation skill; it uses default models)
- You want to list **generated files** → use `comfyui-list-assets`

## Usage

```bash
python3 scripts/run.py [--models <comma-separated>] [--groups <comma-separated>]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--models` | No | Comma-separated list of model names to validate |
| `--groups` | No | Comma-separated model groups to list: checkpoints, vae, clip, lora, unet (default: all) |

### Examples

```bash
# List all available models
python3 scripts/run.py

# List only checkpoints and LoRAs
python3 scripts/run.py --groups checkpoints,lora

# Check if specific models exist
python3 scripts/run.py --models "juggernaut_reborn.safetensors,my_lora.safetensors"

# Combine: list LoRAs and validate specific ones
python3 scripts/run.py --groups lora --models "pixel_art.safetensors,anime_style.safetensors"
```

### Output

JSON object with available models and validation results:
```json
{
  "status": "success",
  "available_models": {
    "checkpoints": ["sd1.5/juggernaut_reborn.safetensors"],
    "lora": ["pixel_art.safetensors"]
  },
  "validation": {
    "juggernaut_reborn.safetensors": true,
    "missing_model.safetensors": false
  }
}
```

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/object_info` | Get node definitions with model lists | None (GET request) |
