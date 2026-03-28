---
name: comfyui-preview-img2img
description: "Quick preview of an image-to-image transformation with only 12 steps. Use to test how a restyle will look before committing to full generation."
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
            "img2img",
            "draft"
        ],
        "category": "media-generation",
        "input_type": "image/*",
        "output_type": "image/png",
        "output_can_feed_into": [
            "comfyui-img2img-remix",
            "comfyui-download-image"
        ],
        "accepts_input_from": [
            "comfyui-upload-image"
        ],
        "priority": 70,
        "files": [
            "scripts/*"
        ]
    }
}
---

# ComfyUI Preview Img2Img (Fast Draft)

Quick 12-step preview of an image-to-image transformation for rapid iteration.

## When to use this skill

- User wants a quick preview of how an image restyle will look
- User says "quick test", "draft restyle", "preview the transformation"
- User is experimenting with different style prompts on the same image
- Speed matters more than quality for the img2img result

## When NOT to use this skill

- User wants final high-quality img2img output -> use `comfyui-img2img-remix`
- User wants text-to-image (no input image) -> use `comfyui-preview-image` or `comfyui-generate-image`
- User wants video from an image -> use `comfyui-img2video`

## Why this skill over img2img-remix?

- **12 steps** vs 28 steps -- roughly 2x faster
- **CFG 5.0** -- lighter guidance for speed
- Trade-off: lower quality, less refined transformation

## Usage

```bash
python3 scripts/run.py <input-image> <output-path> --prompt "<style>" [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--prompt` | (required) | Style/transformation prompt |
| `--denoise` | 0.5 | Denoise strength (0.0 = no change, 1.0 = full regeneration) |
| `--steps` | 12 | Sampling steps (kept low for speed) |
| `--cfg` | 5.0 | Classifier-free guidance scale |
| `--seed` | random | Seed for reproducibility |
| `--negative` | `"watermark, text, blurry, low quality, artifacts"` | Negative prompt |

### Examples

```bash
# Quick restyle preview
python3 scripts/run.py photo.png preview.png --prompt "oil painting style, impressionist"

# Test different denoise levels
python3 scripts/run.py photo.png preview.png --prompt "anime style" --denoise 0.6

# Preview with fixed seed for comparison
python3 scripts/run.py photo.png preview.png --prompt "cyberpunk neon style" --seed 42
```

## Chaining with other skills

**Requires input from:**
- `comfyui-upload-image` -- upload a local image to ComfyUI server first

**Output can feed into:**
- `comfyui-img2img-remix` -- once style is confirmed, run full-quality version
- `comfyui-download-image` -- download the preview

## Confirm before running

> "I'll generate a quick preview of the img2img restyle on '[input]' with prompt '[prompt]' (12 steps, ~10 seconds). Go ahead?"

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/upload/image` | Upload input image | Image binary |
| `$COMFY_URL/prompt` | Submit workflow | Image name, prompt, sampling params |
| `$COMFY_URL/history/<id>` | Poll job status | Prompt ID |
| `$COMFY_URL/view?filename=<f>` | Download image | Filename |
