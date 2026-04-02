#!/usr/bin/env python3
"""Unified image generation: text-to-image, portrait, landscape, LoRA, animated WebP."""

import argparse
import os
import random
import sys

_skills_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_skills_root, "_shared"))
sys.path.insert(0, os.path.join(_skills_root, "shared"))
import time as _time
from comfy_lib import (
    CHECKPOINT, check_env, queue_prompt, wait_for_completion, download_output,
)
from catalog import load_workflow_json, apply_overrides, find_workflow
from learning import log_generation, get_learned_defaults, get_context


# ── Aspect presets ──────────────────────────────────────────────────────────

ASPECTS = {
    "square":    (512, 512),
    "portrait":  (512, 768),
    "landscape": (768, 512),
    "widescreen": (768, 432),
}


# ── Built-in workflow builders (fallbacks) ──────────────────────────────────

def build_txt2img(prompt, negative, width, height, batch, steps, cfg, seed):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": prompt}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": negative}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": batch}},
        "5": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0],
            "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
        }},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "openclaw_generate"}},
    }


def build_lora(prompt, negative, lora, strength, width, height, steps, cfg, seed):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": lora, "strength_model": strength}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": prompt}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": negative}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "6": {"class_type": "KSampler", "inputs": {
            "model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0], "latent_image": ["5", 0],
            "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
        }},
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": "openclaw_lora"}},
    }


def build_animated_webp(prompt, negative, width, height, frames, fps, steps, cfg, seed):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": prompt}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": negative}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": frames}},
        "5": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0],
            "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
        }},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveAnimatedWebP", "inputs": {
            "images": ["6", 0], "filename_prefix": "openclaw_animated",
            "fps": fps, "lossless": False, "quality": 80, "method": "default",
        }},
    }


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate images from text using ComfyUI")
    parser.add_argument("prompt", help="Text prompt")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--aspect", choices=list(ASPECTS.keys()), default=None, help="Aspect preset")
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--height", type=int, default=None)
    parser.add_argument("--batch", type=int, default=1, help="Number of variations")
    parser.add_argument("--steps", type=int, default=35)
    parser.add_argument("--cfg", type=float, default=7.0)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--negative", default="watermark, text, blurry, low quality, deformed, extra fingers")
    parser.add_argument("--lora", default=None, help="LoRA adapter filename")
    parser.add_argument("--lora-strength", type=float, default=1.0)
    parser.add_argument("--format", choices=["png", "webp"], default="png")
    parser.add_argument("--frames", type=int, default=8, help="Frames for animated WebP")
    parser.add_argument("--fps", type=int, default=6, help="FPS for animated WebP")
    parser.add_argument("--workflow", default=None, help="Curated workflow ID or JSON path")
    args = parser.parse_args()

    check_env()
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    # Load learned defaults (non-destructive — only suggest, don't override explicit args)
    learned = get_learned_defaults("comfyui-generate")
    ctx = get_context()
    if ctx:
        print(f"  [Learning] Context loaded ({len(ctx)} chars)")

    # Resolve dimensions
    if args.width and args.height:
        width, height = args.width, args.height
    elif args.aspect:
        width, height = ASPECTS[args.aspect]
    else:
        width = learned.get("width", 512)
        height = learned.get("height", 512)

    # Route to the right workflow
    is_animated = args.format == "webp"
    is_lora = args.lora is not None

    if args.workflow:
        # Use curated workflow
        if os.path.isfile(args.workflow):
            wf, defaults = load_workflow_json(file_path=args.workflow)
        else:
            wf, defaults = load_workflow_json(workflow_id=args.workflow)
        overrides = {
            "prompt": args.prompt, "negative": args.negative,
            "width": width, "height": height, "seed": seed,
            "steps": args.steps, "cfg": args.cfg, "checkpoint": CHECKPOINT,
            "batch": args.batch,
        }
        if is_lora and args.lora:
            overrides["lora"] = args.lora
            overrides["lora_strength"] = args.lora_strength
        if is_animated:
            overrides["frames"] = args.frames
            overrides["fps"] = args.fps
        workflow = apply_overrides(wf, overrides)
        mode = f"curated ({args.workflow})"
    elif is_animated:
        workflow = build_animated_webp(args.prompt, args.negative, width, height, args.frames, args.fps, args.steps, args.cfg, seed)
        mode = "animated WebP"
    elif is_lora:
        workflow = build_lora(args.prompt, args.negative, args.lora, args.lora_strength, width, height, args.steps, args.cfg, seed)
        mode = f"LoRA ({args.lora})"
    else:
        workflow = build_txt2img(args.prompt, args.negative, width, height, args.batch, args.steps, args.cfg, seed)
        mode = "txt2img"

    print(f"Generating image ({mode})...")
    print(f"  Prompt: \"{args.prompt}\"")
    print(f"  Size: {width}x{height}, Steps: {args.steps}, CFG: {args.cfg}, Seed: {seed}")
    if args.batch > 1:
        print(f"  Batch: {args.batch} variations")

    t0 = _time.time()
    prompt_id = queue_prompt(workflow)
    print(f"  Queued: {prompt_id}")

    result = wait_for_completion(prompt_id)
    duration_s = round(_time.time() - t0, 1)

    # Handle output
    if is_animated:
        output_meta = result["images"][0] if result["images"] else (result["videos"][0] if result["videos"] else None)
        if not output_meta:
            print("No output returned", file=sys.stderr)
            sys.exit(1)
        output_path = args.output if args.output.lower().endswith(".webp") else args.output + ".webp"
        size_kb = download_output(output_meta, output_path)
        print(f"Animation saved to: {output_path} ({size_kb:.1f} KB)")
    elif args.batch > 1 and len(result["images"]) > 1:
        saved = []
        for i, img_meta in enumerate(result["images"]):
            base, ext = os.path.splitext(args.output)
            if not ext:
                ext = ".png"
            out = f"{base}_{i + 1}{ext}"
            size_kb = download_output(img_meta, out)
            saved.append(out)
            print(f"  Saved: {out} ({size_kb:.1f} KB)")
        print(f"\n{len(saved)} images saved. Seed: {seed}")
    else:
        if not result["images"]:
            print("No images returned", file=sys.stderr)
            sys.exit(1)
        output_path = args.output
        if not output_path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            output_path += ".png"
        size_kb = download_output(result["images"][0], output_path)
        print(f"Image saved to: {output_path} ({size_kb:.1f} KB, Seed: {seed})")

    # Log to learning history
    final_output = output_path if not is_animated else (args.output if args.output.lower().endswith(".webp") else args.output + ".webp")
    log_generation(
        skill="comfyui-generate",
        prompt=args.prompt,
        params={"width": width, "height": height, "steps": args.steps, "cfg": args.cfg,
                "batch": args.batch, "mode": mode, "lora": args.lora,
                "format": args.format},
        output_path=final_output,
        seed=seed,
        duration_s=duration_s,
    )


if __name__ == "__main__":
    main()
