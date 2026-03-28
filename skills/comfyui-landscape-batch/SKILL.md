---
name: comfyui-landscape-batch
description: >
  Generate multiple landscape image variations in a single batch.
  Use this skill when the user wants landscape, scenery, environment, or
  panoramic images — especially when they want multiple options to choose from.
  Produces 3 variations by default at 768x512 (widescreen 3:2 aspect ratio).
  Use this instead of comfyui-generate-image when the user says "landscape",
  "scenery", "environment", "panorama", or wants "a few options" / "variations".
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
metadata.clawdbot.tags: ["landscape", "batch", "scenery", "environment", "panoramic", "comfyui"]
metadata.clawdbot.category: "media-generation"
metadata.clawdbot.input_type: "text"
metadata.clawdbot.output_type: "image/png"
metadata.clawdbot.output_can_feed_into: ["comfyui-crop", "comfyui-img2img-remix", "comfyui-crop-then-refine", "comfyui-download-image"]
metadata.clawdbot.accepts_input_from: []
metadata.clawdbot.priority: 80
---

# ComfyUI Landscape Batch

Generate multiple landscape image variations in one go.

## When to use this skill

- User asks for "landscape", "scenery", "environment", "vista", "panorama"
- User wants **multiple options** or **variations** of an image
- User describes natural scenes: mountains, forests, oceans, cities from above
- User says "give me a few options" or "generate some variations"

## When NOT to use this skill

- User wants a single specific image → use `comfyui-generate-image`
- User wants a portrait → use `comfyui-portrait`
- User wants to modify an existing image → use `comfyui-img2img-remix`

## Usage

```bash
python3 scripts/run.py "<landscape description>" <output-prefix> [options]
```

Output files are named `<output-prefix>_1.png`, `<output-prefix>_2.png`, etc.

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--width` | 768 | Image width (widescreen) |
| `--height` | 512 | Image height |
| `--batch` | 3 | Number of variations to generate |
| `--steps` | 30 | Sampling steps |
| `--cfg` | 7.0 | Guidance scale |
| `--seed` | random | Seed for reproducibility |
| `--negative` | `"watermark, text, low quality, blurry, oversaturated"` | Negative prompt |

### Examples

```bash
# Mountain landscape (3 variations)
python3 scripts/run.py "epic mountain valley at golden hour, dramatic clouds, river flowing through" mountains

# City skyline (5 variations)
python3 scripts/run.py "futuristic city skyline at night, neon lights, rain" city --batch 5

# Ocean panorama
python3 scripts/run.py "vast ocean at sunset, waves crashing on rocky shore" ocean --width 1024 --height 512
```

## Chaining

After generating a batch, the user can:
1. Pick their favorite and **crop** it with `comfyui-crop`
2. Pick one and **restyle** it with `comfyui-img2img-remix`
3. Pick one and **refine a region** with `comfyui-crop-then-refine`

## Confirm before running

> "I'll generate {batch} landscape variations of [description] at {width}x{height}. This may take ~{batch * 30} seconds. Go ahead?"
