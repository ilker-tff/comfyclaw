#!/usr/bin/env python3
"""Transform an existing image with a new style using img2img."""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
from comfy_lib import (
    CHECKPOINT, check_env, upload_image, queue_prompt, wait_for_completion, download_output,
)


def build_workflow(image_name, prompt, negative_prompt, steps, denoise, cfg, seed):
    return {
        "1": {
            "class_type": "LoadImage",
            "inputs": {"image": image_name},
        },
        "2": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": CHECKPOINT},
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["2", 1], "text": prompt},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["2", 1], "text": negative_prompt},
        },
        "5": {
            "class_type": "VAEEncode",
            "inputs": {"pixels": ["1", 0], "vae": ["2", 2]},
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
                "denoise": denoise,
            },
        },
        "7": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["6", 0], "vae": ["2", 2]},
        },
        "8": {
            "class_type": "SaveImage",
            "inputs": {"images": ["7", 0], "filename_prefix": "openclaw_remix"},
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Restyle an image using img2img")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--prompt", required=True, help="Style/transformation prompt")
    parser.add_argument("--negative", default="watermark, text, blurry, low quality, artifacts")
    parser.add_argument("--steps", type=int, default=28)
    parser.add_argument("--denoise", type=float, default=0.55)
    parser.add_argument("--cfg", type=float, default=7.0)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    check_env()
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Remixing image...")
    print(f"  Input: {args.input}")
    print(f"  Style: \"{args.prompt}\"")
    print(f"  Denoise: {args.denoise}, Steps: {args.steps}, Seed: {seed}")

    server_name = upload_image(args.input)
    workflow = build_workflow(server_name, args.prompt, args.negative, args.steps, args.denoise, args.cfg, seed)
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
    print(f"Remixed image saved to: {output_path}")
    print(f"  Size: {size_kb:.1f} KB, Seed: {seed}")


if __name__ == "__main__":
    main()
