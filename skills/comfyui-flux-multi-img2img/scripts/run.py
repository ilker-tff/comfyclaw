#!/usr/bin/env python3
"""Blend 2-3 reference images into a single output using Flux model on ComfyUI."""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
from comfy_lib import check_env, queue_prompt, wait_for_completion, download_output


def build_workflow(image1, image2, image3, prompt, width, height, steps, cfg, seed):
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "flux/flux1-dev-fp8.safetensors"},
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["1", 1], "text": prompt},
        },
        "3": {
            "class_type": "LoadImage",
            "inputs": {"image": image1},
        },
        "4": {
            "class_type": "LoadImage",
            "inputs": {"image": image2},
        },
        "6": {
            "class_type": "ImageBatch",
            "inputs": {"image1": ["3", 0], "image2": ["4", 0]},
        },
    }

    # If a third image is provided, load it and batch it in
    if image3:
        workflow["5"] = {
            "class_type": "LoadImage",
            "inputs": {"image": image3},
        }
        # Re-batch: combine the first batch with the third image
        workflow["6b"] = {
            "class_type": "ImageBatch",
            "inputs": {"image1": ["6", 0], "image2": ["5", 0]},
        }
        batch_output = "6b"
    else:
        batch_output = "6"

    workflow["7"] = {
        "class_type": "VAEEncode",
        "inputs": {"pixels": [batch_output, 0], "vae": ["1", 2]},
    }
    workflow["8"] = {
        "class_type": "KSampler",
        "inputs": {
            "model": ["1", 0],
            "positive": ["2", 0],
            "negative": ["2", 0],
            "latent_image": ["7", 0],
            "seed": seed,
            "steps": steps,
            "cfg": cfg,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 0.75,
        },
    }
    workflow["9"] = {
        "class_type": "VAEDecode",
        "inputs": {"samples": ["8", 0], "vae": ["1", 2]},
    }
    workflow["10"] = {
        "class_type": "SaveImage",
        "inputs": {"images": ["9", 0], "filename_prefix": "openclaw_flux_multi"},
    }

    return workflow


def main():
    parser = argparse.ArgumentParser(
        description="Blend 2-3 reference images into one using Flux model"
    )
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--image1", required=True, help="First reference image filename (on ComfyUI server)")
    parser.add_argument("--image2", required=True, help="Second reference image filename (on ComfyUI server)")
    parser.add_argument("--image3", default=None, help="Optional third reference image filename")
    parser.add_argument("--prompt", required=True, help="Text prompt describing the desired blend")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--cfg", type=float, default=3.5)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    check_env()
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    image_count = 3 if args.image3 else 2
    print(f"Blending {image_count} images with Flux...")
    print(f"  Image 1: {args.image1}")
    print(f"  Image 2: {args.image2}")
    if args.image3:
        print(f"  Image 3: {args.image3}")
    print(f"  Prompt: \"{args.prompt}\"")
    print(f"  Size: {args.width}x{args.height}, Steps: {args.steps}, CFG: {args.cfg}, Seed: {seed}")

    workflow = build_workflow(
        args.image1, args.image2, args.image3,
        args.prompt, args.width, args.height,
        args.steps, args.cfg, seed,
    )
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
    print(f"Blended image saved to: {output_path}")
    print(f"  Size: {size_kb:.1f} KB, Seed: {seed}")


if __name__ == "__main__":
    main()
