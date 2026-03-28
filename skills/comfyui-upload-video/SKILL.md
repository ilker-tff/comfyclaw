---
name: comfyui-upload-video
description: "Upload a local video file to the ComfyUI server's input storage. Use this skill when the user provides a video file that needs to be processed by ComfyUI skills. Transfers the video to the server and returns the server-side filename for downstream skills to reference."
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
            "upload",
            "video",
            "utility",
            "comfyui",
            "input"
        ],
        "category": "utility",
        "input_type": "video/*",
        "output_type": "text/json",
        "output_can_feed_into": [],
        "accepts_input_from": [],
        "priority": 90,
        "files": [
            "scripts/*"
        ]
    }
}
---

# ComfyUI Upload Video

Upload a local video file to the ComfyUI server so it can be used by processing skills.

## When to use this skill

- User provides a local video file that needs to be sent to ComfyUI for processing
- User says "use this video", "process this clip", "work with this video"
- Any time a downstream skill needs a server-side video filename

## When NOT to use this skill

- User wants to upload an **image** → use `comfyui-upload-image`
- User wants to **download** a generated video → use `comfyui-download-video`
- User wants to **generate** a video from scratch or from an image → use `comfyui-img2video` or `comfyui-video-clip`
- The video is already on the ComfyUI server

## Usage

```bash
python3 scripts/run.py <local-video-path>
```

### Options

| Argument | Required | Description |
|----------|----------|-------------|
| `video_path` | Yes | Local path to the video file to upload |

### Examples

```bash
# Upload an MP4 video
python3 scripts/run.py /tmp/my_clip.mp4

# Upload a video from Downloads
python3 scripts/run.py ~/Downloads/source_video.mov
```

### Output

JSON object with the server-side filename:
```json
{
  "status": "success",
  "server_filename": "my_clip.mp4",
  "original_path": "/tmp/my_clip.mp4"
}
```

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/upload/image` | Upload video file | Multipart form with video binary |
