#!/usr/bin/env python3
"""Generate multiple landscape image variations in a batch."""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
from comfy_lib import (
    CHECKPOINT, check_env, queue_prompt, wait_for_completion, download_output,
)


def build_workflow(prompt, negative_prompt, width, height, batch_size, steps, cfg, seed):
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
            "inputs": {"width": width, "height": height, "batch_size": batch_size},
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
            "inputs": {"images": ["6", 0], "filename_prefix": "openclaw_landscape"},
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Generate landscape image variations")
    parser.add_argument("prompt", help="Landscape description")
    parser.add_argument("output", help="Output file prefix (files will be prefix_1.png, prefix_2.png, ...)")
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--batch", type=int, default=3)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--cfg", type=float, default=7.0)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--negative", default="watermark, text, low quality, blurry, oversaturated")
    args = parser.parse_args()

    check_env()
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    print(f"Generating {args.batch} landscape variations...")
    print(f"  Prompt: \"{args.prompt}\"")
    print(f"  Size: {args.width}x{args.height}, Batch: {args.batch}, Steps: {args.steps}, Seed: {seed}")

    workflow = build_workflow(args.prompt, args.negative, args.width, args.height, args.batch, args.steps, args.cfg, seed)
    prompt_id = queue_prompt(workflow)
    print(f"  Queued: {prompt_id}")

    result = wait_for_completion(prompt_id)
    if not result["images"]:
        print("No images returned", file=sys.stderr)
        sys.exit(1)

    saved = []
    for i, img_meta in enumerate(result["images"]):
        output_path = f"{args.output}_{i + 1}.png"
        size_kb = download_output(img_meta, output_path)
        saved.append(output_path)
        print(f"  Saved: {output_path} ({size_kb:.1f} KB)")

    print(f"\n{len(saved)} landscape images saved. Seed: {seed}")


if __name__ == "__main__":
    main()
