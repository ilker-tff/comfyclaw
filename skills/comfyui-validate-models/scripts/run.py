#!/usr/bin/env python3
"""List available models on ComfyUI server and validate specific models."""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from comfy_lib import check_env, make_request, COMFY_URL

# Mapping of friendly group names to ComfyUI node class and input field
MODEL_GROUP_MAP = {
    "checkpoints": ("CheckpointLoaderSimple", "ckpt_name"),
    "vae": ("VAELoader", "vae_name"),
    "clip": ("CLIPLoader", "clip_name"),
    "lora": ("LoraLoader", "lora_name"),
    "unet": ("UNETLoader", "unet_name"),
}


def validate_server_models(models=None, groups=None):
    """List available models and optionally validate specific model names."""
    object_info = make_request(f"{COMFY_URL}/object_info")

    target_groups = groups if groups else list(MODEL_GROUP_MAP.keys())

    available = {}
    all_model_names = set()

    for group_name in target_groups:
        if group_name not in MODEL_GROUP_MAP:
            continue
        node_class, field_name = MODEL_GROUP_MAP[group_name]
        node_info = object_info.get(node_class, {})
        input_info = node_info.get("input", {}).get("required", {})
        field_info = input_info.get(field_name, [])

        model_list = []
        if field_info and isinstance(field_info[0], list):
            model_list = sorted(field_info[0])

        available[group_name] = model_list
        all_model_names.update(model_list)

    result = {
        "status": "success",
        "available_models": available,
    }

    # Validate specific models if requested
    if models:
        validation = {}
        for model_name in models:
            model_name = model_name.strip()
            # Check exact match or partial match (basename)
            found = model_name in all_model_names
            if not found:
                # Try matching just the basename
                for available_name in all_model_names:
                    if available_name.endswith(model_name) or model_name in available_name:
                        found = True
                        break
            validation[model_name] = found
        result["validation"] = validation

    return result


def main():
    parser = argparse.ArgumentParser(description="List and validate ComfyUI server models")
    parser.add_argument("--models", default=None, help="Comma-separated model names to validate")
    parser.add_argument("--groups", default=None, help="Comma-separated groups: checkpoints,vae,clip,lora,unet")
    args = parser.parse_args()

    check_env()

    models = [m.strip() for m in args.models.split(",")] if args.models else None
    groups = [g.strip() for g in args.groups.split(",")] if args.groups else None

    result = validate_server_models(models=models, groups=groups)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
