#!/usr/bin/env python3
"""Crop a region from an image and refine it with img2img."""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
from comfy_lib import (
    CHECKPOINT, check_env, upload_image, queue_prompt, wait_for_completion, download_output,
)


def build_workflow(image_name, prompt, negative_prompt, x, y, width, height, steps, denoise, cfg, seed):
    return {
        "1": {
            "class_type": "LoadImage",
            "inputs": {"image": image_name},
        },
        "2": {
            "class_type": "ImageCrop",
            "inputs": {
                "image": ["1", 0],
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            },
        },
        "3": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": CHECKPOINT},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["3", 1], "text": prompt},
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["3", 1], "text": negative_prompt},
        },
        "6": {
            "class_type": "VAEEncode",
            "inputs": {"pixels": ["2", 0], "vae": ["3", 2]},
        },
        "7": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["3", 0],
                "positive": ["4", 0],
                "negative": ["5", 0],
                "latent_image": ["6", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": denoise,
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["7", 0], "vae": ["3", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"images": ["8", 0], "filename_prefix": "openclaw_crop_refine"},
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Crop and refine a region of an image")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--prompt", required=True, help="Refinement prompt")
    parser.add_argument("--x", type=int, default=64)
    parser.add_argument("--y", type=int, default=64)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--steps", type=int, default=24)
    parser.add_argument("--denoise", type=float, default=0.5)
    parser.add_argument("--cfg", type=float, default=6.8)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--negative", default="watermark, text, blurry, low quality, distorted face")
    args = parser.parse_args()

    check_env()
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Crop + refine...")
    print(f"  Input: {args.input}")
    print(f"  Region: ({args.x}, {args.y}) {args.width}x{args.height}")
    print(f"  Prompt: \"{args.prompt}\"")
    print(f"  Denoise: {args.denoise}, Steps: {args.steps}, Seed: {seed}")

    server_name = upload_image(args.input)
    workflow = build_workflow(server_name, args.prompt, args.negative, args.x, args.y, args.width, args.height, args.steps, args.denoise, args.cfg, seed)
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
    print(f"Refined crop saved to: {output_path}")
    print(f"  Size: {size_kb:.1f} KB, Seed: {seed}")


if __name__ == "__main__":
    main()
