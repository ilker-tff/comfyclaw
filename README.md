# ComfyClaw — ComfyUI Skills for OpenClaw

4 unified skills for image generation, editing, video, and custom workflows — powered by a remote ComfyUI server. Learns from user feedback to get better over time.

## Install

```bash
npx github:ilker-tff/comfyclaw
```

Then restart OpenClaw:

```bash
openclaw gateway restart
```

## Uninstall

```bash
npx github:ilker-tff/comfyclaw uninstall
```

## Skills

| Skill | Description |
|-------|-------------|
| `comfyui-generate` | Text-to-image: standard, portrait, landscape, batch, LoRA, animated WebP |
| `comfyui-edit` | Image editing: crop, img2img restyle, crop+refine |
| `comfyui-video` | Text-to-video using Wan 2.1 (MP4) |
| `comfyui-workflow` | Run any ComfyUI workflow JSON, manage feedback & preferences |

## Quick examples

```
"Generate an image of a sunset over mountains"
"Create a portrait of a fantasy warrior"
"Generate a landscape and crop it to Instagram square"
"Make a short video clip of ocean waves"
"List available ComfyUI workflows"
"Restyle my photo as a watercolor painting"
```

## Architecture

### Curated workflow catalog

ComfyClaw includes a catalog of curated workflow JSON files for common tasks. Each skill can use these via the `--workflow` flag, or fall back to built-in workflow builders.

Available workflows:

| ID | Description |
|----|-------------|
| `sd15_txt2img` | Standard SD 1.5 text-to-image |
| `sd15_lora` | SD 1.5 with LoRA adapter |
| `sd15_animated_webp` | Animated WebP loop |
| `sd15_img2img` | Image-to-image restyling |
| `sd15_crop` | Image cropping |
| `sd15_crop_refine` | Crop + AI enhance |
| `wan21_t2v` | Wan 2.1 text-to-video |

### Skill chaining

OpenClaw's LLM automatically chains skills based on your request:

- "Generate a portrait and make it look like watercolor" → `comfyui-generate` → `comfyui-edit`
- "Create a landscape and crop to Instagram square" → `comfyui-generate` → `comfyui-edit`
- "Generate a robot, then make it steampunk, then weather it" → `comfyui-generate` → `comfyui-edit` → `comfyui-edit`

### Custom workflows

The `comfyui-workflow` skill is an escape hatch for power users. You can:
- Pass a curated workflow ID: `--workflow sd15_txt2img`
- Pass a JSON file path: `--workflow /path/to/custom.json`
- Pass inline JSON: `--json '{...}'`

## Iterative learning

ComfyClaw learns from each user's feedback to improve over time — like reinforcement learning for image generation.

### How it works

1. **Auto-logging**: Every generation is logged (prompt, parameters, seed, timing)
2. **Feedback collection**: After each result, OpenClaw asks if the user likes it and records the response
3. **Pattern analysis**: The system finds patterns in liked vs disliked generations (preferred sizes, styles, CFG ranges)
4. **Context generation**: A summary (`context.md`) is built from the analysis and loaded before each generation
5. **Adaptive defaults**: When the user doesn't specify parameters, learned defaults are applied

### Per-user isolation

Learning data lives in each user's OpenClaw workspace (`~/.openclaw/workspace/comfyui/`):

```
~/.openclaw/workspace/comfyui/
  history.jsonl      # Every generation with feedback
  preferences.json   # Explicit user preferences
  context.md         # Auto-generated LLM context from patterns
```

Skills are shared (installed at the package level), but learning data is per-user. Multi-user setups use `OPENCLAW_PROFILE` for workspace isolation.

### Managing feedback & preferences

Via the `comfyui-workflow` skill:

```bash
# Record feedback
python3 scripts/run.py --feedback liked --feedback-file output.png
python3 scripts/run.py --feedback disliked --feedback-file output.png --feedback-notes "too blurry"

# View what the system has learned
python3 scripts/run.py --show-context

# View generation history
python3 scripts/run.py --show-history

# Set explicit preferences
python3 scripts/run.py --set-preference default_width 768
python3 scripts/run.py --set-preference default_steps 40
```

## Environment variables

Set automatically by the installer:

| Variable | Description |
|----------|-------------|
| `COMFY_URL` | ComfyUI server URL |
| `COMFY_AUTH_HEADER` | `Bearer <api-key>` |
| `COMFY_CKPT` | Checkpoint override (optional, default: `sd1.5/juggernaut_reborn.safetensors`) |

## Upgrading from v2

The installer automatically removes legacy skills (9 individual skills) and installs the new unified set (4 skills). Just run the install command again:

```bash
npx --yes github:ilker-tff/comfyclaw
```

## License

MIT
