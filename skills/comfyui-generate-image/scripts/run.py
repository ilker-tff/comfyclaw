#!/usr/bin/env python3
"""Generate images from text using ComfyUI + Stable Diffusion 1.5."""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
from comfy_lib import (
    COMFY_URL, CHECKPOINT, check_env, queue_prompt, wait_for_completion, download_output,
)


def build_workflow(prompt, negative_prompt, width, height, steps, cfg, seed):
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": CHECKPOINT},
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["1", 1], "text": prompt},
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["1", 1], "text": negative_prompt},
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
            },
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {"images": ["6", 0], "filename_prefix": "openclaw_generate"},
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Generate images from text using ComfyUI")
    parser.add_argument("prompt", help="Text prompt")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--steps", type=int, default=35)
    parser.add_argument("--cfg", type=float, default=7.0)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--negative", default="watermark, text, blurry, low quality, deformed, extra fingers")
    args = parser.parse_args()

    check_env()
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    print(f"Generating image...")
    print(f"  Prompt: \"{args.prompt}\"")
    print(f"  Size: {args.width}x{args.height}, Steps: {args.steps}, CFG: {args.cfg}, Seed: {seed}")

    workflow = build_workflow(args.prompt, args.negative, args.width, args.height, args.steps, args.cfg, seed)
    prompt_id = queue_prompt(workflow)
    print(f"  Queued: {prompt_id}")

    result = wait_for_completion(prompt_id)
    if not result["images"]:
        print("No images returned", file=sys.stderr)
        sys.exit(1)

    output_path = args.output
    if not output_path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        output_path += ".png"

    size_kb = download_output(result["images"][0], output_path)
    print(f"Image saved to: {output_path}")
    print(f"  Size: {size_kb:.1f} KB, Seed: {seed}")


if __name__ == "__main__":
    main()
