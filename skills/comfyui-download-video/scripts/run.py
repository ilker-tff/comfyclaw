#!/usr/bin/env python3
"""Download a generated video from the ComfyUI server to a local file."""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from comfy_lib import check_env, download_output


def main():
    parser = argparse.ArgumentParser(description="Download a generated video from ComfyUI server")
    parser.add_argument("output_path", help="Local path to save the downloaded video")
    parser.add_argument("--filename", required=True, help="Server-side filename")
    parser.add_argument("--subfolder", default="", help="Server subfolder (default: empty)")
    parser.add_argument("--type", default="output", dest="file_type", help="Output type: output or temp (default: output)")
    args = parser.parse_args()

    check_env()

    output_path = os.path.expanduser(args.output_path)
    if not output_path.lower().endswith((".mp4", ".webm", ".webp", ".gif", ".mov")):
        output_path += ".mp4"

    meta = {
        "filename": args.filename,
        "subfolder": args.subfolder,
        "type": args.file_type,
    }

    print(f"Downloading video: {args.filename}", file=sys.stderr)
    try:
        size_kb = download_output(meta, output_path)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

    result = {
        "status": "success",
        "local_path": output_path,
        "size_kb": round(size_kb, 1),
        "filename": args.filename,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
