#!/usr/bin/env python3
"""Check ComfyUI queue status."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
from comfy_lib import check_env, get_queue_status


def main():
    check_env()
    result = get_queue_status()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
