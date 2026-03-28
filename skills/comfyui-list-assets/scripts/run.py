#!/usr/bin/env python3
"""List files available in ComfyUI's input and output directories."""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from comfy_lib import check_env, make_request, COMFY_URL


def list_comfy_assets():
    """List files in ComfyUI input and output directories."""
    result = {
        "status": "success",
        "input_files": [],
        "output_files": [],
    }

    # List input files
    try:
        # ComfyUI doesn't have a dedicated list endpoint, but /api/view-raw works
        # Try the standard approach: get history and extract filenames, or use object_info
        # Most reliable: use the /view endpoint with directory listing
        input_data = make_request(f"{COMFY_URL}/api/view-raw/input")
        if isinstance(input_data, list):
            result["input_files"] = sorted(input_data)
        elif isinstance(input_data, dict):
            result["input_files"] = sorted(input_data.keys()) if input_data else []
    except SystemExit:
        # Endpoint may not exist in all ComfyUI versions; try alternative
        try:
            input_data = make_request(f"{COMFY_URL}/view?type=input")
            if isinstance(input_data, list):
                result["input_files"] = sorted(input_data)
        except SystemExit:
            result["input_files_error"] = "Could not list input files"

    # List output files
    try:
        output_data = make_request(f"{COMFY_URL}/api/view-raw/output")
        if isinstance(output_data, list):
            result["output_files"] = sorted(output_data)
        elif isinstance(output_data, dict):
            result["output_files"] = sorted(output_data.keys()) if output_data else []
    except SystemExit:
        try:
            output_data = make_request(f"{COMFY_URL}/view?type=output")
            if isinstance(output_data, list):
                result["output_files"] = sorted(output_data)
        except SystemExit:
            result["output_files_error"] = "Could not list output files"

    return result


def main():
    parser = argparse.ArgumentParser(description="List ComfyUI input and output assets")
    parser.parse_args()

    check_env()

    result = list_comfy_assets()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
