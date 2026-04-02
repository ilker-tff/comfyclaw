#!/usr/bin/env python3
"""Unified image editing: crop, img2img remix, crop+refine."""

import argparse
import os
import random
import sys

_skills_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_skills_root, "_shared"))
sys.path.insert(0, os.path.join(_skills_root, "shared"))
import time as _time
from comfy_lib import (
    CHECKPOINT, check_env, upload_image, queue_prompt, wait_for_completion, download_output,
)
from catalog import load_workflow_json, apply_overrides
from learning import log_generation, get_learned_defaults, get_context


# ── Built-in workflows ─────────────────────────────────────────────────────

def build_crop(image_name, x, y, width, height):
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "2": {"class_type": "ImageCrop", "inputs": {"image": ["1", 0], "x": x, "y": y, "width": width, "height": height}},
        "3": {"class_type": "SaveImage", "inputs": {"images": ["2", 0], "filename_prefix": "openclaw_crop"}},
    }


def build_remix(image_name, prompt, negative, steps, denoise, cfg, seed):
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "2": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": prompt}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": negative}},
        "5": {"class_type": "VAEEncode", "inputs": {"pixels": ["1", 0], "vae": ["2", 2]}},
        "6": {"class_type": "KSampler", "inputs": {
            "model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0], "latent_image": ["5", 0],
            "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "euler", "scheduler": "normal", "denoise": denoise,
        }},
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["2", 2]}},
        "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": "openclaw_remix"}},
    }


def build_crop_refine(image_name, prompt, negative, x, y, width, height, steps, denoise, cfg, seed):
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "2": {"class_type": "ImageCrop", "inputs": {"image": ["1", 0], "x": x, "y": y, "width": width, "height": height}},
        "3": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 1], "text": prompt}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 1], "text": negative}},
        "6": {"class_type": "VAEEncode", "inputs": {"pixels": ["2", 0], "vae": ["3", 2]}},
        "7": {"class_type": "KSampler", "inputs": {
            "model": ["3", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0],
            "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "euler", "scheduler": "normal", "denoise": denoise,
        }},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "openclaw_crop_refine"}},
    }


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Edit images using ComfyUI")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--mode", choices=["crop", "remix", "refine"], default="remix")
    parser.add_argument("--prompt", default=None, help="Style/transformation prompt")
    parser.add_argument("--negative", default="watermark, text, blurry, low quality, artifacts")
    parser.add_argument("--x", type=int, default=0)
    parser.add_argument("--y", type=int, default=0)
    parser.add_argument("--width", type=int, default=256)
    parser.add_argument("--height", type=int, default=256)
    parser.add_argument("--denoise", type=float, default=0.55)
    parser.add_argument("--steps", type=int, default=28)
    parser.add_argument("--cfg", type=float, default=7.0)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--workflow", default=None, help="Curated workflow ID or JSON path")
    args = parser.parse_args()

    check_env()

    # Load learned context
    learned = get_learned_defaults("comfyui-edit")
    ctx = get_context()
    if ctx:
        print(f"  [Learning] Context loaded ({len(ctx)} chars)")

    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.mode in ("remix", "refine") and not args.prompt:
        print("Error: --prompt is required for remix and refine modes", file=sys.stderr)
        sys.exit(1)

    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    # Upload input image to ComfyUI server
    server_name = upload_image(args.input)

    if args.workflow:
        # Curated workflow mode
        if os.path.isfile(args.workflow):
            wf, defaults = load_workflow_json(file_path=args.workflow)
        else:
            wf, defaults = load_workflow_json(workflow_id=args.workflow)
        overrides = {
            "image": server_name, "prompt": args.prompt or "", "negative": args.negative,
            "x": args.x, "y": args.y, "width": args.width, "height": args.height,
            "denoise": args.denoise, "steps": args.steps, "cfg": args.cfg,
            "seed": seed, "checkpoint": CHECKPOINT,
        }
        workflow = apply_overrides(wf, overrides)
        mode_label = f"curated ({args.workflow})"
    elif args.mode == "crop":
        workflow = build_crop(server_name, args.x, args.y, args.width, args.height)
        mode_label = f"crop ({args.x},{args.y}) {args.width}x{args.height}"
    elif args.mode == "remix":
        workflow = build_remix(server_name, args.prompt, args.negative, args.steps, args.denoise, args.cfg, seed)
        mode_label = f"remix (denoise={args.denoise})"
    else:  # refine
        workflow = build_crop_refine(server_name, args.prompt, args.negative, args.x, args.y, args.width, args.height, args.steps, args.denoise, args.cfg, seed)
        mode_label = f"crop+refine ({args.x},{args.y}) {args.width}x{args.height}"

    print(f"Editing image ({mode_label})...")
    print(f"  Input: {args.input}")
    if args.prompt:
        print(f"  Prompt: \"{args.prompt}\"")
    if args.mode != "crop":
        print(f"  Denoise: {args.denoise}, Steps: {args.steps}, Seed: {seed}")

    t0 = _time.time()
    prompt_id = queue_prompt(workflow)
    print(f"  Queued: {prompt_id}")

    result = wait_for_completion(prompt_id)
    duration_s = round(_time.time() - t0, 1)

    if not result["images"]:
        print("No images returned", file=sys.stderr)
        sys.exit(1)

    output_path = args.output
    if not output_path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        output_path += ".png"

    size_kb = download_output(result["images"][0], output_path)
    print(f"Saved to: {output_path} ({size_kb:.1f} KB)")
    if args.mode != "crop":
        print(f"  Seed: {seed}")

    # Log to learning history
    log_generation(
        skill="comfyui-edit",
        prompt=args.prompt or "",
        params={"mode": args.mode, "denoise": args.denoise, "steps": args.steps,
                "cfg": args.cfg, "width": args.width, "height": args.height},
        output_path=output_path,
        seed=seed,
        duration_s=duration_s,
    )


if __name__ == "__main__":
    main()
