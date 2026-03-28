---
name: comfyui-portrait
description: "Generate high-quality cinematic portrait images optimized for faces and people. Use this skill when the user specifically asks for a portrait, headshot, character portrait, face shot, profile picture, or avatar. This skill uses portrait-optimized dimensions (512x768 vertical) and higher step count for better facial detail. For non-portrait images, use comfyui-generate-image instead."
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
            "portrait",
            "face",
            "character",
            "headshot",
            "comfyui"
        ],
        "category": "media-generation",
        "input_type": "text",
        "output_type": "image/png",
        "output_can_feed_into": [
            "comfyui-crop",
            "comfyui-img2img-remix",
            "comfyui-crop-then-refine",
            "comfyui-img2video",
            "comfyui-download-image"
        ],
        "accepts_input_from": [],
        "priority": 95,
        "files": [
            "scripts/*"
        ]
    }
}
---

# ComfyUI Cinematic Portrait

Generate high-quality portrait images optimized for faces and characters.

## When to use this skill

- User asks for a "portrait", "headshot", "profile picture", "avatar", "character"
- User describes a person and wants them rendered as a portrait
- User wants face-focused composition with cinematic quality
- User mentions "close-up", "face shot", "bust shot"

## When NOT to use this skill

- User wants a full scene, landscape, or object → use `comfyui-generate-image`
- User wants to modify an existing portrait → use `comfyui-img2img-remix`
- User wants multiple images → use `comfyui-landscape-batch`

## Why this skill over generate-image?

This skill is tuned for faces:
- **Vertical 512x768 format** — natural portrait framing (3:4 aspect)
- **35 steps** — higher quality for facial detail
- **Optimized negative prompt** — blocks deformed hands, extra fingers, blurry faces
- Better at rendering eyes, skin texture, and hair

## Usage

```bash
python3 scripts/run.py "<portrait description>" <output-path> [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--width` | 512 | Portrait width |
| `--height` | 768 | Portrait height (vertical format) |
| `--steps` | 35 | Sampling steps |
| `--cfg` | 7.0 | Guidance scale |
| `--seed` | random | Seed for reproducibility |
| `--negative` | `"watermark, text, logo, blurry, deformed hands, extra fingers"` | Negative prompt |

### Examples

```bash
# Classic portrait
python3 scripts/run.py "cinematic portrait of a woman with red hair, golden hour lighting, shallow depth of field" portrait.png

# Fantasy character
python3 scripts/run.py "detailed portrait of an elf warrior, intricate armor, forest background, dramatic lighting" elf.png

# Professional headshot
python3 scripts/run.py "professional headshot, man in suit, studio lighting, neutral background" headshot.png
```

## Chaining

This skill's portrait output can be:
- **Cropped** with `comfyui-crop` to extract face region or resize for profile picture
- **Restyled** with `comfyui-img2img-remix` to apply artistic effects
- **Refined** with `comfyui-crop-then-refine` to enhance a specific region

## Confirm before running

> "I'll generate a cinematic portrait of [description] at 512x768 (vertical). This will take ~30 seconds. Go ahead?"
