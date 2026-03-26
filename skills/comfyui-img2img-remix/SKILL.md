---
name: comfyui-img2img-remix
description: >
  Transform an existing image into a new style or variation using img2img.
  Use this skill when the user has an existing image and wants to change its style,
  repaint it, remix it, or apply artistic transformations. Examples: "make this look
  like a watercolor", "turn this photo into anime style", "repaint this in cyberpunk
  style", "make this more cinematic". This skill preserves the composition and
  structure of the original while changing its visual style.
  Requires an existing image as input — does NOT generate from scratch.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
metadata.clawdbot.tags: ["image-to-image", "style-transfer", "remix", "transformation", "comfyui"]
metadata.clawdbot.category: "image-processing"
metadata.clawdbot.input_type: "image/png"
metadata.clawdbot.output_type: "image/png"
metadata.clawdbot.output_can_feed_into: ["comfyui-crop", "comfyui-img2img-remix", "comfyui-crop-then-refine"]
metadata.clawdbot.accepts_input_from: ["comfyui-generate-image", "comfyui-portrait", "comfyui-landscape-batch", "comfyui-lora", "comfyui-crop"]
metadata.clawdbot.priority: 85
---

# ComfyUI Image-to-Image Remix

Transform an existing image with a new style or artistic direction while preserving its composition.

## When to use this skill

- User wants to change the **style** of an existing image ("make it watercolor", "cyberpunk version")
- User says "remix", "repaint", "restyle", "transform", "reimagine" an image
- User wants to apply artistic effects to a photo or generated image
- User wants **variations** of an image with a different mood or aesthetic
- Use AFTER a generation skill when user says "generate X then make it look like Y"

## When NOT to use this skill

- User wants to generate from text only (no source image) → use `comfyui-generate-image`
- User wants to crop only → use `comfyui-crop`
- User wants to crop a region AND refine it → use `comfyui-crop-then-refine`

## Denoise guide

The `--denoise` parameter controls how much the image changes:
- **0.3**: Subtle changes — color grading, minor style shifts (keeps most of original)
- **0.5**: Moderate — noticeable style change while keeping composition (default: 0.55)
- **0.7**: Strong — significant transformation, some original structure remains
- **0.9**: Almost new — heavy repaint, only basic shapes preserved

## Usage

```bash
python3 scripts/run.py <input-image> <output-path> --prompt "<style description>" [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--prompt` | required | Style/transformation description |
| `--negative` | `"watermark, text, blurry, low quality, artifacts"` | Negative prompt |
| `--steps` | 28 | Sampling steps |
| `--denoise` | 0.55 | How much to change (0.0=nothing, 1.0=complete repaint) |
| `--cfg` | 7.0 | Guidance scale |
| `--seed` | random | Seed for reproducibility |

### Examples

```bash
# Turn a photo into watercolor
python3 scripts/run.py photo.png watercolor.png --prompt "beautiful watercolor painting, soft edges, flowing colors"

# Cyberpunk restyle
python3 scripts/run.py portrait.png cyber.png --prompt "cyberpunk neon portrait, glowing edges, dark atmosphere" --denoise 0.6

# Subtle color grading
python3 scripts/run.py scene.png warm.png --prompt "warm golden hour lighting, cinematic color grading" --denoise 0.3
```

## Chaining

Common chains:
1. `comfyui-generate-image` → `comfyui-img2img-remix` (generate, then restyle)
2. `comfyui-crop` → `comfyui-img2img-remix` (crop region, then restyle it)
3. `comfyui-img2img-remix` → `comfyui-img2img-remix` (iterative refinement — apply style, then refine further)

## Confirm before running

> "I'll transform the image with style: [prompt], denoise strength: [denoise]. Higher denoise = more change. Go ahead?"

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/upload/image` | Upload source image | Image file |
| `$COMFY_URL/prompt` | Submit img2img workflow | Style prompt, denoise params |
| `$COMFY_URL/history/<id>` | Poll job status | Prompt ID |
| `$COMFY_URL/view?filename=<f>` | Download result | Filename |
