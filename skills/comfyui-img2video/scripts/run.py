#!/usr/bin/env python3
"""Convert a still image into a short video clip using LTX-Video on ComfyUI."""

import argparse
import os
import random
import sys

# Override timeout for video generation before importing comfy_lib
os.environ.setdefault("COMFY_TIMEOUT", "600")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
from comfy_lib import check_env, queue_prompt, wait_for_completion, download_output


def build_workflow(image_filename, prompt, negative, width, height, frames, fps, steps, seed):
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "ltxv/ltx-video-2b-v0.9.5.safetensors"},
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["1", 1], "text": prompt},
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["1", 1], "text": negative},
        },
        "4": {
            "class_type": "LoadImage",
            "inputs": {"image": image_filename},
        },
        "5": {
            "class_type": "LTXVImgToVideo",
            "inputs": {
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "image": ["4", 0],
                "vae": ["1", 2],
                "width": width,
                "height": height,
                "length": frames,
                "seed": seed,
                "steps": steps,
                "cfg": 3.0,
                "batch_size": 1,
            },
        },
        "6": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["5", 0],
                "frame_rate": fps,
                "format": "video/h264-mp4",
                "filename_prefix": "openclaw_img2video",
            },
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Convert a still image into a short video clip using LTX-Video"
    )
    parser.add_argument("output", help="Output file path (.mp4)")
    parser.add_argument("--image", required=True, help="Image filename on ComfyUI server")
    parser.add_argument("--prompt", required=True, help="Motion/animation description")
    parser.add_argument("--negative", default="low quality, blurry, distorted",
                        help="Negative prompt")
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--frames", type=int, default=97)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    check_env()
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    duration_sec = args.frames / args.fps
    print(f"Generating video from image...")
    print(f"  Image: {args.image}")
    print(f"  Prompt: \"{args.prompt}\"")
    print(f"  Size: {args.width}x{args.height}, Frames: {args.frames}, FPS: {args.fps}")
    print(f"  Duration: ~{duration_sec:.1f}s, Steps: {args.steps}, Seed: {seed}")
    print(f"  (Video generation takes 10-15 minutes)")

    workflow = build_workflow(
        args.image, args.prompt, args.negative,
        args.width, args.height, args.frames,
        args.fps, args.steps, seed,
    )
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
