---
name: comfyui-generate-image
description: "Generate images from text descriptions using ComfyUI with Stable Diffusion 1.5. This is the PRIMARY image generation skill. Use it when the user asks to create, generate, draw, paint, render, or make any image from a text description. Handles all styles: photorealistic, cinematic, artistic, illustration, fantasy, product photography, concept art, and more. Use this skill for ANY text-to-image request unless the user specifically asks for portraits (use comfyui-portrait), landscapes (use comfyui-landscape-batch), animations (use comfyui-animated-webp), video (use comfyui-video-clip), or image-to-image transformation (use comfyui-img2img-remix)."
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
            "image-generation",
            "text-to-image",
            "stable-diffusion",
            "comfyui"
        ],
        "category": "media-generation",
        "input_type": "text",
        "output_type": "image/png",
        "output_can_feed_into": [
            "comfyui-crop",
            "comfyui-img2img-remix",
            "comfyui-crop-then-refine",
            "comfyui-img2video",
            "comfyui-download-image"
        ],
        "accepts_input_from": [],
        "priority": 100,
        "files": [
            "scripts/*"
        ]
    }
}
---

# ComfyUI Image Generation

Generate images from text prompts using Stable Diffusion 1.5 on a remote ComfyUI server.

## When to use this skill

- User asks to "generate", "create", "make", "draw", "paint", "render" an image
- User describes a scene, object, character, or concept they want visualized
- User wants a specific art style applied to a text description
- General image generation — this is the default/fallback image skill

## When NOT to use this skill

- User wants to modify an **existing image** → use `comfyui-img2img-remix`
- User wants to **crop** an image → use `comfyui-crop`
- User specifically wants a **portrait** → use `comfyui-portrait` (optimized for faces)
- User wants **multiple landscape variations** → use `comfyui-landscape-batch`
- User wants **animation** → use `comfyui-animated-webp`
- User wants **video** → use `comfyui-video-clip`
- User wants to use a **LoRA model** → use `comfyui-lora`

## Usage

```bash
python3 scripts/run.py "<prompt>" <output-path> [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--width` | 512 | Image width in pixels (256-2048) |
| `--height` | 512 | Image height in pixels (256-2048) |
| `--steps` | 35 | Sampling steps (more = better quality, slower) |
| `--cfg` | 7.0 | Classifier-free guidance scale |
| `--seed` | random | Seed for reproducibility |
| `--negative` | `"watermark, text, blurry, low quality, deformed, extra fingers"` | Negative prompt |

### Examples

```bash
# Product photo
python3 scripts/run.py "cinematic product photo of a red sneaker on white background, studio lighting" sneaker.png

# Fantasy art
python3 scripts/run.py "epic dragon flying over a medieval castle, dramatic sunset, digital art" dragon.png --width 768 --height 512

# Specific seed for reproducibility
python3 scripts/run.py "a steampunk clocktower in the rain" clock.png --seed 42
```

## Chaining with other skills

This skill's output image can be:
- **Cropped** using `comfyui-crop` to extract a region
- **Restyled** using `comfyui-img2img-remix` to apply a different artistic style
- **Refined** using `comfyui-crop-then-refine` to crop a region and enhance it

## Confirm before running

Before generating, tell the user:
> "I'll generate an image of [description] at [width]x[height]. This will take ~30 seconds. Go ahead?"

## Prompt tips for best results

1. Be specific about style, lighting, composition, mood
2. Use art terms: "cinematic lighting", "8K", "shallow depth of field", "oil painting"
3. Describe subjects in detail: character features, poses, expressions
4. Set the scene: environment, background, atmosphere
5. Use negative prompt to exclude unwanted elements

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/prompt` | Submit workflow | Text prompt, dimensions, sampling params |
| `$COMFY_URL/history/<id>` | Poll job status | Prompt ID |
| `$COMFY_URL/view?filename=<f>` | Download image | Filename |
