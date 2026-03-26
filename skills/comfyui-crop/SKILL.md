---
name: comfyui-crop
description: >
  Crop a rectangular region from an existing image. Use this skill when the user
  wants to cut out, extract, or trim a portion of an image. Also use when the user
  wants to resize an image to specific dimensions by cropping (e.g. "make it
  square", "crop to Instagram format", "crop to widescreen 16:9").
  This skill requires an existing image as input — it does NOT generate new images.
homepage: https://github.com/ilker-tff/comfyui-text2img
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
metadata.clawdbot.tags: ["image-processing", "crop", "resize", "utility", "comfyui"]
metadata.clawdbot.category: "image-processing"
metadata.clawdbot.input_type: "image/png"
metadata.clawdbot.output_type: "image/png"
metadata.clawdbot.output_can_feed_into: ["comfyui-img2img-remix", "comfyui-crop-then-refine"]
metadata.clawdbot.accepts_input_from: ["comfyui-generate-image", "comfyui-portrait", "comfyui-landscape-batch", "comfyui-lora", "comfyui-img2img-remix"]
metadata.clawdbot.priority: 90
---

# ComfyUI Image Crop

Crop a rectangular region from an image using the ComfyUI server.

## When to use this skill

- User says "crop", "trim", "cut out", "extract region" from an image
- User wants to change aspect ratio: "make it square", "make it 16:9", "Instagram format"
- User wants to focus on a specific part of a generated image
- Use AFTER a generation skill when user says "generate X and then crop to Y"

## When NOT to use this skill

- User wants to generate a new image from text → use `comfyui-generate-image`
- User wants to crop AND apply style changes → use `comfyui-crop-then-refine`
- User wants to restyle the whole image → use `comfyui-img2img-remix`

## Common aspect ratio crops

When the user asks for a format, calculate crop dimensions from the source image:
- **Square (1:1)**: Instagram post — e.g. 512x512
- **Widescreen (16:9)**: YouTube thumbnail — e.g. 512x288 from center
- **Portrait (9:16)**: Instagram story/TikTok — e.g. 288x512 from center
- **Landscape (3:2)**: Photography standard — e.g. 512x341
- **Wide banner (21:9)**: Ultrawide — e.g. 512x219

## Usage

```bash
python3 scripts/run.py <input-image> <output-path> [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--x` | 0 | X coordinate of crop start (left edge) |
| `--y` | 0 | Y coordinate of crop start (top edge) |
| `--width` | 256 | Width of crop region |
| `--height` | 256 | Height of crop region |

### Examples

```bash
# Crop center 512x512 from a larger image
python3 scripts/run.py input.png cropped.png --x 128 --y 0 --width 512 --height 512

# Crop to widescreen
python3 scripts/run.py portrait.png wide.png --x 0 --y 100 --width 512 --height 288
```

## Chaining

This skill is commonly used AFTER a generation skill:
1. `comfyui-generate-image` → `comfyui-crop` (generate then extract region)
2. `comfyui-landscape-batch` → `comfyui-crop` (pick best landscape, crop to format)

And BEFORE a refinement skill:
1. `comfyui-crop` → `comfyui-img2img-remix` (crop then restyle the cropped region)

## Confirm before running

> "I'll crop the image at position ({x}, {y}) with size {width}x{height}. Go ahead?"

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/upload/image` | Upload source image | Image file |
| `$COMFY_URL/prompt` | Submit crop workflow | Crop coordinates |
| `$COMFY_URL/history/<id>` | Poll job status | Prompt ID |
| `$COMFY_URL/view?filename=<f>` | Download cropped image | Filename |
