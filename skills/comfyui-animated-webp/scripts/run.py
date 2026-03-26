#!/usr/bin/env python3
"""Generate animated WebP images from text using SD 1.5."""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
from comfy_lib import (
    CHECKPOINT, check_env, queue_prompt, wait_for_completion, download_output,
)


def build_workflow(prompt, negative_prompt, width, height, frames, fps, steps, cfg, seed):
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
            "inputs": {"width": width, "height": height, "batch_size": frames},
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
            "class_type": "SaveAnimatedWebP",
            "inputs": {
                "images": ["6", 0],
                "filename_prefix": "openclaw_animated",
                "fps": fps,
                "lossless": False,
                "quality": 80,
                "method": "default",
            },
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Generate animated WebP from text")
    parser.add_argument("prompt", help="Animation description")
    parser.add_argument("output", help="Output file path (.webp)")
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--fps", type=int, default=6)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--cfg", type=float, default=7.0)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--negative", default="watermark, text, blurry, low quality, extra limbs")
    args = parser.parse_args()

    check_env()
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    print(f"Generating {args.frames}-frame animation...")
    print(f"  Prompt: \"{args.prompt}\"")
    print(f"  Size: {args.width}x{args.height}, Frames: {args.frames}, FPS: {args.fps}, Seed: {seed}")

    workflow = build_workflow(args.prompt, args.negative, args.width, args.height, args.frames, args.fps, args.steps, args.cfg, seed)
    prompt_id = queue_prompt(workflow)
    print(f"  Queued: {prompt_id}")

    result = wait_for_completion(prompt_id)

    # Animated WebP comes back as images
    output_meta = None
    if result["images"]:
        output_meta = result["images"][0]
    elif result["videos"]:
        output_meta = result["videos"][0]

    if not output_meta:
        print("No output returned", file=sys.stderr)
        sys.exit(1)

    output_path = args.output
    if not output_path.lower().endswith(".webp"):
        output_path += ".webp"

    size_kb = download_output(output_meta, output_path)
    print(f"Animation saved to: {output_path}")
    print(f"  Size: {size_kb:.1f} KB, Seed: {seed}")


if __name__ == "__main__":
    main()
