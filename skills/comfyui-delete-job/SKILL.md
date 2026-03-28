---
name: comfyui-delete-job
description: >
  Delete or cancel a ComfyUI generation job from the queue. Use this skill
  to cancel a stuck or unwanted generation job. Can remove jobs from either
  the running or pending queue. Takes the prompt ID of the job to cancel.
homepage: https://github.com/ilker-tff/comfyclaw
metadata.clawdbot.os: ["darwin", "linux"]
metadata.clawdbot.requires.bins: ["python3"]
metadata.clawdbot.requires.env: ["COMFY_URL", "COMFY_AUTH_HEADER"]
metadata.clawdbot.files: ["scripts/*"]
metadata.clawdbot.tags: ["cancel", "delete", "queue", "utility", "comfyui"]
metadata.clawdbot.category: "utility"
metadata.clawdbot.input_type: "text"
metadata.clawdbot.output_type: "text/json"
metadata.clawdbot.output_can_feed_into: []
metadata.clawdbot.accepts_input_from: []
metadata.clawdbot.priority: 40
---

# ComfyUI Delete Job

Delete or cancel a ComfyUI generation job from the queue.

## When to use this skill

- User asks to "cancel", "stop", or "abort" a generation
- A job appears stuck or is taking too long
- User submitted a job by mistake and wants to cancel it
- Clearing unwanted jobs from the pending queue

## When NOT to use this skill

- You want to check **job progress** → use `comfyui-progress`
- You want to check the **queue** → use `comfyui-queue-status`
- The job has already completed (it's in history, not in queue)
- You want to clear **all** history (this cancels one job at a time)

## Usage

```bash
python3 scripts/run.py <prompt-id>
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `prompt_id` | Yes | The prompt ID of the job to cancel |

### Examples

```bash
# Cancel a specific job
python3 scripts/run.py "abc123-def456-789"
```

### Output

JSON object with cancellation result:
```json
{
  "status": "success",
  "prompt_id": "abc123-def456-789",
  "message": "Job cancelled"
}
```

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/queue` | Delete job from queue | JSON with prompt ID to delete |
| `$COMFY_URL/interrupt` | Interrupt currently running job | POST request |
