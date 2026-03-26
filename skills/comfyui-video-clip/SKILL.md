---
name: comfyui-video-clip
description: >
  Generate short video clips from text descriptions using the Wan 2.1 video model.
  Use this skill when the user asks for a video, video clip, MP4, motion content,
  or cinematic footage. Produces real video with temporal coherence (smooth motion)
  unlike comfyui-animated-webp which just stitches independent frames.
  Output is MP4 (h264) at 848x480 (16:9 widescreen), ~1.5 seconds at 16fps.
  This is significantly slower than image generation (~60-120 seconds).
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
metadata.clawdbot.tags: ["video", "mp4", "text-to-video", "clip", "motion", "cinematic", "comfyui"]
metadata.clawdbot.category: "media-generation"
metadata.clawdbot.input_type: "text"
metadata.clawdbot.output_type: "video/mp4"
metadata.clawdbot.output_can_feed_into: []
metadata.clawdbot.accepts_input_from: []
metadata.clawdbot.priority: 70
---

# ComfyUI Video Clip Generation

Generate short video clips from text using the Wan 2.1 text-to-video model.

## When to use this skill

- User asks for a "video", "video clip", "MP4", "footage", "motion"
- User wants moving content with temporal coherence (smooth motion between frames)
- User describes a scene they want as video, not a still image
- User says "make a video of...", "create a clip of..."

## When NOT to use this skill

- User wants a **still image** → use `comfyui-generate-image`
- User wants an **animated GIF/sticker** (lightweight loop) → use `comfyui-animated-webp`
- User wants to modify an existing image → use `comfyui-img2img-remix`

## Video vs animated WebP

| Feature | Video clip (this skill) | Animated WebP |
|---------|------------------------|---------------|
| Output format | MP4 (h264) | WebP animation |
| Motion | True temporal coherence | Independent frames |
| Model | Wan 2.1 (video-specific) | SD 1.5 (image model) |
| Resolution | 848x480 (16:9) | 512x512 (flexible) |
| Duration | ~1.5 sec (25 frames @ 16fps) | Variable |
| Speed | Slow (60-120 sec) | Moderate |

## Usage

```bash
python3 scripts/run.py "<video description>" <output-path> [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--width` | 848 | Video width |
| `--height` | 480 | Video height |
| `--frames` | 25 | Number of frames |
| `--fps` | 16 | Frames per second |
| `--steps` | 10 | Sampling steps |
| `--cfg` | 8.0 | Guidance scale |
| `--seed` | random | Seed |
| `--negative` | `"Overexposure, static, blurred details, low quality, artifacts"` | Negative prompt |

### Examples

```bash
# Product video
python3 scripts/run.py "cinematic product video of a perfume bottle rotating slowly, studio lighting" perfume.mp4

# Nature clip
python3 scripts/run.py "ocean waves rolling onto sandy beach, golden sunset, aerial view" beach.mp4

# Action scene
python3 scripts/run.py "a sports car driving through a neon-lit city at night, rain on windshield" car.mp4
```

## Limitations

- Output is short (~1.5 seconds at 25 frames / 16fps)
- Fixed 16:9 widescreen (848x480)
- Uses different model (Wan 2.1) — must be installed on the ComfyUI server
- Significantly slower than image generation
- Cannot chain to image-based skills (video output)
- Quality depends on prompt clarity — be specific about motion

## Confirm before running

> "I'll generate a ~1.5 second video clip of [description] at 848x480. This will take 60-120 seconds. Go ahead?"
