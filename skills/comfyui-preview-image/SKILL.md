---
name: comfyui-preview-image
description: "Quick preview image generation with only 12 sampling steps. Use when the user wants to quickly check if a prompt looks right before running a full-quality generation. Much faster than comfyui-generate-image but lower quality. Good for iterating."
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
            "preview",
            "fast",
            "draft",
            "quick"
        ],
        "category": "media-generation",
        "input_type": "text",
        "output_type": "image/png",
        "output_can_feed_into": [
            "comfyui-generate-image",
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

# ComfyUI Preview Image (Fast Draft)

Quick 12-step preview image generation for rapid prompt iteration.

## When to use this skill

- User says "quick preview", "draft", "rough sketch", "let me see how it looks first"
- User is iterating on prompts and wants fast feedback
- User wants to test a prompt before committing to full generation
- Speed matters more than quality

## When NOT to use this skill

- User wants final/high-quality output -> use `comfyui-generate-image`
- User wants a portrait -> use `comfyui-portrait`
- User wants to modify an existing image -> use `comfyui-img2img-remix`
- User wants video -> use `comfyui-video-clip` or `comfyui-img2video`

## Why this skill over generate-image?

- **12 steps** vs 35 steps -- roughly 3x faster
- **512x512** default -- smaller output, faster rendering
- **CFG 5.0** -- lighter guidance for speed
- Trade-off: lower quality, less detail, may have minor artifacts

## Usage

```bash
python3 scripts/run.py "<prompt>" <output-path> [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--width` | 512 | Image width in pixels |
| `--height` | 512 | Image height in pixels |
| `--steps` | 12 | Sampling steps (kept low for speed) |
| `--cfg` | 5.0 | Classifier-free guidance scale |
| `--seed` | random | Seed for reproducibility |
| `--negative` | `"watermark, text, blurry, low quality, deformed, extra fingers"` | Negative prompt |

### Examples

```bash
# Quick test of a prompt
python3 scripts/run.py "a dragon flying over a castle at sunset" preview.png

# Preview with specific seed to compare later
python3 scripts/run.py "cyberpunk cityscape, neon lights, rain" preview.png --seed 42

# Slightly larger preview
python3 scripts/run.py "product photo of headphones on white background" preview.png --width 768 --height 512
```

## Chaining with other skills

**Output can feed into:**
- `comfyui-generate-image` -- once prompt is finalized, generate full quality with same seed
- `comfyui-download-image` -- download the preview

## Confirm before running

> "I'll generate a quick preview of '[prompt]' at [width]x[height] (12 steps, ~10 seconds). Go ahead?"

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/prompt` | Submit workflow | Text prompt, dimensions, sampling params |
| `$COMFY_URL/history/<id>` | Poll job status | Prompt ID |
| `$COMFY_URL/view?filename=<f>` | Download image | Filename |
