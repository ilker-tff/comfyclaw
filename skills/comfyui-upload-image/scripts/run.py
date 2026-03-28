#!/usr/bin/env python3
"""Upload a local image file to the ComfyUI server's input storage."""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from comfy_lib import check_env, upload_image


def main():
    parser = argparse.ArgumentParser(description="Upload a local image to ComfyUI server")
    parser.add_argument("image_path", help="Local path to the image file to upload")
    args = parser.parse_args()

    check_env()

    filepath = os.path.expanduser(args.image_path)
    if not os.path.isfile(filepath):
        print(json.dumps({"status": "error", "message": f"File not found: {filepath}"}))
        sys.exit(1)

    print(f"Uploading image: {filepath}", file=sys.stderr)
    server_filename = upload_image(filepath)

    result = {
        "status": "success",
        "server_filename": server_filename,
        "original_path": filepath,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
