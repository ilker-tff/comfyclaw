---
name: comfyui-img2video
description: "Generate a short video clip from a still image using the LTX-Video model. Use when the user wants to animate a photo or generated image. The input image must be uploaded to ComfyUI first via comfyui-upload-image. Produces MP4 video at 24fps."
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
            "video",
            "img2video",
            "ltxv",
            "animation",
            "motion"
        ],
        "category": "media-generation",
        "input_type": "text/json",
        "output_type": "video/mp4",
        "output_can_feed_into": [
            "comfyui-download-video"
        ],
        "accepts_input_from": [
            "comfyui-upload-image",
            "comfyui-generate-image",
            "comfyui-portrait",
            "comfyui-flux-multi-img2img"
        ],
        "priority": 80,
        "files": [
            "scripts/*"
        ]
    }
}
---

# ComfyUI Image-to-Video (LTX-Video)

Generate a short video clip (up to ~6 seconds) from a still image using the LTX-Video model.

## When to use this skill

- User wants to animate a still image or photo
- User says "make this image move", "animate this", "turn this into a video"
- User wants a short video clip from a generated or uploaded image
- User wants motion added to a static scene

## When NOT to use this skill

- User wants text-to-video with no input image -> use `comfyui-video-clip`
- User wants to generate a still image -> use `comfyui-generate-image`
- User wants an animated GIF/WebP -> use `comfyui-animated-webp`
- User wants to edit/transform an image without video -> use `comfyui-img2img-remix`

## Usage

```bash
python3 scripts/run.py --image <server-filename> --prompt "<text>" <output-path> [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--image` | (required) | Image filename on the ComfyUI server |
| `--prompt` | (required) | Text description of desired motion/animation |
| `--width` | 768 | Video width in pixels |
| `--height` | 512 | Video height in pixels |
| `--frames` | 97 | Number of frames (~4 seconds at 24fps) |
| `--fps` | 24 | Frames per second |
| `--steps` | 30 | Sampling steps |
| `--negative` | `"low quality, blurry, distorted"` | Negative prompt |
| `--seed` | random | Seed for reproducibility |

### Examples

```bash
# Animate a landscape photo
python3 scripts/run.py --image "landscape.png" --prompt "gentle wind blowing through trees, clouds moving slowly" landscape_video.mp4

# Animate a portrait
python3 scripts/run.py --image "portrait.png" --prompt "person slowly turning head, gentle smile, hair flowing" portrait_anim.mp4

# Short clip with custom frames
python3 scripts/run.py --image "scene.png" --prompt "camera slowly zooming in, cinematic" scene.mp4 --frames 49 --steps 40
```

## Chaining with other skills

**Requires input from:**
- `comfyui-upload-image` -- upload a local image to ComfyUI server first
- `comfyui-generate-image` -- generate an image, then animate it
- `comfyui-portrait` -- generate a portrait, then animate it
- `comfyui-flux-multi-img2img` -- blend images, then animate the result

**Output can feed into:**
- `comfyui-download-video` -- download the generated video

## Confirm before running

> "I'll animate the image '[filename]' into a ~[frames/fps]-second video at [width]x[height]. Video generation takes 10-15 minutes. Go ahead?"

## Important notes

- Video generation is **much slower** than image generation (10-15 minutes typical)
- The script sets COMFY_TIMEOUT to 600 seconds to accommodate this
- Keep prompts focused on **motion and animation** rather than content changes
- Best results with simple, natural motions (wind, water, camera movement)

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/prompt` | Submit workflow | Image filename, prompt, dimensions, frame count, sampling params |
| `$COMFY_URL/history/<id>` | Poll job status | Prompt ID |
| `$COMFY_URL/view?filename=<f>` | Download video | Filename |
