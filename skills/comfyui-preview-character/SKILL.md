---
name: comfyui-preview-character
description: >
  Quick character concept preview using 12-step generation. Use when the user
  wants to rapidly iterate on character designs -- explore different looks,
  outfits, poses before committing to full quality.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
metadata.clawdbot.tags: ["preview", "character", "concept", "fast", "design"]
metadata.clawdbot.category: "media-generation"
metadata.clawdbot.input_type: "text"
metadata.clawdbot.output_type: "image/png"
metadata.clawdbot.output_can_feed_into: ["comfyui-generate-image", "comfyui-portrait", "comfyui-download-image"]
metadata.clawdbot.accepts_input_from: []
metadata.clawdbot.priority: 70
---

# ComfyUI Preview Character (Fast Concept)

Quick 12-step character concept preview optimized for character design iteration.

## When to use this skill

- User wants to quickly explore character designs before committing to full quality
- User says "quick character sketch", "rough concept", "let me see some character ideas"
- User is iterating on character outfits, poses, or features
- User wants fast feedback on a character description

## When NOT to use this skill

- User wants final high-quality character art -> use `comfyui-generate-image` or `comfyui-portrait`
- User wants a portrait/headshot -> use `comfyui-portrait`
- User wants to modify an existing character image -> use `comfyui-img2img-remix`
- User wants a scene or landscape -> use `comfyui-preview-image`

## Why this skill?

- **12 steps** -- roughly 3x faster than full generation
- **512x768 vertical format** -- optimized for character framing
- **Character-optimized negative prompt** -- blocks "multiple people, crowd" for clean single-character output
- Perfect for rapid iteration on character concepts

## Usage

```bash
python3 scripts/run.py "<character description>" <output-path> [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--width` | 512 | Image width |
| `--height` | 768 | Image height (vertical for characters) |
| `--steps` | 12 | Sampling steps (kept low for speed) |
| `--cfg` | 5.0 | Classifier-free guidance scale |
| `--seed` | random | Seed for reproducibility |
| `--negative` | `"watermark, text, blurry, low quality, deformed, extra fingers, multiple people, crowd"` | Negative prompt |

### Examples

```bash
# Quick character concept
python3 scripts/run.py "female elf ranger, leather armor, bow, forest background" elf_concept.png

# Iterate on outfit variations
python3 scripts/run.py "cyberpunk hacker, neon jacket, goggles, dark alley" cyber_v1.png --seed 42
python3 scripts/run.py "cyberpunk hacker, trench coat, visor, dark alley" cyber_v2.png --seed 42

# Fantasy warrior concept
python3 scripts/run.py "dwarf warrior, heavy plate armor, battle axe, mountain backdrop" dwarf.png
```

## Chaining with other skills

**Output can feed into:**
- `comfyui-generate-image` -- once design is finalized, generate at full quality
- `comfyui-portrait` -- generate a high-quality portrait version
- `comfyui-download-image` -- download the preview

## Confirm before running

> "I'll generate a quick character preview of '[description]' at 512x768 (12 steps, ~10 seconds). Go ahead?"

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/prompt` | Submit workflow | Text prompt, dimensions, sampling params |
| `$COMFY_URL/history/<id>` | Poll job status | Prompt ID |
| `$COMFY_URL/view?filename=<f>` | Download image | Filename |
