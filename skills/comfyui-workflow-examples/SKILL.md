---
name: comfyui-workflow-examples
description: "REFERENCE ONLY — not an executable skill. This document teaches you how to chain ComfyUI skills together for complex requests. Read this when the user's request requires multiple steps (e.g. "generate an image and then crop it", "create a portrait and make it look like watercolor", "upload my photo and turn it into a video"). Each example shows which skills to run in sequence and how to pass outputs between them. Also covers utility skills: checking server status, monitoring progress, managing assets."
homepage: https://github.com/ilker-tff/comfyclaw
metadata: {
    "openclaw": {
        "os": [
            "darwin",
            "linux"
        ],
        "requires": {
            "bins": [],
            "env": []
        },
        "tags": [
            "reference",
            "chaining",
            "workflow",
            "examples",
            "comfyui",
            "pipeline"
        ],
        "category": "reference",
        "files": []
    }
}
---

# ComfyUI Workflow Chaining Guide

This is a **reference document** — not an executable skill. Use this to understand how to chain multiple ComfyUI skills together for complex user requests.

## Skill inventory

### Generation skills (text → image/video)
| Skill | Output | Speed | Best for |
|-------|--------|-------|----------|
| `comfyui-generate-image` | PNG | ~30s | General-purpose text-to-image (SD1.5) |
| `comfyui-portrait` | PNG 512x768 | ~30s | Faces, headshots, character portraits |
| `comfyui-landscape-batch` | Multiple PNGs | ~90s | Scenery with 3 variations |
| `comfyui-lora` | PNG | ~35s | Custom LoRA model styles |
| `comfyui-animated-webp` | Animated WebP | ~60s | Stickers, short loops |
| `comfyui-video-clip` | MP4 | ~60s | Short text-to-video clips |
| `comfyui-preview-image` | PNG | ~10s | Quick draft (12 steps) |
| `comfyui-preview-character` | PNG 512x768 | ~10s | Quick character draft |

### Transform skills (image → image/video)
| Skill | Input | Output | Best for |
|-------|-------|--------|----------|
| `comfyui-crop` | Image | PNG | Extract region, change aspect ratio |
| `comfyui-img2img-remix` | Image | PNG | Restyle, remix existing images |
| `comfyui-crop-then-refine` | Image | PNG | Crop + enhance in one step |
| `comfyui-flux-multi-img2img` | 2-3 images | PNG | Blend multiple references (Flux) |
| `comfyui-img2video` | Image | MP4 | Animate a still image (LTX-Video, ~10min) |
| `comfyui-preview-img2img` | Image | PNG | Quick restyle draft (12 steps) |

### Utility skills
| Skill | Purpose |
|-------|---------|
| `comfyui-upload-image` | Upload user's image to ComfyUI server |
| `comfyui-upload-video` | Upload user's video to ComfyUI server |
| `comfyui-download-image` | Download generated image to local file |
| `comfyui-download-video` | Download generated video to local file |
| `comfyui-progress` | Check generation progress (percentage) |
| `comfyui-queue-status` | How many jobs running/pending |
| `comfyui-server-status` | Server health, GPU info, system stats |
| `comfyui-validate-models` | List/verify available models |
| `comfyui-list-assets` | List uploaded/generated files on server |
| `comfyui-delete-job` | Cancel a queued/running job |

## Skill compatibility map

### What can feed into what

```
Text prompt
  ├→ generate-image ──→ crop, img2img-remix, crop-then-refine, img2video
  ├→ portrait ────────→ crop, img2img-remix, crop-then-refine, img2video
  ├→ landscape-batch ─→ crop, img2img-remix, crop-then-refine
  ├→ lora ────────────→ crop, img2img-remix, crop-then-refine
  ├→ preview-image ───→ generate-image (upgrade to full quality)
  ├→ preview-character→ portrait (upgrade to full quality)
  ├→ animated-webp ───→ (terminal)
  └→ video-clip ──────→ (terminal)

User's image (upload first!)
  ├→ img2img-remix ───→ crop, img2img-remix, crop-then-refine
  ├→ crop ────────────→ img2img-remix, crop-then-refine
  ├→ crop-then-refine → crop, img2img-remix
  ├→ flux-multi-img2img → crop, img2img-remix, crop-then-refine
  ├→ img2video ───────→ (terminal, produces MP4)
  └→ preview-img2img ─→ img2img-remix (upgrade to full quality)
```

## Example pipelines

### 1. Simple text-to-image
**User says:** "Generate an image of a sunset over mountains"

**Steps:**
1. `comfyui-generate-image` — generate the image
2. Send the output file to user

---

### 2. Generate + Crop to format
**User says:** "Generate a product photo and crop it to Instagram square"

**Steps:**
1. `comfyui-generate-image` — generate at 768x512
2. `comfyui-crop` — crop to 512x512 from center (x=128, y=0)
3. Send cropped image to user

---

### 3. Portrait + Artistic restyle
**User says:** "Create a portrait of a medieval knight, make it look like an oil painting"

**Steps:**
1. `comfyui-portrait` — generate the portrait
2. `comfyui-img2img-remix` — restyle with "classical oil painting, thick brushstrokes" at denoise 0.5
3. Send restyled image to user

---

### 4. Quick iterate then commit (preview workflow)
**User says:** "I want to explore some character designs for a space explorer"

**Steps:**
1. `comfyui-preview-character` — quick 12-step draft: "space explorer in futuristic suit"
2. Show user, get feedback: "I like it but make the suit red"
3. `comfyui-preview-character` — another quick draft with adjusted prompt
4. User says "perfect, make it high quality"
5. `comfyui-portrait` — full-quality generation with the final prompt
6. Send to user

---

### 5. User photo → Animated video (full pipeline)
**User says:** "Here's my photo, turn it into a short video"

This is the most complex pipeline — matches Stelios's birkbeck_monitored pattern:

**Steps:**
1. `comfyui-server-status` — verify server is healthy
2. `comfyui-upload-image` — upload the user's photo to ComfyUI
3. `comfyui-img2video` — generate video from the uploaded image
   - This takes ~10-15 minutes!
   - Use `comfyui-progress` periodically to check and report to user
4. Send the video file to user

**Important:** Tell the user video generation takes 10-15 minutes. Check progress every ~30 seconds and report: "Your video is 35% done, hang tight!"

---

### 6. Multi-reference blend (Flux)
**User says:** "Combine these two product photos into one stylized image"

**Steps:**
1. `comfyui-upload-image` — upload first image
2. `comfyui-upload-image` — upload second image
3. `comfyui-flux-multi-img2img` — blend with a prompt describing desired output
4. Send result to user

---

### 7. Landscape batch + Pick + Restyle
**User says:** "Show me a few mountain landscapes, I'll pick one to make watercolor"

**Steps:**
1. `comfyui-landscape-batch` — generate 3 variations
2. Send all 3 to user, ask them to pick
3. Wait for selection: "I like the second one"
4. `comfyui-img2img-remix` — restyle with "watercolor painting, soft washes" at denoise 0.55
5. Send final image to user

---

### 8. Iterative refinement (remix chain)
**User says:** "Generate a robot, make it steampunk, then weather it"

**Steps:**
1. `comfyui-generate-image` — base robot
2. `comfyui-img2img-remix` — "steampunk brass gears copper pipes" at denoise 0.55
3. `comfyui-img2img-remix` — "weathered rust patina battle damage" at denoise 0.4 (lower!)
4. Send final image, keep all intermediates for user to review

---

### 9. Generate + Crop region + Refine detail
**User says:** "Generate a cityscape and zoom into the sky, make it more dramatic"

**Steps:**
1. `comfyui-generate-image` — full cityscape at 768x512
2. `comfyui-crop-then-refine` — crop sky region (y=0, h=256) + enhance with "dramatic stormy sky, lightning" at denoise 0.6
3. Send refined region to user

---

### 10. Server management
**User says:** "Is the server up?" / "What models are available?" / "Cancel my last job"

- `comfyui-server-status` — health check, GPU info
- `comfyui-queue-status` — running/pending job counts
- `comfyui-validate-models` — list available checkpoints, LoRAs, VAEs
- `comfyui-list-assets` — see uploaded/generated files
- `comfyui-delete-job` — cancel a stuck job

---

## Decision flowchart

When a user makes a request, follow this logic:

1. **Is this a server/admin question?**
   - "Is it up?" / "status" → `comfyui-server-status`
   - "What models?" → `comfyui-validate-models`
   - "Cancel" / "stop" → `comfyui-delete-job`

2. **Does the user provide an image/video?**
   - Yes → Upload it first with `comfyui-upload-image` or `comfyui-upload-video`
   - Then decide: crop? → `comfyui-crop` / restyle? → `comfyui-img2img-remix` / animate? → `comfyui-img2video`

3. **What output type?**
   - Video/MP4 → `comfyui-video-clip` (from text) or `comfyui-img2video` (from image)
   - Animation/sticker → `comfyui-animated-webp`
   - Portrait/face → `comfyui-portrait`
   - Landscape + options → `comfyui-landscape-batch`
   - Custom LoRA → `comfyui-lora`
   - Quick draft → `comfyui-preview-image` or `comfyui-preview-character`
   - General image → `comfyui-generate-image`

4. **Multi-step request?**
   - "Generate X then Y" → Chain skills in sequence
   - "Give me options then..." → Batch → user picks → chain next skill
   - "Upload my image and..." → Upload → transform

5. **Always confirm the plan before executing.**
   - Tell the user which skills you'll use and in what order
   - For long operations (video ~10min), warn about time
   - For chains, offer to show intermediate results

## Passing outputs between skills

When chaining skills, the output file from one becomes the input of the next:
- Skill A writes to `step1_output.png`
- Skill B reads `step1_output.png`, writes to `step2_output.png`
- Send final file to user (and intermediates if they want progress)

## Tips for better chains

1. **Use previews first** — for iterative work, start with preview skills (12 steps, ~10s) before committing to full generation (~30s+)
2. **Lower denoise for second passes** — first remix: 0.5, second remix: 0.3-0.4 to avoid over-processing
3. **Match dimensions** — crop output dimensions become the next skill's input dimensions
4. **Save all intermediates** — so user can go back to any step
5. **Report progress for long jobs** — video generation takes 10-15 min, poll and update user
6. **Check server before batch work** — use `comfyui-server-status` before submitting multiple jobs
7. **Let the user guide iteration** — show result, ask if they want to continue or adjust
