---
name: comfyui-animated-webp
description: "Generate animated WebP images (short looping animations) from text descriptions. Use this skill when the user wants an animation, animated image, GIF-like output, animated sticker, or looping image. Produces a batch of frames compiled into a WebP animation. This is NOT video — it's a lightweight looping animation (like a GIF but better quality). For actual video (MP4), use comfyui-video-clip instead."
homepage: https://github.com/ilker-tff/comfyclaw
metadata: {
    "openclaw": {
        "os": [
            "darwin",
            "linux"
        ],
        "requires": {
            "bins": [
                "python3"
            ],
            "env": [
                "COMFY_URL",
                "COMFY_AUTH_HEADER"
            ]
        },
        "tags": [
            "animation",
            "animated",
            "webp",
            "gif",
            "sticker",
            "loop",
            "comfyui"
        ],
        "category": "media-generation",
        "input_type": "text",
        "output_type": "image/webp",
        "output_can_feed_into": [
            "comfyui-download-video"
        ],
        "accepts_input_from": [],
        "priority": 70,
        "files": [
            "scripts/*"
        ]
    }
}
---

# ComfyUI Animated WebP

Generate animated looping images (WebP format) from text descriptions.

## When to use this skill

- User asks for an "animation", "animated image", "GIF", "sticker", "looping image"
- User wants movement in a still image concept
- User wants a lightweight animation (not full video)
- User says "animate this", "make it move", "create a GIF of..."

## When NOT to use this skill

- User wants a **still image** → use `comfyui-generate-image`
- User wants **actual video (MP4)** → use `comfyui-video-clip`
- User wants to modify an existing image → use `comfyui-img2img-remix`

## How it works

This skill generates a **batch of SD1.5 images** with the same prompt but different latent noise, then compiles them into an animated WebP. The result is a looping animation — each frame is a variation of the prompt. It's like a flipbook, not true motion video.

## Usage

```bash
python3 scripts/run.py "<animation description>" <output-path> [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--width` | 512 | Frame width |
| `--height` | 512 | Frame height |
| `--frames` | 8 | Number of frames (more = longer animation, slower) |
| `--fps` | 6 | Playback speed (frames per second) |
| `--steps` | 20 | Sampling steps per frame |
| `--cfg` | 7.0 | Guidance scale |
| `--seed` | random | Seed |
| `--negative` | `"watermark, text, blurry, low quality, extra limbs"` | Negative prompt |

### Examples

```bash
# Simple animation
python3 scripts/run.py "a glowing crystal orb, magical particles, fantasy style" orb.webp

# Longer animation
python3 scripts/run.py "ocean waves crashing on shore, sunset" waves.webp --frames 16 --fps 8

# Square sticker
python3 scripts/run.py "cute cartoon cat waving" sticker.webp --width 256 --height 256 --frames 6
```

## Limitations

- Output is animated WebP (not MP4 video)
- Each frame is independently generated (no temporal coherence)
- More frames = significantly longer generation time
- Cannot chain output to other image skills (animation format)

## Confirm before running

> "I'll generate a {frames}-frame animated WebP of [description] at {fps}fps. This may take ~{frames * 5} seconds. Go ahead?"
