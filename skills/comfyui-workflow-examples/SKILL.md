---
name: comfyui-workflow-examples
description: >
  REFERENCE ONLY — not an executable skill. This document teaches you how to chain
  ComfyUI skills together for complex requests. Read this when the user's request
  requires multiple steps (e.g. "generate an image and then crop it", "create a
  portrait and make it look like watercolor"). Each example shows which skills to
  run in sequence and how to pass outputs between them.
homepage: https://github.com/ilker-tff/comfyui-text2img
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: []
metadata.clawdbot.requires.env: []
metadata.clawdbot.files: []
metadata.clawdbot.tags: ["reference", "chaining", "workflow", "examples", "comfyui"]
metadata.clawdbot.category: "reference"
---

# ComfyUI Workflow Chaining Guide

This is a **reference document** — not an executable skill. Use this to understand how to chain multiple ComfyUI skills together for complex user requests.

## Skill compatibility map

### Text-input skills (generate from scratch)
| Skill | Output type | Can feed into |
|-------|------------|---------------|
| `comfyui-generate-image` | PNG image | crop, img2img-remix, crop-then-refine |
| `comfyui-portrait` | PNG image (512x768) | crop, img2img-remix, crop-then-refine |
| `comfyui-landscape-batch` | Multiple PNG images | crop, img2img-remix, crop-then-refine |
| `comfyui-lora` | PNG image | crop, img2img-remix, crop-then-refine |
| `comfyui-animated-webp` | Animated WebP | (terminal — no chaining) |
| `comfyui-video-clip` | MP4 video | (terminal — no chaining) |

### Image-input skills (transform existing images)
| Skill | Requires | Output type | Can feed into |
|-------|----------|------------|---------------|
| `comfyui-crop` | Image file | PNG image | img2img-remix, crop-then-refine |
| `comfyui-img2img-remix` | Image file | PNG image | crop, img2img-remix, crop-then-refine |
| `comfyui-crop-then-refine` | Image file | PNG image | crop, img2img-remix |

## Example chains

### 1. Generate + Crop to format
**User says:** "Generate a product photo of a coffee mug and crop it to Instagram square format"

**Steps:**
1. Run `comfyui-generate-image`:
   ```bash
   python3 scripts/run.py "cinematic product photo of a ceramic coffee mug, studio lighting, white background" mug_full.png --width 768 --height 512
   ```
2. Run `comfyui-crop` on the output:
   ```bash
   python3 scripts/run.py mug_full.png mug_instagram.png --x 128 --y 0 --width 512 --height 512
   ```
3. Send `mug_instagram.png` to user

---

### 2. Portrait + Artistic restyle
**User says:** "Create a portrait of a medieval knight and then make it look like an oil painting"

**Steps:**
1. Run `comfyui-portrait`:
   ```bash
   python3 scripts/run.py "detailed portrait of a medieval knight in full plate armor, dramatic lighting, castle background" knight.png
   ```
2. Run `comfyui-img2img-remix` on the output:
   ```bash
   python3 scripts/run.py knight.png knight_oil.png --prompt "classical oil painting, thick brushstrokes, rich colors, museum quality, Renaissance style" --denoise 0.5
   ```
3. Send `knight_oil.png` to user

---

### 3. Generate + Crop region + Refine detail
**User says:** "Generate a cityscape and then zoom into the sky area and make it more dramatic"

**Steps:**
1. Run `comfyui-generate-image`:
   ```bash
   python3 scripts/run.py "futuristic cityscape at dusk, skyscrapers, flying vehicles" city.png --width 768 --height 512
   ```
2. Run `comfyui-crop-then-refine` on the sky region:
   ```bash
   python3 scripts/run.py city.png sky_dramatic.png --prompt "dramatic stormy sky, lightning bolts, swirling clouds, epic atmosphere" --x 0 --y 0 --width 768 --height 256 --denoise 0.6
   ```
3. Send `sky_dramatic.png` to user

---

### 4. Landscape batch + Pick best + Restyle
**User says:** "Give me a few mountain landscape options, then I'll pick one to make it look like a watercolor"

**Steps:**
1. Run `comfyui-landscape-batch`:
   ```bash
   python3 scripts/run.py "majestic mountain range at sunrise, misty valleys, pine forests" mountains --batch 3
   ```
2. Send all 3 images (`mountains_1.png`, `mountains_2.png`, `mountains_3.png`) to user
3. Wait for user to pick (e.g. "I like the second one")
4. Run `comfyui-img2img-remix` on their choice:
   ```bash
   python3 scripts/run.py mountains_2.png mountains_watercolor.png --prompt "beautiful watercolor painting, soft edges, flowing washes, paper texture" --denoise 0.55
   ```
5. Send `mountains_watercolor.png` to user

---

### 5. Generate with LoRA + Crop to banner
**User says:** "Generate a fantasy scene using the watercolor LoRA and crop it to a Twitter banner"

**Steps:**
1. Run `comfyui-lora`:
   ```bash
   python3 scripts/run.py "enchanted forest with glowing mushrooms and fairy lights" forest.png --lora "watercolor_style.safetensors" --strength 0.8 --width 768 --height 512
   ```
2. Run `comfyui-crop` to Twitter banner (1500x500 → scale down from 768, crop to 3:1):
   ```bash
   python3 scripts/run.py forest.png banner.png --x 0 --y 85 --width 768 --height 256
   ```
3. Send `banner.png` to user

---

### 6. Iterative refinement (remix → remix)
**User says:** "Generate a robot, make it steampunk, then make it even more weathered"

**Steps:**
1. Run `comfyui-generate-image`:
   ```bash
   python3 scripts/run.py "detailed humanoid robot, clean design, standing pose, studio lighting" robot.png
   ```
2. Run `comfyui-img2img-remix` for steampunk:
   ```bash
   python3 scripts/run.py robot.png robot_steampunk.png --prompt "steampunk mechanical robot, brass gears, copper pipes, Victorian engineering" --denoise 0.55
   ```
3. Run `comfyui-img2img-remix` again for weathering:
   ```bash
   python3 scripts/run.py robot_steampunk.png robot_weathered.png --prompt "heavily weathered and aged steampunk robot, rust, patina, battle damage, dust" --denoise 0.4
   ```
4. Send `robot_weathered.png` to user

---

### 7. Generate + User uploads their own image for remix
**User says:** "Here's my photo, make it look like a comic book character"

**Steps:**
1. User sends an image (saved locally as `user_photo.png`)
2. Run `comfyui-img2img-remix`:
   ```bash
   python3 scripts/run.py user_photo.png comic.png --prompt "comic book character illustration, bold outlines, cel shading, vibrant colors, Marvel style" --denoise 0.6
   ```
3. Send `comic.png` to user

---

## Decision flowchart

When a user makes a request, follow this logic:

1. **Does the request involve an existing image?**
   - Yes → Does it need cropping? → `comfyui-crop` or `comfyui-crop-then-refine`
   - Yes → Does it need restyling? → `comfyui-img2img-remix`
   - No → Continue to step 2

2. **What type of output does the user want?**
   - Video/MP4 → `comfyui-video-clip`
   - Animation/GIF/sticker → `comfyui-animated-webp`
   - Portrait/headshot/face → `comfyui-portrait`
   - Landscape/scenery + variations → `comfyui-landscape-batch`
   - Uses specific LoRA → `comfyui-lora`
   - Anything else → `comfyui-generate-image`

3. **Does the request have multiple steps?**
   - "Generate X and then Y" → Chain the appropriate skills in sequence
   - "Give me options then..." → Use batch skill, wait for user choice, then chain

4. **Always confirm the plan before executing.**
   - Tell the user which skills you'll chain and in what order
   - Wait for their approval before running

## Passing outputs between skills

When chaining skills, the output file from one becomes the input file of the next:
- Skill A writes to `step1_output.png`
- Skill B reads from `step1_output.png` and writes to `step2_output.png`
- Send `step2_output.png` to the user (or all intermediate files if they want to see progress)

## Tips for better chains

1. **Lower denoise for second-pass refinement** — if chaining two img2img operations, use denoise 0.5 for the first and 0.3-0.4 for the second to avoid over-processing
2. **Match dimensions** — when cropping then remixing, the crop dimensions become the remix dimensions
3. **Save intermediate files** — keep all outputs so the user can go back to any step
4. **Let the user guide iteration** — after each step, show the result and ask if they want to continue or adjust
