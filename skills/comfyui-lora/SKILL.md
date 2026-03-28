---
name: comfyui-lora
description: "Generate images using a LoRA (Low-Rank Adaptation) model for specific styles or characters. Use this skill when the user mentions a specific LoRA model, wants a consistent character or brand style, or asks for a specialized art style that requires a LoRA adapter. The user must specify which LoRA file to use. If you don't know which LoRA is available, use comfyui-validate-models to list available LoRA models before asking the user. For general image generation without LoRA, use comfyui-generate-image instead."
homepage: https://github.com/ilker-tff/comfyclaw
metadata: {
    "openclaw": {
        "os": [
            "darwin",
            "linux"
        ],
        "requires": {
            "bins": [
                "python3"
            ],
            "env": [
                "COMFY_URL",
                "COMFY_AUTH_HEADER"
            ]
        },
        "tags": [
            "lora",
            "style",
            "character",
            "fine-tuned",
            "comfyui"
        ],
        "category": "media-generation",
        "input_type": "text",
        "output_type": "image/png",
        "output_can_feed_into": [
            "comfyui-crop",
            "comfyui-img2img-remix",
            "comfyui-crop-then-refine",
            "comfyui-img2video",
            "comfyui-download-image"
        ],
        "accepts_input_from": [],
        "priority": 75,
        "files": [
            "scripts/*"
        ]
    }
}
---

# ComfyUI LoRA Generation

Generate images using Stable Diffusion 1.5 with a LoRA adapter for specialized styles or characters.

## When to use this skill

- User mentions a specific **LoRA model** by name
- User wants a **consistent character** or **brand style** across multiple images
- User asks for a style that requires fine-tuning (specific art styles, characters, products)
- User says "use the [name] LoRA" or "apply the [style] model"

## When NOT to use this skill

- User wants general image generation → use `comfyui-generate-image`
- User doesn't mention a specific LoRA → use `comfyui-generate-image`
- User wants to transform an existing image → use `comfyui-img2img-remix`

## Important: LoRA availability

Before using this skill, you need to know which LoRA files are installed on the server. If you're unsure, ask the user: "Which LoRA model would you like to use?"

## Usage

```bash
python3 scripts/run.py "<prompt>" <output-path> --lora "<lora-filename>" [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--lora` | required | LoRA filename (e.g. `"style_lora.safetensors"`) |
| `--strength` | 1.0 | LoRA strength (0.0-2.0, higher = stronger effect) |
| `--width` | 512 | Image width |
| `--height` | 512 | Image height |
| `--steps` | 35 | Sampling steps |
| `--cfg` | 7.0 | Guidance scale |
| `--seed` | random | Seed |
| `--negative` | `"watermark, text, blurry, low quality, deformed"` | Negative prompt |

### Strength guide

- **0.5**: Subtle LoRA influence — blended with base model
- **1.0**: Full strength — standard LoRA application (default)
- **1.5**: Overshoot — exaggerated LoRA style (may cause artifacts)

### Examples

```bash
# Apply a style LoRA
python3 scripts/run.py "a castle on a hill at sunset" castle.png --lora "watercolor_style.safetensors" --strength 0.8

# Character LoRA at full strength
python3 scripts/run.py "a warrior in battle stance" warrior.png --lora "fantasy_character.safetensors"
```

## Chaining

Output can be fed into:
- `comfyui-crop` to extract a region
- `comfyui-img2img-remix` to further restyle
- `comfyui-crop-then-refine` to crop and enhance

## Confirm before running

> "I'll generate an image using LoRA [lora_name] at strength [strength]. Go ahead?"
