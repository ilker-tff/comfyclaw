---
name: comfyui-upload-video
description: >
  Upload a local video file to the ComfyUI server's input storage.
  Use this skill when the user provides a video file that needs to be
  processed by ComfyUI skills. Transfers the video to the server and
  returns the server-side filename for downstream skills to reference.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
metadata.clawdbot.tags: ["upload", "video", "utility", "comfyui", "input"]
metadata.clawdbot.category: "utility"
metadata.clawdbot.input_type: "video/*"
metadata.clawdbot.output_type: "text/json"
metadata.clawdbot.output_can_feed_into: []
metadata.clawdbot.accepts_input_from: []
metadata.clawdbot.priority: 90
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
