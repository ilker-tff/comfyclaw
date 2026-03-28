---
name: comfyui-download-video
description: "Download a generated video from the ComfyUI server to a local file. Use this skill after any video generation skill to save the result locally so it can be sent to the user. Takes the video metadata (filename, subfolder, type) from a generation skill's output and downloads the actual video file."
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
            "download",
            "video",
            "utility",
            "comfyui",
            "output"
        ],
        "category": "utility",
        "input_type": "text/json",
        "output_type": "video/mp4",
        "output_can_feed_into": [],
        "accepts_input_from": [
            "comfyui-video-clip",
            "comfyui-img2video",
            "comfyui-animated-webp"
        ],
        "priority": 85,
        "files": [
            "scripts/*"
        ]
    }
}
---

# ComfyUI Download Video

Download a generated video from the ComfyUI server to a local file path.

## When to use this skill

- After any video generation skill has completed and you need the video locally
- User wants to save, view, or share a generated video
- Retrieving video output from `comfyui-video-clip`, `comfyui-img2video`, or `comfyui-animated-webp`

## When NOT to use this skill

- You need to download an **image** → use `comfyui-download-image`
- You want to **upload** a video to the server → use `comfyui-upload-video`
- The generation skill already saved the file locally
- You want to list available outputs → use `comfyui-list-assets`

## Usage

```bash
python3 scripts/run.py --filename <name> --subfolder <subfolder> --type <type> <output-path>
```

### Options

| Option | Required | Description |
|--------|----------|-------------|
| `output_path` | Yes | Local path where the video will be saved |
| `--filename` | Yes | Server-side filename from generation output |
| `--subfolder` | No | Server subfolder (default: empty) |
| `--type` | No | Output type: "output" or "temp" (default: "output") |

### Examples

```bash
# Download a generated video
python3 scripts/run.py --filename "openclaw_video_00001_.mp4" --type output /tmp/result.mp4

# Download from temp directory
python3 scripts/run.py --filename "preview_00001_.webp" --type temp /tmp/preview.webp
```

### Output

JSON object with download details:
```json
{
  "status": "success",
  "local_path": "/tmp/result.mp4",
  "size_kb": 5678.9,
  "filename": "openclaw_video_00001_.mp4"
}
```

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/view?filename=<f>&subfolder=<s>&type=<t>` | Download generated video | Filename, subfolder, type as query params |
