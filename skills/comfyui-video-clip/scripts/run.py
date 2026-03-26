#!/usr/bin/env python3
"""Generate video clips from text using Wan 2.1 text-to-video model."""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
from comfy_lib import check_env, queue_prompt, wait_for_completion, download_output


def build_workflow(prompt, negative_prompt, width, height, frames, fps, steps, cfg, seed):
    return {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "wan2.1/wan2.1_t2v_1.3B_fp16.safetensors",
                "weight_dtype": "default",
            },
        },
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
                "type": "wan",
                "device": "default",
            },
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "wan_2.1_vae.safetensors"},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["2", 0], "text": prompt},
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["2", 0], "text": negative_prompt},
        },
        "6": {
            "class_type": "EmptyHunyuanLatentVideo",
            "inputs": {
                "width": width,
                "height": height,
                "length": frames,
                "batch_size": 1,
            },
        },
        "7": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["4", 0],
                "negative": ["5", 0],
                "latent_image": ["6", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "uni_pc",
                "scheduler": "simple",
                "denoise": 1.0,
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["7", 0], "vae": ["3", 0]},
        },
        "9": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["8", 0],
                "frame_rate": fps,
                "loop_count": 0,
                "filename_prefix": "openclaw_video",
                "format": "video/h264-mp4",
                "pix_fmt": "yuv420p",
                "crf": 19,
                "save_metadata": True,
                "trim_to_audio": False,
                "pingpong": False,
                "save_output": True,
            },
        },
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
    args = parser.parse_args()

    check_env()
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    print(f"Generating video clip...")
    print(f"  Prompt: \"{args.prompt}\"")
    print(f"  Size: {args.width}x{args.height}, Frames: {args.frames}, FPS: {args.fps}")
    print(f"  Steps: {args.steps}, CFG: {args.cfg}, Seed: {seed}")
    print(f"  (This may take 60-120 seconds)")

    workflow = build_workflow(args.prompt, args.negative, args.width, args.height, args.frames, args.fps, args.steps, args.cfg, seed)
    prompt_id = queue_prompt(workflow)
    print(f"  Queued: {prompt_id}")

    result = wait_for_completion(prompt_id)

    # Video output comes through the gifs/videos key
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
    print(f"Video saved to: {output_path}")
    print(f"  Size: {size_kb:.1f} KB, Seed: {seed}")


if __name__ == "__main__":
    main()
