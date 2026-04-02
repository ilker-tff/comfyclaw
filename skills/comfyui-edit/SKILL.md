---
name: comfyui-edit
description: >
  Transform existing images using ComfyUI. Supports cropping, img2img restyling, and
  crop+refine in one step. Use --mode to select the operation: crop, remix, or refine.
  Can process outputs from comfyui-generate or user-uploaded images.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/run.py"]
metadata.clawdbot.tags: ["comfyui", "image-editing", "crop", "img2img", "remix", "restyle"]
metadata.clawdbot.category: "editing"
metadata.clawdbot.output_type: "image/png"
metadata.clawdbot.output_can_feed_into: ["comfyui-edit"]
metadata.clawdbot.priority: 90
---

# ComfyUI Image Editing

Transform existing images: crop regions, restyle with img2img, or crop + AI enhance in one step.

## When to use this skill

- User has an **existing image** and wants to **crop** a region or change aspect ratio
- User wants to **restyle** an image (e.g. "make it look like watercolor")
- User wants to **crop and enhance** a region with AI refinement
- Chaining after `comfyui-generate` (e.g. "generate a landscape, then crop to Instagram square")

## When NOT to use this skill

- User wants to **generate an image from scratch** (no input image) → use `comfyui-generate`
- User wants **video** → use `comfyui-video`
- User wants to run a **custom workflow JSON** → use `comfyui-workflow`

## Usage

```bash
# Crop to a specific region
python3 scripts/run.py photo.png cropped.png --mode crop --x 100 --y 50 --width 512 --height 512

# Restyle with img2img
python3 scripts/run.py photo.png watercolor.png --mode remix --prompt "watercolor painting, soft edges, flowing colors"

# Stronger transformation (higher denoise)
python3 scripts/run.py photo.png abstract.png --mode remix --prompt "abstract cubist painting" --denoise 0.7

# Subtle enhancement (lower denoise)
python3 scripts/run.py photo.png enhanced.png --mode remix --prompt "professional photography, sharp details" --denoise 0.3

# Crop + AI refine in one step
python3 scripts/run.py photo.png face_enhanced.png --mode refine --x 50 --y 20 --width 256 --height 256 --prompt "detailed face, sharp features"

# Use a curated workflow
python3 scripts/run.py photo.png styled.png --mode remix --workflow sd15_img2img --prompt "oil painting"
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `input` | (required) | Input image file path |
| `output` | (required) | Output file path |
| `--mode` | `remix` | Operation: `crop`, `remix`, or `refine` |
| `--prompt` | (required for remix/refine) | Style/transformation prompt |
| `--negative` | default | Negative prompt |
| `--x` | 0 | Crop X coordinate |
| `--y` | 0 | Crop Y coordinate |
| `--width` | 256 | Crop width (for crop/refine modes) |
| `--height` | 256 | Crop height (for crop/refine modes) |
| `--denoise` | 0.55 | Denoise strength for remix/refine (0.0=keep original, 1.0=full redraw) |
| `--steps` | 28 | Sampling steps |
| `--cfg` | 7.0 | CFG scale |
| `--seed` | random | Seed for reproducibility |
| `--workflow` | auto | Curated workflow ID or JSON path |

## Denoise guide

| Denoise | Effect |
|---------|--------|
| 0.2-0.3 | Subtle enhancement, keeps most of the original |
| 0.4-0.5 | Moderate transformation, recognizable source |
| 0.5-0.6 | Strong restyle, source composition preserved |
| 0.7-0.8 | Heavy transformation, loose resemblance to source |

## Chaining tips

- After `comfyui-generate`: crop to change aspect ratio, remix to add style
- Multiple remix passes: use denoise 0.5 for first pass, 0.3-0.4 for second (avoids over-processing)
- Crop then remix: crop first, then remix the cropped region for detail work

## Learning from experience

This skill logs every edit to the user's workspace. Over time, it learns preferred denoise levels, styles, and editing patterns.

**As the assistant, you should:**
- After showing a result, ask if the user likes it
- Record feedback via `comfyui-workflow`: `--feedback liked/disliked --feedback-file output.png`
- If the user says "too much change" → lower denoise next time
- If the user says "not enough change" → increase denoise next time
- Check learned context before choosing denoise/steps — adapt to the user's taste

## Confirm before running

Always tell the user what you're about to do before executing:
- The mode (crop/remix/refine)
- For crop: the region coordinates
- For remix/refine: the style prompt and denoise value
