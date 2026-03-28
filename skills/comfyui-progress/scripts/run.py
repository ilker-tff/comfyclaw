#!/usr/bin/env python3
"""Check ComfyUI generation progress."""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
from comfy_lib import check_env, get_progress


def main():
    parser = argparse.ArgumentParser(description="Check generation progress")
    parser.add_argument("--prompt-id", default=None, help="Specific prompt ID to check")
    args = parser.parse_args()

    check_env()
    result = get_progress(args.prompt_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
