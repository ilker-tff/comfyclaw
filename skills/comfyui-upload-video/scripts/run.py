#!/usr/bin/env python3
"""Upload a local video file to the ComfyUI server's input storage."""

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from comfy_lib import check_env, COMFY_URL, _headers


def upload_video(filepath):
    """Upload a local video to ComfyUI /upload/image endpoint. Returns the server filename."""
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


def main():
    parser = argparse.ArgumentParser(description="Upload a local video to ComfyUI server")
    parser.add_argument("video_path", help="Local path to the video file to upload")
    args = parser.parse_args()

    check_env()

    filepath = os.path.expanduser(args.video_path)
    if not os.path.isfile(filepath):
        print(json.dumps({"status": "error", "message": f"File not found: {filepath}"}))
        sys.exit(1)

    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    print(f"Uploading video: {filepath} ({size_mb:.1f} MB)", file=sys.stderr)
    server_filename = upload_video(filepath)

    result = {
        "status": "success",
        "server_filename": server_filename,
        "original_path": filepath,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
