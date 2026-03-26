#!/usr/bin/env python3
"""Generate images using SD 1.5 with a LoRA adapter."""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
from comfy_lib import (
    CHECKPOINT, check_env, queue_prompt, wait_for_completion, download_output,
)


def build_workflow(prompt, negative_prompt, lora_name, strength, width, height, steps, cfg, seed):
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": CHECKPOINT},
        },
        "2": {
            "class_type": "LoraLoaderModelOnly",
            "inputs": {
                "model": ["1", 0],
                "lora_name": lora_name,
                "strength_model": strength,
            },
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["1", 1], "text": prompt},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["1", 1], "text": negative_prompt},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": width, "height": height, "batch_size": 1},
        },
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["2", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["5", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
            },
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["6", 0], "vae": ["1", 2]},
        },
        "8": {
            "class_type": "SaveImage",
            "inputs": {"images": ["7", 0], "filename_prefix": "openclaw_lora"},
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Generate images with LoRA adapter")
    parser.add_argument("prompt", help="Text prompt")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--lora", required=True, help="LoRA filename")
    parser.add_argument("--strength", type=float, default=1.0)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--steps", type=int, default=35)
    parser.add_argument("--cfg", type=float, default=7.0)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--negative", default="watermark, text, blurry, low quality, deformed")
    args = parser.parse_args()

    check_env()
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    print(f"Generating with LoRA...")
    print(f"  Prompt: \"{args.prompt}\"")
    print(f"  LoRA: {args.lora} (strength: {args.strength})")
    print(f"  Size: {args.width}x{args.height}, Steps: {args.steps}, Seed: {seed}")

    workflow = build_workflow(args.prompt, args.negative, args.lora, args.strength, args.width, args.height, args.steps, args.cfg, seed)
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
    print(f"LoRA image saved to: {output_path}")
    print(f"  Size: {size_kb:.1f} KB, Seed: {seed}")


if __name__ == "__main__":
    main()
