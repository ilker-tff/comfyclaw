#!/usr/bin/env python3
"""
Per-user learning system for ComfyUI skills.

Stores generation history, user preferences, and a context summary in the
user's OpenClaw workspace. Skills read this before execution to make better
parameter choices.

Data lives at: ~/.openclaw/workspace/comfyui/
  - history.jsonl    — one JSON line per generation (prompt, params, feedback)
  - preferences.json — learned defaults (preferred styles, sizes, denoise, etc.)
  - context.md       — human-readable summary for the LLM

Multi-user: each user has their own workspace (via OPENCLAW_PROFILE), so
learning data is automatically isolated.
"""

import json
import os
import time
from collections import Counter
from pathlib import Path


def _workspace_dir():
    """Get the ComfyUI learning directory inside the user's workspace."""
    profile = os.environ.get("OPENCLAW_PROFILE", "")
    if profile:
        base = os.path.expanduser(f"~/.openclaw/workspace-{profile}")
    else:
        base = os.path.expanduser("~/.openclaw/workspace")
    return os.path.join(base, "comfyui")


def _ensure_dir():
    d = _workspace_dir()
    os.makedirs(d, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------

def log_generation(skill, prompt, params, output_path, seed, duration_s=None):
    """Append a generation record to history.jsonl."""
    d = _ensure_dir()
    record = {
        "ts": time.time(),
        "skill": skill,
        "prompt": prompt,
        "params": params,
        "output": output_path,
        "seed": seed,
        "duration_s": duration_s,
        "feedback": None,  # filled in later by log_feedback
    }
    with open(os.path.join(d, "history.jsonl"), "a") as f:
        f.write(json.dumps(record) + "\n")
    return record


def log_feedback(output_path, feedback, notes=None):
    """Record user feedback for a specific generation.

    feedback: "liked", "disliked", or "neutral"
    notes: optional free-text (e.g. "too blurry", "perfect colors")
    """
    d = _ensure_dir()
    history_path = os.path.join(d, "history.jsonl")
    if not os.path.exists(history_path):
        return False

    # Read all lines, update the matching one, rewrite
    lines = []
    updated = False
    with open(history_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if not updated and record.get("output") == output_path:
                record["feedback"] = feedback
                if notes:
                    record["feedback_notes"] = notes
                updated = True
            lines.append(json.dumps(record))

    if updated:
        with open(history_path, "w") as f:
            f.write("\n".join(lines) + "\n")
        # Regenerate context after feedback
        _rebuild_context()
    return updated


def get_history(limit=50):
    """Read the most recent history entries."""
    d = _workspace_dir()
    history_path = os.path.join(d, "history.jsonl")
    if not os.path.exists(history_path):
        return []
    entries = []
    with open(history_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries[-limit:]


# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------

def get_preferences():
    """Load user preferences. Returns dict (empty if none yet)."""
    d = _workspace_dir()
    prefs_path = os.path.join(d, "preferences.json")
    if os.path.exists(prefs_path):
        with open(prefs_path, "r") as f:
            return json.load(f)
    return {}


def update_preferences(updates):
    """Merge updates into preferences."""
    d = _ensure_dir()
    prefs = get_preferences()
    prefs.update(updates)
    with open(os.path.join(d, "preferences.json"), "w") as f:
        json.dump(prefs, f, indent=2)
    return prefs


# ---------------------------------------------------------------------------
# Context generation
# ---------------------------------------------------------------------------

def _rebuild_context():
    """Regenerate context.md from history and preferences."""
    d = _ensure_dir()
    history = get_history(limit=100)
    prefs = get_preferences()

    lines = ["# ComfyUI User Context", ""]
    lines.append("Auto-generated from generation history and feedback. Read this before choosing parameters.")
    lines.append("")

    # Preferences section
    if prefs:
        lines.append("## User Preferences")
        lines.append("")
        for key, val in prefs.items():
            lines.append(f"- **{key}**: {val}")
        lines.append("")

    if not history:
        lines.append("*No generation history yet.*")
        with open(os.path.join(d, "context.md"), "w") as f:
            f.write("\n".join(lines))
        return

    # Stats
    total = len(history)
    liked = [h for h in history if h.get("feedback") == "liked"]
    disliked = [h for h in history if h.get("feedback") == "disliked"]

    lines.append("## Generation Stats")
    lines.append("")
    lines.append(f"- Total generations: {total}")
    lines.append(f"- Liked: {len(liked)}, Disliked: {len(disliked)}")
    lines.append("")

    # Analyze liked generations for patterns
    if liked:
        lines.append("## What Works (from liked generations)")
        lines.append("")

        # Common aspect ratios
        sizes = Counter()
        for h in liked:
            p = h.get("params", {})
            w = p.get("width", p.get("aspect"))
            he = p.get("height")
            if w and he:
                sizes[f"{w}x{he}"] += 1
        if sizes:
            top_sizes = sizes.most_common(3)
            lines.append(f"- Preferred sizes: {', '.join(f'{s} ({c}x)' for s, c in top_sizes)}")

        # Common styles/themes from prompts
        style_words = Counter()
        style_keywords = [
            "cinematic", "watercolor", "oil painting", "photo", "realistic",
            "anime", "cartoon", "digital art", "fantasy", "sci-fi", "portrait",
            "landscape", "dramatic", "soft", "vibrant", "dark", "bright",
            "detailed", "minimalist", "abstract", "vintage", "modern",
        ]
        for h in liked:
            prompt_lower = h.get("prompt", "").lower()
            for kw in style_keywords:
                if kw in prompt_lower:
                    style_words[kw] += 1
        if style_words:
            top_styles = style_words.most_common(5)
            lines.append(f"- Preferred styles: {', '.join(f'{s} ({c}x)' for s, c in top_styles)}")

        # Common param ranges
        cfgs = [h["params"].get("cfg") for h in liked if h.get("params", {}).get("cfg")]
        steps_list = [h["params"].get("steps") for h in liked if h.get("params", {}).get("steps")]
        denoises = [h["params"].get("denoise") for h in liked if h.get("params", {}).get("denoise")]

        if cfgs:
            avg_cfg = sum(cfgs) / len(cfgs)
            lines.append(f"- Average CFG for liked: {avg_cfg:.1f}")
        if steps_list:
            avg_steps = sum(steps_list) / len(steps_list)
            lines.append(f"- Average steps for liked: {avg_steps:.0f}")
        if denoises:
            avg_denoise = sum(denoises) / len(denoises)
            lines.append(f"- Average denoise for liked: {avg_denoise:.2f}")

        lines.append("")

    # Analyze disliked for anti-patterns
    if disliked:
        lines.append("## What Doesn't Work (from disliked generations)")
        lines.append("")
        for h in disliked[-5:]:  # last 5 disliked
            notes = h.get("feedback_notes", "no notes")
            lines.append(f"- \"{h.get('prompt', '?')[:60]}\" — {notes}")
        lines.append("")

    # Recent generations (last 5)
    lines.append("## Recent Generations")
    lines.append("")
    for h in history[-5:]:
        fb = h.get("feedback", "no feedback")
        skill = h.get("skill", "?")
        prompt = h.get("prompt", "?")[:50]
        lines.append(f"- [{skill}] \"{prompt}\" → {fb}")
    lines.append("")

    with open(os.path.join(d, "context.md"), "w") as f:
        f.write("\n".join(lines))


def get_context():
    """Read the context.md file. Returns empty string if none yet."""
    d = _workspace_dir()
    ctx_path = os.path.join(d, "context.md")
    if os.path.exists(ctx_path):
        with open(ctx_path, "r") as f:
            return f.read()
    return ""


def get_learned_defaults(skill):
    """Get suggested parameter defaults based on history and preferences.

    Returns a dict of parameter overrides the skill should consider.
    """
    prefs = get_preferences()
    history = get_history(limit=50)

    # Start with explicit preferences
    defaults = {}
    if "default_width" in prefs:
        defaults["width"] = prefs["default_width"]
    if "default_height" in prefs:
        defaults["height"] = prefs["default_height"]
    if "default_steps" in prefs:
        defaults["steps"] = prefs["default_steps"]
    if "default_cfg" in prefs:
        defaults["cfg"] = prefs["default_cfg"]
    if "default_negative" in prefs:
        defaults["negative"] = prefs["default_negative"]

    # Learn from liked generations for this skill
    liked = [h for h in history if h.get("feedback") == "liked" and h.get("skill") == skill]
    if len(liked) >= 3:
        # Use average params from liked generations as suggestions
        cfgs = [h["params"]["cfg"] for h in liked if "cfg" in h.get("params", {})]
        steps_list = [h["params"]["steps"] for h in liked if "steps" in h.get("params", {})]
        denoises = [h["params"]["denoise"] for h in liked if "denoise" in h.get("params", {})]

        if cfgs and "cfg" not in defaults:
            defaults["suggested_cfg"] = round(sum(cfgs) / len(cfgs), 1)
        if steps_list and "steps" not in defaults:
            defaults["suggested_steps"] = round(sum(steps_list) / len(steps_list))
        if denoises:
            defaults["suggested_denoise"] = round(sum(denoises) / len(denoises), 2)

    return defaults
