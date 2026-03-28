#!/usr/bin/env python3
"""Check ComfyUI server health and system stats."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "_shared"))
from comfy_lib import check_env, get_server_status


def main():
    check_env()
    result = get_server_status()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
