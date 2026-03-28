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
# Configuration — env vars first, then openclaw.json fallback
# ---------------------------------------------------------------------------

def _load_from_openclaw_config(skill_name="comfyui-generate-image"):
    """Fallback: read COMFY_URL and COMFY_AUTH_HEADER from openclaw.json."""
    config_path = os.path.join(os.path.expanduser("~"), ".openclaw", "openclaw.json")
    if not os.path.exists(config_path):
        return {}, {}
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        entries = config.get("skills", {}).get("entries", {})
        # Try the exact skill name first, then any comfyui-* skill
        for key in [skill_name] + [k for k in entries if k.startswith("comfyui-")]:
            entry = entries.get(key, {})
            env = entry.get("env", {})
            if env.get("COMFY_URL"):
                return env, entry
        return {}, {}
    except Exception:
        return {}, {}


def _resolve_env():
    """Resolve COMFY_URL and COMFY_AUTH_HEADER from env or openclaw.json."""
    url = os.environ.get("COMFY_URL", "").rstrip("/")
    auth = os.environ.get("COMFY_AUTH_HEADER", "")

    if not url:
        fallback_env, _ = _load_from_openclaw_config()
        url = fallback_env.get("COMFY_URL", "").rstrip("/")
        auth = auth or fallback_env.get("COMFY_AUTH_HEADER", "")
        # Also inject into os.environ so subprocesses see them
        if url:
            os.environ["COMFY_URL"] = url
        if auth:
            os.environ["COMFY_AUTH_HEADER"] = auth

    return url, auth


COMFY_URL, COMFY_AUTH_HEADER = _resolve_env()
CHECKPOINT = os.environ.get("COMFY_CKPT", "sd1.5/juggernaut_reborn.safetensors")
TIMEOUT_SECONDS = int(os.environ.get("COMFY_TIMEOUT", "180"))
POLL_INTERVAL = 1.0


def check_env():
    """Validate that required configuration is available."""
    global COMFY_URL, COMFY_AUTH_HEADER
    # Re-resolve in case env was set after module import
    if not COMFY_URL:
        COMFY_URL, COMFY_AUTH_HEADER = _resolve_env()
    if not COMFY_URL:
        print("Error: COMFY_URL not set (checked env vars and ~/.openclaw/openclaw.json)", file=sys.stderr)
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


def _safe_request(url, data=None, method="GET", timeout=30):
    """Like make_request but returns (data, error) instead of exiting."""
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=_headers(), method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            if raw:
                return json.loads(raw), None
            return {}, None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return None, f"HTTP {e.code}: {error_body}"
    except urllib.error.URLError as e:
        return None, f"Connection error: {e.reason}"
    except Exception as e:
        return None, str(e)


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


def upload_video(filepath):
    """Upload a local video to ComfyUI /upload/image endpoint. Returns the server filename."""
    import mimetypes
    boundary = "----ComfyUploadBoundary"
    filename = os.path.basename(filepath)
    mime = mimetypes.guess_type(filepath)[0] or "video/mp4"

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
        with urllib.request.urlopen(req, timeout=120) as resp:
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


def wait_for_completion(prompt_id, timeout=None):
    """Poll ComfyUI history until the prompt completes. Returns output metadata."""
    max_wait = timeout or TIMEOUT_SECONDS
    start = time.time()
    while time.time() - start < max_wait:
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

    print(f"Timeout after {max_wait}s waiting for generation", file=sys.stderr)
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


# ---------------------------------------------------------------------------
# Utility functions (used by utility skills)
# ---------------------------------------------------------------------------

def get_progress(prompt_id=None):
    """Get generation progress. Tries /progress first, falls back to queue/history."""
    # Try /progress endpoint first
    progress_url = f"{COMFY_URL}/progress"
    data, err = _safe_request(progress_url)

    if data and not err:
        value = data.get("value", 0)
        max_val = data.get("max", 0)
        if max_val > 0:
            pct = round((value / max_val) * 100, 1)
            return {
                "status": "running" if pct < 100 else "done",
                "progress_percent": pct,
                "value": value,
                "max": max_val,
                "state": "generating",
                "source": "progress_endpoint",
            }

    # Fallback: use queue + history
    queue_data, q_err = _safe_request(f"{COMFY_URL}/queue")
    if q_err:
        return {"status": "error", "progress_percent": 0, "state": "unknown", "source": "error", "error": q_err}

    running = queue_data.get("queue_running", [])
    pending = queue_data.get("queue_pending", [])

    # Check if our prompt is running
    if prompt_id:
        for item in running:
            if len(item) > 1 and item[1] == prompt_id:
                elapsed = time.time() - item[0] if isinstance(item[0], (int, float)) else 0
                # Estimate: ramp from 20% to 95% over expected time
                pct = min(95, 20 + (elapsed / 120) * 75)
                return {
                    "status": "running",
                    "progress_percent": round(pct, 1),
                    "state": "generating",
                    "source": "queue_fallback",
                    "queue_running": len(running),
                    "queue_pending": len(pending),
                }
        for item in pending:
            if len(item) > 1 and item[1] == prompt_id:
                pct = min(15, 5 + (len(pending) - 1) * 2)
                return {
                    "status": "pending",
                    "progress_percent": round(pct, 1),
                    "state": "queued",
                    "source": "queue_fallback",
                    "queue_running": len(running),
                    "queue_pending": len(pending),
                }

        # Check history for completion
        hist_data, h_err = _safe_request(f"{COMFY_URL}/history/{prompt_id}")
        if hist_data and prompt_id in hist_data:
            return {
                "status": "done",
                "progress_percent": 100,
                "state": "completed",
                "source": "history",
            }

    # Generic status
    if running:
        return {
            "status": "busy",
            "progress_percent": 50,
            "state": "server_busy",
            "source": "queue_fallback",
            "queue_running": len(running),
            "queue_pending": len(pending),
        }

    return {
        "status": "idle",
        "progress_percent": 0,
        "state": "idle",
        "source": "queue_fallback",
        "queue_running": 0,
        "queue_pending": len(pending),
    }


def get_queue_status():
    """Get queue status: running and pending job counts."""
    data, err = _safe_request(f"{COMFY_URL}/queue")
    if err:
        return {"status": "error", "error": err, "running_count": 0, "pending_count": 0, "running": [], "pending": []}

    running = data.get("queue_running", [])
    pending = data.get("queue_pending", [])
    return {
        "status": "ok",
        "running_count": len(running),
        "pending_count": len(pending),
        "running": running,
        "pending": pending,
    }


def get_server_status():
    """Get server health: system stats + queue state."""
    stats_data, stats_err = _safe_request(f"{COMFY_URL}/system_stats")
    queue_info = get_queue_status()

    if stats_err:
        return {
            "status": "error",
            "error": stats_err,
            "busy": False,
            "running_count": 0,
            "pending_count": 0,
            "queue": {},
            "system_stats": {},
        }

    return {
        "status": "ok",
        "busy": queue_info["running_count"] > 0,
        "running_count": queue_info["running_count"],
        "pending_count": queue_info["pending_count"],
        "queue": queue_info,
        "system_stats": stats_data,
    }


def validate_server_models(model_names=None, include_groups=None, case_sensitive=False):
    """List available models and validate requested ones exist."""
    data, err = _safe_request(f"{COMFY_URL}/object_info")
    if err:
        return {"status": "error", "error": err, "available": {}, "all_model_names": [], "exists": {}, "missing": []}

    # Known model loader nodes and their input fields
    loaders = {
        "checkpoints": ("CheckpointLoaderSimple", "ckpt_name"),
        "vae": ("VAELoader", "vae_name"),
        "clip": ("CLIPLoader", "clip_name"),
        "lora": ("LoraLoader", "lora_name"),
        "unet": ("UNETLoader", "unet_name"),
    }

    available = {}
    all_names = []

    for group, (node_type, field_name) in loaders.items():
        if include_groups and group not in include_groups:
            continue
        node_info = data.get(node_type, {})
        inputs = node_info.get("input", {}).get("required", {})
        field_info = inputs.get(field_name, [])
        names = field_info[0] if field_info and isinstance(field_info[0], list) else []
        available[group] = names
        all_names.extend(names)

    # Validate requested models
    exists = {}
    missing = []
    if model_names:
        for name in model_names:
            if case_sensitive:
                found = name in all_names
            else:
                found = name.lower() in [n.lower() for n in all_names]
            exists[name] = found
            if not found:
                missing.append(name)

    return {
        "status": "ok",
        "available": available,
        "all_model_names": all_names,
        "exists": exists,
        "missing": missing,
    }


def list_comfy_assets():
    """List files in ComfyUI input and output directories."""
    results = {"status": "ok", "input": [], "output": []}

    for asset_type in ["input", "output"]:
        url = f"{COMFY_URL}/view?type={asset_type}"
        # The /view endpoint without filename lists directory contents on some setups
        # Fall back to empty list if it doesn't work
        data, err = _safe_request(url)
        if data and isinstance(data, list):
            results[asset_type] = data
        elif err:
            # Try alternative: some ComfyUI versions use different endpoints
            results[asset_type] = []

    return results


def delete_job(prompt_id):
    """Delete/cancel a job from the ComfyUI queue."""
    payload = {"delete": [prompt_id]}
    data, err = _safe_request(f"{COMFY_URL}/queue", data=payload, method="POST")
    if err:
        return {"status": "error", "error": err, "prompt_id": prompt_id}
    return {"status": "ok", "deleted": prompt_id}
