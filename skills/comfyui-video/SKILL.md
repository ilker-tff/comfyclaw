---
name: comfyui-video
description: >
  Generate video clips from text using Wan 2.1 text-to-video model via ComfyUI.
  Produces MP4 files at 848x480 by default. Videos take 60-120 seconds to generate.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/run.py"]
metadata.clawdbot.tags: ["comfyui", "video", "text2video", "mp4", "wan"]
metadata.clawdbot.category: "generation"
metadata.clawdbot.output_type: "video/mp4"
metadata.clawdbot.output_can_feed_into: []
metadata.clawdbot.priority: 80
---

# ComfyUI Video Generation

Generate video clips from text descriptions using the Wan 2.1 text-to-video model.

## When to use this skill

- User wants a **video clip** or **MP4** from a text description
- User mentions **motion**, **animation as video**, or **moving scene**

## When NOT to use this skill

- User wants a **still image** → use `comfyui-generate`
- User wants an **animated GIF/WebP** (looping sticker) → use `comfyui-generate` with `--format webp`
- User wants to **edit an existing image** → use `comfyui-edit`

## Usage

```bash
# Basic video (848x480, 25 frames, ~1.5s at 16fps)
python3 scripts/run.py "ocean waves crashing on a rocky shore at sunset" waves.mp4

# More frames for longer clip
python3 scripts/run.py "a cat playing with a ball of yarn" cat.mp4 --frames 49

# Custom resolution
python3 scripts/run.py "drone shot over a forest" forest.mp4 --width 640 --height 480

# Higher quality (more steps)
python3 scripts/run.py "fireworks display over a city" fireworks.mp4 --steps 20

# Use curated workflow
python3 scripts/run.py "time lapse of clouds" clouds.mp4 --workflow wan21_t2v
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `prompt` | (required) | Video description |
| `output` | (required) | Output file path (.mp4) |
| `--width` | 848 | Video width |
| `--height` | 480 | Video height |
| `--frames` | 25 | Number of frames |
| `--fps` | 16 | Frames per second |
| `--steps` | 10 | Sampling steps |
| `--cfg` | 8.0 | CFG scale |
| `--seed` | random | Seed for reproducibility |
| `--negative` | default | Negative prompt |
| `--workflow` | auto | Curated workflow ID or JSON path |

## Important notes

- Video generation takes **60-120 seconds** — warn the user before starting
- Output is **terminal** — videos cannot be chained into other skills
- The Wan 2.1 model uses separate UNET, CLIP, and VAE loaders (not CheckpointLoaderSimple)

## Learning from experience

This skill logs every video generation. Over time it learns preferred resolutions, frame counts, and styles.

**As the assistant, you should:**
- After showing a result, ask if the user likes it
- Record feedback via `comfyui-workflow`: `--feedback liked/disliked --feedback-file output.mp4`
- Check learned context before choosing parameters

## Confirm before running

Tell the user:
- The prompt you'll use
- The expected duration (frames / fps)
- That it will take 60-120 seconds
