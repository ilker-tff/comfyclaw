#!/usr/bin/env python3
"""
Shared ComfyUI HTTP client for OpenClaw skills.

Handles authentication, workflow submission, polling, and file download.
All skills import this module for consistent server interaction.

Environment variables:
    COMFY_URL          - ComfyUI server URL (e.g. http://34.30.216.121)
    COMFY_AUTH_HEADER  - Auth header value (e.g. "Basic dXNlcjpwYXNz")
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse


# ---------------------------------------------------------------------------
# Configuration (from environment)
# ---------------------------------------------------------------------------

COMFY_URL = os.environ.get("COMFY_URL", "").rstrip("/")
COMFY_AUTH_HEADER = os.environ.get("COMFY_AUTH_HEADER", "")
CHECKPOINT = os.environ.get("COMFY_CKPT", "sd1.5/juggernaut_reborn.safetensors")
TIMEOUT_SECONDS = int(os.environ.get("COMFY_TIMEOUT", "180"))
POLL_INTERVAL = 1.0


def check_env():
    """Validate that required environment variables are set."""
    if not COMFY_URL:
        print("Error: COMFY_URL environment variable not set", file=sys.stderr)
        sys.exit(1)
    if not COMFY_AUTH_HEADER:
        print("Warning: COMFY_AUTH_HEADER not set, attempting without auth", file=sys.stderr)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _headers(content_type="application/json"):
    h = {}
    if content_type:
        h["Content-Type"] = content_type
    if COMFY_AUTH_HEADER:
        h["Authorization"] = COMFY_AUTH_HEADER
    return h


def make_request(url, data=None, method="GET"):
    """Make an HTTP request with auth headers. Returns parsed JSON."""
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=_headers(), method=method)
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


def download_binary(url, dest_path):
    """Download binary content (image/video) to a file."""
    req = urllib.request.Request(url, headers=_headers(content_type=None), method="GET")
    with urllib.request.urlopen(req, timeout=60) as resp:
        with open(dest_path, "wb") as f:
            f.write(resp.read())


def upload_image(filepath):
    """Upload a local image to ComfyUI /upload/image endpoint. Returns the server filename."""
    import mimetypes
    boundary = "----ComfyUploadBoundary"
    filename = os.path.basename(filepath)
    mime = mimetypes.guess_type(filepath)[0] or "image/png"

    with open(filepath, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    url = f"{COMFY_URL}/upload/image"
    headers = _headers(content_type=f"multipart/form-data; boundary={boundary}")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("name", filename)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"Upload failed - HTTP {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# ComfyUI API interaction
# ---------------------------------------------------------------------------

def queue_prompt(workflow):
    """Submit a workflow to ComfyUI and return the prompt_id."""
    payload = {"prompt": workflow}
    result = make_request(f"{COMFY_URL}/prompt", data=payload, method="POST")
    prompt_id = result.get("prompt_id")
    if not prompt_id:
        print(f"Unexpected response: {result}", file=sys.stderr)
        sys.exit(1)
    return prompt_id


def wait_for_completion(prompt_id):
    """Poll ComfyUI history until the prompt completes. Returns output metadata."""
    start = time.time()
    while time.time() - start < TIMEOUT_SECONDS:
        try:
            history = make_request(f"{COMFY_URL}/history/{prompt_id}")
        except SystemExit:
            time.sleep(POLL_INTERVAL)
            continue

        entry = history.get(prompt_id)
        if not entry:
            time.sleep(POLL_INTERVAL)
            continue

        status = entry.get("status", {})
        if status.get("status_str") == "error":
            messages = status.get("messages", [])
            print(f"ComfyUI execution error: {messages}", file=sys.stderr)
            sys.exit(1)

        outputs = entry.get("outputs", {})

        # Collect images
        images = []
        for node_id, node_output in outputs.items():
            for img in node_output.get("images", []):
                images.append(img)

        # Collect videos (VHS_VideoCombine outputs gifs/videos)
        videos = []
        for node_id, node_output in outputs.items():
            for vid in node_output.get("gifs", []):
                videos.append(vid)

        if images or videos:
            return {"images": images, "videos": videos}

        time.sleep(POLL_INTERVAL)

    print(f"Timeout after {TIMEOUT_SECONDS}s waiting for generation", file=sys.stderr)
    sys.exit(1)


def download_output(meta, dest_path):
    """Download a generated file from ComfyUI /view endpoint."""
    params = urllib.parse.urlencode({
        "filename": meta["filename"],
        "subfolder": meta.get("subfolder", ""),
        "type": meta.get("type", "output"),
    })
    url = f"{COMFY_URL}/view?{params}"
    download_binary(url, dest_path)
    size_kb = os.path.getsize(dest_path) / 1024
    return size_kb
