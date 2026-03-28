---
name: comfyui-flux-multi-img2img
description: >
  Generate a single image by blending 2-3 reference images using the Flux model.
  Use when the user wants to combine elements from multiple images, or create a
  composite from several references. Requires images to be uploaded first via
  comfyui-upload-image.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
metadata.clawdbot.tags: ["flux", "img2img", "multi-reference", "blend", "composite"]
metadata.clawdbot.category: "media-generation"
metadata.clawdbot.input_type: "text/json"
metadata.clawdbot.output_type: "image/png"
metadata.clawdbot.output_can_feed_into: ["comfyui-crop", "comfyui-img2img-remix", "comfyui-crop-then-refine", "comfyui-download-image"]
metadata.clawdbot.accepts_input_from: ["comfyui-upload-image"]
metadata.clawdbot.priority: 80
---

# ComfyUI Flux Multi-Image Blend

Generate a single image by blending 2-3 reference images using the Flux model.

## When to use this skill

- User wants to combine elements from multiple reference images into one output
- User has 2-3 images and wants a composite or blend
- User wants to merge visual styles, subjects, or concepts from several images
- User says "combine these images", "blend these together", "mix these references"

## When NOT to use this skill

- User has only one image to transform -> use `comfyui-img2img-remix`
- User wants text-to-image with no reference images -> use `comfyui-generate-image`
- User wants to animate an image -> use `comfyui-img2video`
- User hasn't uploaded images yet -> use `comfyui-upload-image` first

## Usage

```bash
python3 scripts/run.py --image1 <filename> --image2 <filename> [--image3 <filename>] --prompt "<text>" <output-path> [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--image1` | (required) | First reference image filename (on ComfyUI server) |
| `--image2` | (required) | Second reference image filename (on ComfyUI server) |
| `--image3` | (optional) | Third reference image filename (on ComfyUI server) |
| `--prompt` | (required) | Text prompt describing the desired blend |
| `--width` | 1024 | Output width in pixels |
| `--height` | 1024 | Output height in pixels |
| `--steps` | 20 | Sampling steps |
| `--cfg` | 3.5 | Classifier-free guidance scale |
| `--seed` | random | Seed for reproducibility |

### Examples

```bash
# Blend two character references
python3 scripts/run.py --image1 "warrior.png" --image2 "mage.png" --prompt "a warrior-mage hybrid character, epic fantasy art" blend.png

# Combine three landscape references
python3 scripts/run.py --image1 "forest.png" --image2 "ocean.png" --image3 "mountains.png" --prompt "a fantasy landscape combining forest, ocean, and mountains" composite.png

# Merge style references
python3 scripts/run.py --image1 "photo.png" --image2 "painting.png" --prompt "photorealistic painting style blend" merged.png --steps 30
```

## Chaining with other skills

**Requires input from:**
- `comfyui-upload-image` -- images must be uploaded to ComfyUI server first

**Output can feed into:**
- `comfyui-crop` -- crop a region from the blended result
- `comfyui-img2img-remix` -- restyle the blended output
- `comfyui-crop-then-refine` -- crop and enhance a region
- `comfyui-download-image` -- download the result

## Confirm before running

> "I'll blend [N] reference images using Flux with the prompt '[prompt]' at [width]x[height]. This will take ~45 seconds. Go ahead?"

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/prompt` | Submit workflow | Image filenames, prompt, dimensions, sampling params |
| `$COMFY_URL/history/<id>` | Poll job status | Prompt ID |
| `$COMFY_URL/view?filename=<f>` | Download image | Filename |
