---
name: comfyui-workflow
description: >
  Run any ComfyUI workflow JSON — either a curated workflow from the catalog or a
  custom-built workflow. This is the power-user/escape-hatch skill for when the other
  skills don't cover the use case. You can pass a workflow file path, a catalog ID,
  or inline JSON directly. Parameter overrides are applied automatically.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/run.py"]
metadata.clawdbot.tags: ["comfyui", "workflow", "custom", "advanced", "json"]
metadata.clawdbot.category: "advanced"
metadata.clawdbot.output_type: "mixed"
metadata.clawdbot.output_can_feed_into: ["comfyui-edit"]
metadata.clawdbot.priority: 50
---

# ComfyUI Workflow Runner

Run any ComfyUI workflow — curated from the catalog, loaded from a JSON file, or passed as inline JSON.

## When to use this skill

- The other skills (`comfyui-generate`, `comfyui-edit`, `comfyui-video`) don't cover the use case
- User provides a specific **ComfyUI workflow JSON** file
- User needs a **custom node combination** not available in built-in workflows
- User asks to **list available workflows** from the catalog
- User wants to run a workflow with **full control** over every parameter

## When NOT to use this skill

- Simple text-to-image → use `comfyui-generate`
- Simple crop/remix/refine → use `comfyui-edit`
- Simple text-to-video → use `comfyui-video`

## Usage

```bash
# Run a curated workflow by ID
python3 scripts/run.py --workflow sd15_txt2img --output result.png --prompt "a sunset" --width 768 --height 512

# Run a workflow from a JSON file
python3 scripts/run.py --workflow /path/to/custom_workflow.json --output result.png --prompt "a cat"

# Pass inline JSON (the workflow dict as a string)
python3 scripts/run.py --json '{"1": {"class_type": "CheckpointLoaderSimple", ...}}' --output result.png

# List all available curated workflows
python3 scripts/run.py --list

# Search workflows
python3 scripts/run.py --search "portrait"

# Upload an input image for workflows that need one
python3 scripts/run.py --workflow sd15_img2img --input photo.png --output styled.png --prompt "oil painting"
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--workflow` | none | Curated workflow ID or path to JSON file |
| `--json` | none | Inline JSON workflow string (alternative to --workflow) |
| `--output` | (required) | Output file path |
| `--input` | none | Input image to upload (for img2img workflows) |
| `--prompt` | none | Text prompt override |
| `--negative` | none | Negative prompt override |
| `--width` | none | Width override |
| `--height` | none | Height override |
| `--steps` | none | Steps override |
| `--cfg` | none | CFG scale override |
| `--seed` | random | Seed override |
| `--denoise` | none | Denoise override |
| `--list` | false | List all available workflows and exit |
| `--search` | none | Search workflows by keyword |

## Building custom workflows

You can construct ComfyUI API-format JSON and pass it via `--json`. The format is:

```json
{
  "node_id": {
    "class_type": "NodeClassName",
    "inputs": {
      "param": "value",
      "connection": ["other_node_id", output_index]
    }
  }
}
```

Common node types:
- `CheckpointLoaderSimple` — load a model checkpoint
- `CLIPTextEncode` — encode text prompt
- `EmptyLatentImage` — create blank latent
- `KSampler` — the main sampling node
- `VAEDecode` — decode latent to image
- `SaveImage` — save output
- `LoadImage` — load uploaded image
- `VAEEncode` — encode image to latent (for img2img)

## Available curated workflows

| ID | Description |
|----|-------------|
| `sd15_txt2img` | Standard text-to-image |
| `sd15_portrait` | Portrait preset (512x768) |
| `sd15_landscape` | Landscape batch (768x512, 3 images) |
| `sd15_lora` | Generation with LoRA adapter |
| `sd15_animated_webp` | Animated WebP loop |
| `sd15_img2img` | Image-to-image restyling |
| `sd15_crop` | Image cropping |
| `sd15_crop_refine` | Crop + AI enhance |
| `wan21_t2v` | Wan 2.1 text-to-video |

## Learning system commands

This skill also serves as the hub for the learning/feedback system. All ComfyUI skills log their generations automatically, but feedback and preferences are managed here.

### Record feedback

After the user reacts to a generation, record their feedback:

```bash
# User liked a result
python3 scripts/run.py --feedback liked --feedback-file /path/to/output.png

# User disliked a result (with notes about why)
python3 scripts/run.py --feedback disliked --feedback-file /path/to/output.png --feedback-notes "faces are distorted, too dark"

# Neutral (acceptable but not great)
python3 scripts/run.py --feedback neutral --feedback-file /path/to/output.png
```

### View history and context

```bash
# Show recent generation history with feedback
python3 scripts/run.py --show-history

# Show the learned user context (what the system has learned)
python3 scripts/run.py --show-context
```

### Set preferences

```bash
# Set default image width
python3 scripts/run.py --set-preference default_width 768

# Set default steps
python3 scripts/run.py --set-preference default_steps 40

# Set default negative prompt
python3 scripts/run.py --set-preference default_negative "watermark, text, blurry, ugly"
```

### How learning works

1. **Automatic logging**: Every generation across all 4 skills is logged with prompt, params, output file, seed, and timing
2. **Feedback collection**: When the user reacts (positive or negative), you record it with `--feedback`
3. **Pattern analysis**: The system analyzes liked vs disliked generations to find patterns (preferred sizes, styles, CFG ranges, denoise levels)
4. **Context generation**: A `context.md` summary is built from the analysis — loaded by all skills before execution
5. **Adaptive defaults**: Skills use learned defaults when the user doesn't specify parameters explicitly

### As the assistant, you MUST

- **Always ask for feedback** after showing a generation result ("Do you like this? Any adjustments?")
- **Record feedback immediately** when the user reacts — don't wait for them to ask
- **Use specific notes** for dislikes — "too blurry" is much more useful than just "disliked"
- **Check context** before generating — if the user prefers landscapes, default to landscape
- **Mention learned preferences** so the user knows the system is adapting: "Based on your feedback history, I'll use 768x512 with CFG 8.0"
- **Never override explicit requests** — learned defaults only apply when the user hasn't specified
