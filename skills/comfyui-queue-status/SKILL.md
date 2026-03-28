---
name: comfyui-queue-status
description: "Check the ComfyUI job queue — how many jobs are currently running and pending. Use this to check if the server is busy before submitting new work, or to explain to the user why their generation might be slow (other jobs ahead in queue)."
homepage: https://github.com/ilker-tff/comfyclaw
metadata: {
    "openclaw": {
        "os": [
            "darwin",
            "linux"
        ],
        "requires": {
            "bins": [
                "python3"
            ],
            "env": [
                "COMFY_URL",
                "COMFY_AUTH_HEADER"
            ]
        },
        "tags": [
            "queue",
            "status",
            "monitoring",
            "jobs",
            "comfyui"
        ],
        "category": "utility",
        "input_type": "none",
        "output_type": "text/json",
        "output_can_feed_into": [],
        "accepts_input_from": [],
        "priority": 60,
        "files": [
            "scripts/*"
        ]
    }
}
---

# ComfyUI Queue Status

Check running and pending jobs in the ComfyUI queue.

## When to use this skill

- Before submitting work, to check if the server is busy
- To explain why generation is taking longer than expected
- When the user asks "is anything running?" or "how busy is the server?"

## When NOT to use this skill

- To check a specific job's progress → use `comfyui-progress`
- To check server health/GPU info → use `comfyui-server-status`

## Usage

```bash
python3 scripts/run.py
```

## Confirm before running

No confirmation needed — this is a read-only status check.

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/queue` | Queue state | None |
