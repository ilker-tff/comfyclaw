---
name: comfyui-upload-image
description: "Upload a local image file to the ComfyUI server's input storage. Use this skill when the user provides or sends an image that needs to be processed by other ComfyUI skills (img2img, video generation, multi-image compositing, cropping, etc). This skill MUST run BEFORE any skill that needs a user-provided image. It transfers the file to the server and returns the server-side filename that downstream skills reference."
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
            "image",
            "utility",
            "comfyui",
            "input"
        ],
        "category": "utility",
        "input_type": "image/*",
        "output_type": "text/json",
        "output_can_feed_into": [
            "comfyui-img2img-remix",
            "comfyui-flux-multi-img2img",
            "comfyui-img2video",
            "comfyui-crop",
            "comfyui-crop-then-refine"
        ],
        "accepts_input_from": [],
        "priority": 90,
        "files": [
            "scripts/*"
        ]
    }
}
---

# ComfyUI Upload Image

Upload a local image file to the ComfyUI server so it can be used by generation skills.

## When to use this skill

- User provides a local image file that needs to be sent to ComfyUI for processing
- Before running any img2img, crop, video-from-image, or multi-image skill
- User says "use this image", "transform this photo", "start from this picture"
- Any time a downstream skill needs a `server_filename` from an uploaded image

## When NOT to use this skill

- User wants to **generate** an image from text only (no input image needed)
- User wants to **download** a result from the server → use `comfyui-download-image`
- The image is already on the ComfyUI server (already uploaded previously)
- User wants to upload a **video** → use `comfyui-upload-video`

## Usage

```bash
python3 scripts/run.py <local-image-path>
```

### Options

| Argument | Required | Description |
|----------|----------|-------------|
| `image_path` | Yes | Local path to the image file to upload |

### Examples

```bash
# Upload a photo for img2img processing
python3 scripts/run.py /tmp/my_photo.png

# Upload a JPEG
python3 scripts/run.py ~/Downloads/reference.jpg
```

### Output

JSON object with the server-side filename:
```json
{
  "status": "success",
  "server_filename": "my_photo.png",
  "original_path": "/tmp/my_photo.png"
}
```

## Chaining with other skills

After uploading, pass the `server_filename` to:
- `comfyui-img2img-remix` — restyle or transform the image
- `comfyui-flux-multi-img2img` — multi-image compositing
- `comfyui-img2video` — animate the image into a video
- `comfyui-crop` — crop a region of the image
- `comfyui-crop-then-refine` — crop and enhance a region

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/upload/image` | Upload image file | Multipart form with image binary |
