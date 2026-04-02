#!/usr/bin/env python3
"""Generate video clips from text using Wan 2.1 text-to-video model."""

import argparse
import os
import random
import sys

_skills_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_skills_root, "_shared"))
sys.path.insert(0, os.path.join(_skills_root, "shared"))
import time as _time
from comfy_lib import check_env, queue_prompt, wait_for_completion, download_output
from catalog import load_workflow_json, apply_overrides
from learning import log_generation, get_learned_defaults, get_context


def build_wan21_t2v(prompt, negative, width, height, frames, fps, steps, cfg, seed):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.1/wan2.1_t2v_1.3B_fp16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": negative}},
        "6": {"class_type": "EmptyHunyuanLatentVideo", "inputs": {"width": width, "height": height, "length": frames, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0],
            "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "uni_pc", "scheduler": "simple", "denoise": 1.0,
        }},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "VHS_VideoCombine", "inputs": {
            "images": ["8", 0], "frame_rate": fps, "loop_count": 0,
            "filename_prefix": "openclaw_video", "format": "video/h264-mp4",
            "pix_fmt": "yuv420p", "crf": 19, "save_metadata": True,
            "trim_to_audio": False, "pingpong": False, "save_output": True,
        }},
    }


def main():
    parser = argparse.ArgumentParser(description="Generate video clips from text")
    parser.add_argument("prompt", help="Video description")
    parser.add_argument("output", help="Output file path (.mp4)")
    parser.add_argument("--width", type=int, default=848)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--frames", type=int, default=25)
    parser.add_argument("--fps", type=int, default=16)
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--cfg", type=float, default=8.0)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--negative", default="Overexposure, static, blurred details, low quality, artifacts")
    parser.add_argument("--workflow", default=None, help="Curated workflow ID or JSON path")
    args = parser.parse_args()

    check_env()
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    # Load learned context
    learned = get_learned_defaults("comfyui-video")
    ctx = get_context()
    if ctx:
        print(f"  [Learning] Context loaded ({len(ctx)} chars)")

    if args.workflow:
        if os.path.isfile(args.workflow):
            wf, defaults = load_workflow_json(file_path=args.workflow)
        else:
            wf, defaults = load_workflow_json(workflow_id=args.workflow)
        overrides = {
            "prompt": args.prompt, "negative": args.negative,
            "width": args.width, "height": args.height, "frames": args.frames,
            "fps": args.fps, "seed": seed, "steps": args.steps, "cfg": args.cfg,
        }
        workflow = apply_overrides(wf, overrides)
        mode = f"curated ({args.workflow})"
    else:
        workflow = build_wan21_t2v(args.prompt, args.negative, args.width, args.height, args.frames, args.fps, args.steps, args.cfg, seed)
        mode = "Wan 2.1 t2v"

    duration = args.frames / args.fps
    print(f"Generating video clip ({mode})...")
    print(f"  Prompt: \"{args.prompt}\"")
    print(f"  Size: {args.width}x{args.height}, Frames: {args.frames}, FPS: {args.fps} (~{duration:.1f}s)")
    print(f"  Steps: {args.steps}, CFG: {args.cfg}, Seed: {seed}")
    print(f"  (This may take 60-120 seconds)")

    t0 = _time.time()
    prompt_id = queue_prompt(workflow)
    print(f"  Queued: {prompt_id}")

    result = wait_for_completion(prompt_id)
    duration_s = round(_time.time() - t0, 1)

    output_meta = None
    if result["videos"]:
        output_meta = result["videos"][0]
    elif result["images"]:
        output_meta = result["images"][0]

    if not output_meta:
        print("No video output returned", file=sys.stderr)
        sys.exit(1)

    output_path = args.output
    if not output_path.lower().endswith((".mp4", ".webm")):
        output_path += ".mp4"

    size_kb = download_output(output_meta, output_path)
    print(f"Video saved to: {output_path} ({size_kb:.1f} KB, Seed: {seed})")

    # Log to learning history
    log_generation(
        skill="comfyui-video",
        prompt=args.prompt,
        params={"width": args.width, "height": args.height, "frames": args.frames,
                "fps": args.fps, "steps": args.steps, "cfg": args.cfg},
        output_path=output_path,
        seed=seed,
        duration_s=duration_s,
    )


if __name__ == "__main__":
    main()
