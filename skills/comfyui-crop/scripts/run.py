#!/usr/bin/env python3
"""Crop a region from an image using ComfyUI."""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
from comfy_lib import check_env, upload_image, queue_prompt, wait_for_completion, download_output


def build_workflow(image_name, x, y, width, height):
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
            "class_type": "SaveImage",
            "inputs": {"images": ["2", 0], "filename_prefix": "openclaw_crop"},
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Crop a region from an image")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--x", type=int, default=0, help="Crop X coordinate")
    parser.add_argument("--y", type=int, default=0, help="Crop Y coordinate")
    parser.add_argument("--width", type=int, default=256, help="Crop width")
    parser.add_argument("--height", type=int, default=256, help="Crop height")
    args = parser.parse_args()

    check_env()

    if not os.path.isfile(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Cropping image...")
    print(f"  Input: {args.input}")
    print(f"  Region: ({args.x}, {args.y}) {args.width}x{args.height}")

    server_name = upload_image(args.input)
    workflow = build_workflow(server_name, args.x, args.y, args.width, args.height)
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
    print(f"Cropped image saved to: {output_path}")
    print(f"  Size: {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
