---
name: comfyui-list-assets
description: >
  List files available in ComfyUI's input and output directories. Use this
  skill to see what images and videos have been uploaded or generated on the
  server. Helpful for finding previously uploaded inputs or browsing generated
  outputs without downloading them.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
metadata.clawdbot.tags: ["assets", "files", "listing", "utility", "comfyui"]
metadata.clawdbot.category: "utility"
metadata.clawdbot.input_type: none
metadata.clawdbot.output_type: "text/json"
metadata.clawdbot.output_can_feed_into: []
metadata.clawdbot.accepts_input_from: []
metadata.clawdbot.priority: 50
---

# ComfyUI List Assets

List files available in ComfyUI's input and output directories.

## When to use this skill

- User asks "what images have been generated?" or "what files are on the server?"
- Checking if a previously uploaded image is still available
- Browsing generated outputs to find a specific file
- Verifying that an upload was successful

## When NOT to use this skill

- You want to **download** a specific file → use `comfyui-download-image` or `comfyui-download-video`
- You want to **upload** a file → use `comfyui-upload-image` or `comfyui-upload-video`
- You want to check **available models** → use `comfyui-validate-models`
- You want **server health** info → use `comfyui-server-status`

## Usage

```bash
python3 scripts/run.py
```

### Arguments

No arguments required.

### Examples

```bash
# List all assets
python3 scripts/run.py
```

### Output

JSON object with input and output file listings:
```json
{
  "status": "success",
  "input_files": ["uploaded_photo.png", "reference.jpg"],
  "output_files": ["openclaw_generate_00001_.png", "openclaw_video_00001_.mp4"]
}
```

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/view?type=input&filename=` | List input files | None (GET with type param) |
| `$COMFY_URL/api/view-raw/output` | List output files | None (GET request) |
