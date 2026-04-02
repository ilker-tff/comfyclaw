#!/usr/bin/env python3
"""Run any ComfyUI workflow: curated, file-based, or inline JSON."""

import argparse
import json
import os
import random
import sys

_skills_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_skills_root, "_shared"))
sys.path.insert(0, os.path.join(_skills_root, "shared"))
import time as _time
from comfy_lib import (
    CHECKPOINT, check_env, upload_image, queue_prompt, wait_for_completion, download_output,
)
from catalog import list_workflows, search_workflows, load_workflow_json, apply_overrides
from learning import log_generation, log_feedback, get_context, get_history, update_preferences


def main():
    parser = argparse.ArgumentParser(description="Run any ComfyUI workflow")
    parser.add_argument("--workflow", default=None, help="Curated workflow ID or path to JSON file")
    parser.add_argument("--json", default=None, help="Inline JSON workflow string")
    parser.add_argument("--output", default=None, help="Output file path")
    parser.add_argument("--input", default=None, help="Input image to upload")
    parser.add_argument("--prompt", default=None)
    parser.add_argument("--negative", default=None)
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--height", type=int, default=None)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--cfg", type=float, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--denoise", type=float, default=None)
    parser.add_argument("--batch", type=int, default=None)
    parser.add_argument("--frames", type=int, default=None)
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--lora", default=None)
    parser.add_argument("--lora-strength", type=float, default=None)
    parser.add_argument("--list", action="store_true", help="List available workflows")
    parser.add_argument("--search", default=None, help="Search workflows by keyword")
    # Learning commands
    parser.add_argument("--feedback", choices=["liked", "disliked", "neutral"], default=None, help="Record feedback for a generation")
    parser.add_argument("--feedback-file", default=None, help="Output file to attach feedback to")
    parser.add_argument("--feedback-notes", default=None, help="Free-text notes for feedback")
    parser.add_argument("--show-history", action="store_true", help="Show recent generation history")
    parser.add_argument("--show-context", action="store_true", help="Show learned user context")
    parser.add_argument("--set-preference", nargs=2, metavar=("KEY", "VALUE"), default=None, help="Set a user preference")
    args = parser.parse_args()

    # List mode
    if args.list:
        workflows = list_workflows()
        print(f"Available workflows ({len(workflows)}):\n")
        for w in workflows:
            tags = ", ".join(w["tags"])
            print(f"  {w['id']:25s} {w['name']:30s} [{tags}]")
        return

    # Search mode
    if args.search:
        results = search_workflows(args.search)
        if not results:
            print(f"No workflows matching '{args.search}'")
            return
        print(f"Workflows matching '{args.search}':\n")
        for w in results:
            tags = ", ".join(w["tags"])
            print(f"  {w['id']:25s} {w['name']:30s} [{tags}]")
        return

    # Feedback mode
    if args.feedback and args.feedback_file:
        updated = log_feedback(args.feedback_file, args.feedback, args.feedback_notes)
        if updated:
            print(f"Feedback recorded: {args.feedback} for {args.feedback_file}")
            if args.feedback_notes:
                print(f"  Notes: {args.feedback_notes}")
        else:
            print(f"No matching generation found for: {args.feedback_file}")
        return

    # Show history
    if args.show_history:
        history = get_history(limit=20)
        if not history:
            print("No generation history yet.")
            return
        print(f"Recent generations ({len(history)}):\n")
        for h in history:
            fb = h.get("feedback", "-")
            skill = h.get("skill", "?")
            prompt = h.get("prompt", "?")[:50]
            output = h.get("output", "?")
            print(f"  [{skill}] \"{prompt}\" → {output} ({fb})")
        return

    # Show context
    if args.show_context:
        ctx = get_context()
        if ctx:
            print(ctx)
        else:
            print("No learning context yet. Generate some images and give feedback to build it.")
        return

    # Set preference
    if args.set_preference:
        key, value = args.set_preference
        # Try to parse as number
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass
        prefs = update_preferences({key: value})
        print(f"Preference set: {key} = {value}")
        return

    # Execution mode
    if not args.workflow and not args.json:
        print("Error: provide --workflow, --json, --list, or --search", file=sys.stderr)
        sys.exit(1)

    if not args.output:
        print("Error: --output is required", file=sys.stderr)
        sys.exit(1)

    check_env()
    seed = args.seed if args.seed is not None else random.randint(1, 2**31)

    # Upload input image if provided
    server_image = None
    if args.input:
        if not os.path.isfile(args.input):
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        server_image = upload_image(args.input)

    if args.json:
        # Inline JSON mode
        try:
            workflow = json.loads(args.json)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
        mode = "inline JSON"
    else:
        # Curated or file workflow
        if os.path.isfile(args.workflow):
            wf, defaults = load_workflow_json(file_path=args.workflow)
            mode = f"file ({args.workflow})"
        else:
            wf, defaults = load_workflow_json(workflow_id=args.workflow)
            mode = f"curated ({args.workflow})"

        # Build overrides from provided args
        overrides = {"seed": seed, "checkpoint": CHECKPOINT}
        if server_image:
            overrides["image"] = server_image
        for key in ("prompt", "negative", "width", "height", "steps", "cfg", "denoise", "batch", "frames", "fps"):
            val = getattr(args, key, None)
            if val is not None:
                overrides[key] = val
        if args.lora:
            overrides["lora"] = args.lora
        if args.lora_strength is not None:
            overrides["lora_strength"] = args.lora_strength

        workflow = apply_overrides(wf, overrides)

    print(f"Running workflow ({mode})...")
    if args.prompt:
        print(f"  Prompt: \"{args.prompt}\"")
    print(f"  Seed: {seed}")

    t0 = _time.time()
    prompt_id = queue_prompt(workflow)
    print(f"  Queued: {prompt_id}")

    result = wait_for_completion(prompt_id)
    duration_s = round(_time.time() - t0, 1)

    # Download outputs
    output_path = args.output
    if result["videos"]:
        if not output_path.lower().endswith((".mp4", ".webm")):
            output_path += ".mp4"
        size_kb = download_output(result["videos"][0], output_path)
        print(f"Video saved to: {output_path} ({size_kb:.1f} KB)")
    elif result["images"]:
        if len(result["images"]) > 1:
            for i, img_meta in enumerate(result["images"]):
                base, ext = os.path.splitext(output_path)
                if not ext:
                    ext = ".png"
                out = f"{base}_{i + 1}{ext}"
                size_kb = download_output(img_meta, out)
                print(f"  Saved: {out} ({size_kb:.1f} KB)")
            print(f"\n{len(result['images'])} outputs saved.")
        else:
            if not output_path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                output_path += ".png"
            size_kb = download_output(result["images"][0], output_path)
            print(f"Image saved to: {output_path} ({size_kb:.1f} KB)")
    else:
        print("No output returned", file=sys.stderr)
        sys.exit(1)

    # Log to learning history
    log_generation(
        skill="comfyui-workflow",
        prompt=args.prompt or "",
        params={"workflow": args.workflow or "inline", "width": args.width,
                "height": args.height, "steps": args.steps, "cfg": args.cfg},
        output_path=output_path,
        seed=seed,
        duration_s=duration_s,
    )


if __name__ == "__main__":
    main()
