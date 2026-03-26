# ComfyUI Skills for OpenClaw

9 base skills + workflow chaining examples for image generation, video, cropping, remixing, and more — powered by a remote ComfyUI server.

## Install

One command — installs all skills and prompts for your credentials:

```bash
npx github:ilker-tff/comfyui-text2img
```

Then restart OpenClaw:

```bash
openclaw gateway restart
```

## Uninstall

```bash
npx github:ilker-tff/comfyui-text2img uninstall
```

## Skills included

### Generation (text → image/video)
| Skill | Description |
|-------|-------------|
| `comfyui-generate-image` | Core text-to-image (512x512, any style) |
| `comfyui-portrait` | Cinematic portraits optimized for faces (512x768) |
| `comfyui-landscape-batch` | Multiple landscape variations (768x512, batch of 3) |
| `comfyui-lora` | Generation with LoRA adapters for custom styles |
| `comfyui-animated-webp` | Animated WebP loops (GIF-like) |
| `comfyui-video-clip` | Real video clips using Wan 2.1 (848x480 MP4) |

### Processing (image → image)
| Skill | Description |
|-------|-------------|
| `comfyui-crop` | Crop regions, change aspect ratios |
| `comfyui-img2img-remix` | Restyle/transform existing images |
| `comfyui-crop-then-refine` | Crop + AI enhance in one step |

### Reference
| Skill | Description |
|-------|-------------|
| `comfyui-workflow-examples` | Chaining recipes — teaches the LLM how to combine skills |

## Skill chaining

OpenClaw's LLM automatically chains skills based on your request:

- "Generate a portrait and make it look like watercolor" → `portrait` → `img2img-remix`
- "Create a landscape and crop to Instagram square" → `landscape-batch` → `crop`
- "Generate a robot, then make it steampunk, then weather it" → `generate-image` → `img2img-remix` → `img2img-remix`

The `comfyui-workflow-examples` skill teaches the LLM these patterns.

## Environment variables

Set automatically by the installer:

| Variable | Description |
|----------|-------------|
| `COMFY_URL` | ComfyUI server URL |
| `COMFY_AUTH_HEADER` | `Basic <base64(user:pass)>` |
| `COMFY_CKPT` | Checkpoint override (optional, default: `sd1.5/juggernaut_reborn.safetensors`) |

## License

MIT
