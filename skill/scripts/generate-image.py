#!/usr/bin/env python3
"""
ComfyUI Text-to-Image Generator for OpenClaw

Generates images using a remote ComfyUI server with Stable Diffusion 1.5.

Environment variables:
    COMFY_URL          - ComfyUI server URL (e.g. http://34.30.216.121)
    COMFY_AUTH_HEADER  - Auth header value (e.g. "Basic dXNlcjpwYXNz")

Usage:
    python3 generate-image.py "A futuristic city" output.png
    python3 generate-image.py "A portrait" out.png --width 768 --height 512 --steps 40
"""

import argparse
import json
import os
import random
import sys
import time
import urllib.request
import urllib.error
import urllib.parse


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COMFY_URL = os.environ.get("COMFY_URL", "http://34.30.216.121")
COMFY_AUTH_HEADER = os.environ.get("COMFY_AUTH_HEADER", "")
CHECKPOINT = os.environ.get("COMFY_CKPT", "sd1.5/juggernaut_reborn.safetensors")
TIMEOUT_SECONDS = 120
POLL_INTERVAL = 1.0


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _make_request(url, data=None, method="GET"):
    """Make an HTTP request with auth headers."""
    headers = {"Content-Type": "application/json"}
    if COMFY_AUTH_HEADER:
        headers["Authorization"] = COMFY_AUTH_HEADER

    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def _download_binary(url, dest_path):
    """Download binary content (image) to a file."""
    headers = {}
    if COMFY_AUTH_HEADER:
        headers["Authorization"] = COMFY_AUTH_HEADER

    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=30) as resp:
        with open(dest_path, "wb") as f:
            f.write(resp.read())


# ---------------------------------------------------------------------------
# ComfyUI workflow builder
# ---------------------------------------------------------------------------

def build_txt2img_workflow(prompt, negative_prompt, width, height, steps, cfg, seed):
    """Build a ComfyUI API-format workflow for txt2img."""
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": CHECKPOINT
            }
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["1", 1],
                "text": prompt
            }
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["1", 1],
                "text": negative_prompt
            }
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            }
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["5", 0],
                "vae": ["1", 2]
            }
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {
                "images": ["6", 0],
                "filename_prefix": "openclaw_txt2img"
            }
        }
    }


# ---------------------------------------------------------------------------
# ComfyUI API interaction
# ---------------------------------------------------------------------------

def queue_prompt(workflow):
    """Submit a workflow to ComfyUI and return the prompt_id."""
    base = COMFY_URL.rstrip("/")
    payload = {"prompt": workflow}
    result = _make_request(f"{base}/prompt", data=payload, method="POST")
    prompt_id = result.get("prompt_id")
    if not prompt_id:
        print(f"Unexpected response: {result}", file=sys.stderr)
        sys.exit(1)
    return prompt_id


def wait_for_completion(prompt_id):
    """Poll ComfyUI history until the prompt completes. Returns output images metadata."""
    base = COMFY_URL.rstrip("/")
    start = time.time()

    while time.time() - start < TIMEOUT_SECONDS:
        try:
            history = _make_request(f"{base}/history/{prompt_id}")
        except SystemExit:
            # history endpoint may 404 while job is queued
            time.sleep(POLL_INTERVAL)
            continue

        entry = history.get(prompt_id)
        if not entry:
            time.sleep(POLL_INTERVAL)
            continue

        # Check for execution error
        status = entry.get("status", {})
        if status.get("status_str") == "error":
            messages = status.get("messages", [])
            print(f"ComfyUI execution error: {messages}", file=sys.stderr)
            sys.exit(1)

        outputs = entry.get("outputs", {})
        images = []
        for node_id, node_output in outputs.items():
            for img in node_output.get("images", []):
                images.append(img)

        if images:
            return images

        time.sleep(POLL_INTERVAL)

    print(f"Timeout after {TIMEOUT_SECONDS}s waiting for generation", file=sys.stderr)
    sys.exit(1)


def download_image(image_meta, dest_path):
    """Download a generated image from ComfyUI /view endpoint."""
    base = COMFY_URL.rstrip("/")
    params = urllib.parse.urlencode({
        "filename": image_meta["filename"],
        "subfolder": image_meta.get("subfolder", ""),
        "type": image_meta.get("type", "output"),
    })
    url = f"{base}/view?{params}"
    _download_binary(url, dest_path)
    size_kb = os.path.getsize(dest_path) / 1024
    return size_kb


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate images from text using ComfyUI + Stable Diffusion"
    )
    parser.add_argument("prompt", help="Text prompt for image generation")
    parser.add_argument("output", help="Output file path (e.g. output.png)")
    parser.add_argument("--width", type=int, default=512, help="Image width (default: 512)")
    parser.add_argument("--height", type=int, default=512, help="Image height (default: 512)")
    parser.add_argument("--steps", type=int, default=35, help="Sampling steps (default: 35)")
    parser.add_argument("--cfg", type=float, default=7.0, help="CFG scale (default: 7.0)")
    parser.add_argument("--seed", type=int, default=None, help="Seed (default: random)")
    parser.add_argument(
        "--negative",
        default="watermark, text, blurry, low quality, deformed, extra fingers",
        help="Negative prompt",
    )

    args = parser.parse_args()
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    if not COMFY_URL:
        print("Error: COMFY_URL environment variable not set", file=sys.stderr)
        sys.exit(1)

    if not COMFY_AUTH_HEADER:
        print("Warning: COMFY_AUTH_HEADER not set, attempting without auth", file=sys.stderr)

    print(f"Generating image...")
    print(f"  Prompt: \"{args.prompt}\"")
    print(f"  Size: {args.width}x{args.height}, Steps: {args.steps}, CFG: {args.cfg}, Seed: {seed}")
    print(f"  Server: {COMFY_URL}")

    # Build and submit workflow
    workflow = build_txt2img_workflow(
        prompt=args.prompt,
        negative_prompt=args.negative,
        width=args.width,
        height=args.height,
        steps=args.steps,
        cfg=args.cfg,
        seed=seed,
    )

    prompt_id = queue_prompt(workflow)
    print(f"  Queued: {prompt_id}")

    # Wait for result
    images = wait_for_completion(prompt_id)
    if not images:
        print("No images returned", file=sys.stderr)
        sys.exit(1)

    # Download first image
    output_path = args.output
    if not output_path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        output_path += ".png"

    size_kb = download_image(images[0], output_path)

    print(f"Image saved to: {output_path}")
    print(f"  Size: {size_kb:.1f} KB")
    print(f"  Seed: {seed}")


if __name__ == "__main__":
    main()
