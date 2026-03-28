---
name: comfyui-progress
description: >
  Check the progress of a running ComfyUI generation job. Use this when a generation
  is in progress and you want to report the completion percentage to the user.
  Especially useful for long-running jobs like video generation (10-15 minutes).
  Tries the /progress endpoint first, falls back to queue/history-based estimation.
  Returns percentage, status (running/pending/done/idle), and queue info.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
metadata.clawdbot.tags: ["progress", "monitoring", "status", "polling", "comfyui"]
metadata.clawdbot.category: "utility"
metadata.clawdbot.input_type: "text"
metadata.clawdbot.output_type: "text/json"
metadata.clawdbot.output_can_feed_into: []
metadata.clawdbot.accepts_input_from: []
metadata.clawdbot.priority: 70
---

# ComfyUI Progress Check

Check the progress percentage of a running generation job.

## When to use this skill

- After submitting a generation job, to report progress to the user
- During long-running jobs (video generation takes 10-15 minutes)
- When the user asks "how's my image coming?" or "is it done yet?"

## When NOT to use this skill

- To check if the server is healthy → use `comfyui-server-status`
- To see how many jobs are queued → use `comfyui-queue-status`

## Usage

```bash
python3 scripts/run.py
python3 scripts/run.py --prompt-id "abc123-def456"
```

## Confirm before running

No confirmation needed — this is a read-only status check.

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/progress` | Primary progress endpoint | None |
| `$COMFY_URL/queue` | Fallback: queue inspection | None |
| `$COMFY_URL/history/<id>` | Fallback: completion check | Prompt ID |
