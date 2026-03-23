# ComfyUI Text-to-Image Skill for OpenClaw

Generate AI images from text prompts using a remote ComfyUI server with Stable Diffusion 1.5.

## Install

One command — installs the skill and prompts for your credentials:

```bash
npx comfyui-text2img
```

Then restart OpenClaw:

```bash
openclaw gateway restart
```

## Use

Just ask your OpenClaw bot:

- "Use stable diffusion to generate a sunset over mountains"
- "Create a cinematic portrait with ComfyUI"
- "Generate a photorealistic landscape using SD"

## Options

The generation script supports these flags:

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
