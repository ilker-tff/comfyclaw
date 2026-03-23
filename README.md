# ComfyUI Text-to-Image Skill for OpenClaw

Generate AI images from text prompts using a remote ComfyUI server with Stable Diffusion 1.5.

## Install

```bash
openclaw skills install github:openclaw/comfyui-text2img
```

Or with clawhub CLI:

```bash
clawhub install comfyui-text2img
```

## Configure

Add your ComfyUI server credentials in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "comfyui-text2img": {
        "enabled": true,
        "env": {
          "COMFY_URL": "http://34.30.216.121",
          "COMFY_AUTH_HEADER": "Basic <BASE64_USER_PASS>"
        }
      }
    }
  }
}
```

Generate the Base64 auth value:

```bash
echo -n "username:password" | base64
```

Then restart: `openclaw gateway restart` or `/new` in chat.

## Use

Just ask your OpenClaw bot:

- "Generate an image of a sunset over mountains"
- "Create a cyberpunk portrait"
- "Draw a watercolor cat"

## Manual Test

```bash
export COMFY_URL="http://34.30.216.121"
export COMFY_AUTH_HEADER="Basic dXNlcjpwYXNz"

python3 scripts/generate-image.py "A robot in a neon city" robot.png
python3 scripts/generate-image.py "Mountain landscape" landscape.png --width 768 --height 512 --steps 40
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--width` | 512 | Image width |
| `--height` | 512 | Image height |
| `--steps` | 35 | Sampling steps |
| `--cfg` | 7.0 | CFG guidance scale |
| `--seed` | random | Reproducibility seed |
| `--negative` | `"watermark, text, blurry..."` | Negative prompt |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `COMFY_URL` | Yes | ComfyUI server URL |
| `COMFY_AUTH_HEADER` | Yes | `Basic <base64(user:pass)>` |
| `COMFY_CKPT` | No | Checkpoint (default: `sd1.5/juggernaut_reborn.safetensors`) |

## License

MIT
