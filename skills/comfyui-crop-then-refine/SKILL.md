---
name: comfyui-crop-then-refine
description: >
  Crop a region from an image AND apply AI refinement to enhance it in one step.
  Use this skill when the user wants to extract a specific area from an image
  and improve or transform it simultaneously. Examples: "zoom into the face and
  make it sharper", "crop the background and make it more dramatic", "extract
  that corner and refine the details". This combines cropping + img2img in a
  single operation — more efficient than chaining comfyui-crop then comfyui-img2img-remix separately.
  If the user just wants to crop without any style change, use comfyui-crop instead.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
metadata.clawdbot.tags: ["crop", "refine", "enhance", "img2img", "comfyui"]
metadata.clawdbot.category: "image-processing"
metadata.clawdbot.input_type: "image/png"
metadata.clawdbot.output_type: "image/png"
metadata.clawdbot.output_can_feed_into: ["comfyui-crop", "comfyui-img2img-remix", "comfyui-img2video", "comfyui-download-image"]
metadata.clawdbot.accepts_input_from: ["comfyui-generate-image", "comfyui-portrait", "comfyui-landscape-batch", "comfyui-lora", "comfyui-img2img-remix"]
metadata.clawdbot.priority: 80
---

# ComfyUI Crop Then Refine

Crop a region from an image and refine it with AI enhancement in a single operation.

## When to use this skill

- User wants to **crop AND enhance** a region in one step
- User says "zoom into [area] and make it [better/sharper/more detailed]"
- User wants to **extract and restyle** a portion of an image
- User wants to focus on a detail and add quality/style improvements

## When NOT to use this skill

- User just wants to crop (no refinement) → use `comfyui-crop`
- User wants to restyle the **whole** image → use `comfyui-img2img-remix`
- User wants to generate from text → use `comfyui-generate-image`

## Usage

```bash
python3 scripts/run.py <input-image> <output-path> --prompt "<refinement description>" [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--prompt` | required | What to do with the cropped region |
| `--x` | 64 | Crop X coordinate |
| `--y` | 64 | Crop Y coordinate |
| `--width` | 512 | Crop width |
| `--height` | 512 | Crop height |
| `--steps` | 24 | Sampling steps |
| `--denoise` | 0.5 | Refinement strength (0.3=subtle, 0.7=strong) |
| `--cfg` | 6.8 | Guidance scale |
| `--seed` | random | Seed |
| `--negative` | `"watermark, text, blurry, low quality, distorted face"` | Negative prompt |

### Examples

```bash
# Crop face region and enhance
python3 scripts/run.py portrait.png face_refined.png --prompt "refined editorial portrait, sharp details, perfect skin" --x 100 --y 50 --width 300 --height 400

# Crop background and make dramatic
python3 scripts/run.py scene.png sky_dramatic.png --prompt "dramatic stormy sky, lightning, dark clouds" --x 0 --y 0 --width 512 --height 256 --denoise 0.6
```

## Chaining

This skill is typically used AFTER a generation skill:
1. `comfyui-generate-image` → `comfyui-crop-then-refine` (generate, then zoom+enhance a region)
2. `comfyui-portrait` → `comfyui-crop-then-refine` (portrait, then refine face details)

Its output can feed into:
1. `comfyui-img2img-remix` for further style changes
2. `comfyui-crop` for additional cropping

## Confirm before running

> "I'll crop the region at ({x}, {y}) size {width}x{height} and refine it with: [prompt]. Denoise {denoise} (higher = more change). Go ahead?"
