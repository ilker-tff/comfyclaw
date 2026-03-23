---
name: comfyui-text2img
description: Generate AI images from text prompts using a remote ComfyUI server with Stable Diffusion. Use when the user asks to create, generate, draw, or produce images, illustrations, artwork, photos, or any visual content from a text description.
homepage: https://github.com/openclaw/comfyui-text2img
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
---

# ComfyUI Text-to-Image Generation

Generate images from text prompts using a remote ComfyUI server running Stable Diffusion 1.5.

## Requirements

- `COMFY_URL` environment variable — ComfyUI server URL (e.g. `http://34.30.216.121`)
- `COMFY_AUTH_HEADER` environment variable — Basic auth header value (e.g. `Basic dXNlcjpwYXNz`)
- Python 3.10+ (uses only standard library — no pip install needed)

## Usage

Generate an image and save it to a local file:

```bash
python3 scripts/generate-image.py "<prompt>" <output-path> [options]
```

### Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--width` | 256-2048 | 512 | Image width in pixels |
| `--height` | 256-2048 | 512 | Image height in pixels |
| `--steps` | 1-150 | 35 | Sampling steps (more = better quality, slower) |
| `--negative` | text | `"watermark, text, blurry, low quality, deformed, extra fingers"` | Negative prompt |
| `--seed` | integer | random | Seed for reproducibility |
| `--cfg` | float | 7.0 | Classifier-free guidance scale |

### Examples

**Basic generation:**
```bash
python3 scripts/generate-image.py "A cute cat sitting on a bookshelf, oil painting style" cat.png
```

**Cinematic portrait:**
```bash
python3 scripts/generate-image.py "cinematic portrait of a woman in golden hour light, bokeh background" portrait.png --width 768 --height 512 --steps 40 --cfg 8
```

**Landscape:**
```bash
python3 scripts/generate-image.py "vast mountain landscape at sunset, dramatic clouds" landscape.png --width 768 --height 512
```

**Reproducible with seed:**
```bash
python3 scripts/generate-image.py "a steampunk clocktower in the rain" clock.png --seed 42
```

## Prompt Tips

1. **Be specific** — describe style, lighting, composition, mood
2. **Use art terms** — "cinematic lighting", "8K resolution", "shallow depth of field", "oil painting"
3. **Describe subjects** — character details, poses, expressions
4. **Set the scene** — environment, background, atmosphere
5. **Use negative prompt** — exclude "blurry, watermark, extra fingers, deformed"

## How It Works

The script builds a Stable Diffusion 1.5 workflow (CheckpointLoader → CLIPTextEncode → KSampler → VAEDecode → SaveImage) and submits it to the remote ComfyUI server via its REST API. It polls for completion and downloads the resulting image to the specified output path.

## External Endpoints

| URL | Purpose | Data Sent |
|-----|---------|-----------|
| `$COMFY_URL/prompt` | Submit generation workflow | Text prompt, image dimensions, sampling parameters |
| `$COMFY_URL/history/<id>` | Poll job status | Prompt ID only |
| `$COMFY_URL/view?filename=<f>` | Download generated image | Filename query parameter |

## Security & Privacy

- Your text prompt is sent to the ComfyUI server specified in `COMFY_URL`
- Authentication credentials are read from `COMFY_AUTH_HEADER` environment variable
- Generated images are downloaded and saved locally to the path you specify
- No data is sent to any third-party service — only your own ComfyUI server

**By using this skill, your prompts are sent to the ComfyUI server at `COMFY_URL`. Only install if you trust that server.**

## Troubleshooting

### "Connection refused" or timeout
Check that `COMFY_URL` is set and the server is reachable.

### "401 Unauthorized"
Generate your auth header: `echo -n "user:pass" | base64`, then set `COMFY_AUTH_HEADER="Basic <result>"`.

### Slow generation
The server may be busy. The script waits up to 120 seconds for results.
