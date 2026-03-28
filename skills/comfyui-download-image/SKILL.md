---
name: comfyui-download-image
description: >
  Download a generated image from the ComfyUI server to a local file.
  Use this skill after any image generation skill to save the result locally
  so it can be sent to the user or processed further. Takes the image metadata
  (filename, subfolder, type) from a generation skill's output and downloads
  the actual image file. This is the bridge between server-side generation
  and local file access.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
metadata.clawdbot.tags: ["download", "image", "utility", "comfyui", "output"]
metadata.clawdbot.category: "utility"
metadata.clawdbot.input_type: "text/json"
metadata.clawdbot.output_type: "image/png"
metadata.clawdbot.output_can_feed_into: []
metadata.clawdbot.accepts_input_from: ["comfyui-generate-image", "comfyui-portrait", "comfyui-landscape-batch", "comfyui-lora", "comfyui-crop", "comfyui-img2img-remix", "comfyui-crop-then-refine", "comfyui-flux-multi-img2img", "comfyui-preview-image", "comfyui-preview-img2img", "comfyui-preview-character"]
metadata.clawdbot.priority: 85
---

# ComfyUI Download Image

Download a generated image from the ComfyUI server to a local file path.

## When to use this skill

- After any image generation skill has completed and you need the image locally
- User wants to save, view, or share a generated image
- You need to retrieve a previously generated image from the server
- Bridging server-side output to local filesystem for delivery to the user

## When NOT to use this skill

- You need to download a **video** → use `comfyui-download-video`
- You want to **upload** an image to the server → use `comfyui-upload-image`
- The generation skill already saved the file locally (some skills do this automatically)
- You want to list available outputs → use `comfyui-list-assets`

## Usage

```bash
python3 scripts/run.py --filename <name> --subfolder <subfolder> --type <type> <output-path>
```

### Options

| Option | Required | Description |
|--------|----------|-------------|
| `output_path` | Yes | Local path where the image will be saved |
| `--filename` | Yes | Server-side filename from generation output |
| `--subfolder` | No | Server subfolder (default: empty) |
| `--type` | No | Output type: "output" or "temp" (default: "output") |

### Examples

```bash
# Download a generated image
python3 scripts/run.py --filename "openclaw_generate_00001_.png" --subfolder "" --type output /tmp/result.png

# Download from temp directory
python3 scripts/run.py --filename "preview_00001_.png" --type temp /tmp/preview.png
```

### Output

JSON object with download details:
```json
{
  "status": "success",
  "local_path": "/tmp/result.png",
  "size_kb": 1234.5,
  "filename": "openclaw_generate_00001_.png"
}
```

## Chaining with other skills

This skill typically comes LAST in a chain:
1. `comfyui-generate-image` (or other generation skill) produces image metadata
2. `comfyui-download-image` downloads the actual file

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/view?filename=<f>&subfolder=<s>&type=<t>` | Download generated image | Filename, subfolder, type as query params |
