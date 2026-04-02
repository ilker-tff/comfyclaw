---
name: comfyui-generate
description: >
  Generate images from text using ComfyUI. Supports SD 1.5 (standard, portrait, landscape, batch),
  LoRA adapters for custom styles, and animated WebP loops. Use --aspect for quick presets
  (square, portrait, landscape, widescreen) or set --width/--height directly. Use --workflow
  to select a specific curated workflow, or --lora for LoRA generation.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/run.py"]
metadata.clawdbot.tags: ["comfyui", "image-generation", "text2img", "portrait", "landscape", "lora", "animation"]
metadata.clawdbot.category: "generation"
metadata.clawdbot.output_type: "image/png"
metadata.clawdbot.output_can_feed_into: ["comfyui-edit"]
metadata.clawdbot.priority: 100
---

# ComfyUI Image Generation

Generate images from text descriptions using Stable Diffusion 1.5 via a remote ComfyUI server.

## When to use this skill

- User wants to **create a new image from a text description**
- User wants a **portrait**, **landscape**, or any image from scratch
- User wants to use a **LoRA adapter** for custom styles
- User wants an **animated WebP** (GIF-like loop)
- User wants **multiple variations** (batch generation)

## When NOT to use this skill

- User has an **existing image** to transform → use `comfyui-edit`
- User wants **video** (MP4) → use `comfyui-video`
- User wants to run a **custom workflow JSON** → use `comfyui-workflow`

## Usage

```bash
# Basic text-to-image (512x512)
python3 scripts/run.py "a red sports car in a desert" car.png

# Portrait (512x768)
python3 scripts/run.py "cinematic portrait of a warrior" warrior.png --aspect portrait

# Landscape (768x512)
python3 scripts/run.py "mountain sunset panorama" sunset.png --aspect landscape

# Landscape batch (3 variations)
python3 scripts/run.py "ocean waves crashing on rocks" waves.png --aspect landscape --batch 3

# Custom dimensions
python3 scripts/run.py "fantasy castle" castle.png --width 768 --height 768

# With LoRA adapter
python3 scripts/run.py "watercolor forest scene" forest.png --lora watercolor_style.safetensors --lora-strength 0.8

# Animated WebP (8 frames at 6fps)
python3 scripts/run.py "flickering candle flame" candle.webp --format webp --frames 8 --fps 6

# Use a specific curated workflow
python3 scripts/run.py "a cat" cat.png --workflow sd15_txt2img

# Fine-tune parameters
python3 scripts/run.py "detailed robot" robot.png --steps 40 --cfg 8.0 --seed 42
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `prompt` | (required) | Text description of the image |
| `output` | (required) | Output file path |
| `--aspect` | `square` | Preset: `square` (512x512), `portrait` (512x768), `landscape` (768x512), `widescreen` (768x432) |
| `--width` | 512 | Image width (overrides --aspect) |
| `--height` | 512 | Image height (overrides --aspect) |
| `--batch` | 1 | Number of variations (outputs: name_1.png, name_2.png, ...) |
| `--steps` | 35 | Sampling steps (more = better quality, slower) |
| `--cfg` | 7.0 | CFG scale (higher = closer to prompt) |
| `--seed` | random | Seed for reproducibility |
| `--negative` | default | Negative prompt |
| `--lora` | none | LoRA adapter filename |
| `--lora-strength` | 1.0 | LoRA strength (0.0-1.0) |
| `--format` | `png` | Output format: `png` or `webp` (webp enables animation) |
| `--frames` | 8 | Number of frames (for animated WebP) |
| `--fps` | 6 | Frames per second (for animated WebP) |
| `--workflow` | auto | Curated workflow ID (e.g. `sd15_txt2img`, `sd15_lora`) |

## Available workflows

| ID | Description |
|----|-------------|
| `sd15_txt2img` | Standard SD 1.5 text-to-image |
| `sd15_portrait` | Portrait-optimized (512x768) |
| `sd15_landscape` | Landscape batch (768x512, 3 images) |
| `sd15_lora` | SD 1.5 with LoRA adapter |
| `sd15_animated_webp` | Animated WebP loop |

## Chaining

Output images can be passed to `comfyui-edit` for:
- Cropping to a specific region or aspect ratio
- Restyling with img2img (e.g. "make it watercolor")
- Crop + AI enhance in one step

## Learning from experience

This skill logs every generation to the user's workspace. Over time, it learns preferred styles, sizes, and parameters.

**How it works:**
1. Every generation is logged automatically (prompt, params, output file, duration)
2. When the user gives feedback ("I love it", "too blurry", "not what I wanted"), record it:
   ```bash
   python3 ../comfyui-workflow/scripts/run.py --feedback liked --feedback-file output.png
   python3 ../comfyui-workflow/scripts/run.py --feedback disliked --feedback-file output.png --feedback-notes "too dark, faces are distorted"
   ```
3. The system builds a context.md from feedback patterns — loaded before each generation
4. Learned defaults are applied when the user doesn't specify explicit parameters

**As the assistant, you should:**
- After showing a result, ask if the user likes it
- If they say "great" / "love it" / "perfect" → record `liked` feedback
- If they say "too blurry" / "wrong style" / "try again" → record `disliked` with their complaint as notes
- Check learned context before choosing parameters — if the user prefers landscape, default to landscape
- Mention when you're using learned preferences: "Based on your history, using landscape aspect..."

## Confirm before running

Always tell the user what you're about to generate before executing:
- The prompt you'll use
- The dimensions/aspect ratio
- Any special options (LoRA, batch, animation)
