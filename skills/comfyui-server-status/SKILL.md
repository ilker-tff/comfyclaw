---
name: comfyui-server-status
description: "Check ComfyUI server health, system stats, GPU info, and queue state. Use this when the user asks if the server is up, wants to know GPU/memory usage, or before starting a batch of work to verify the server is healthy and available."
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
            "server",
            "health",
            "status",
            "gpu",
            "system",
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

# ComfyUI Server Status

Check server health, GPU info, and system statistics.

## When to use this skill

- User asks "is the server up?", "is it running?", "server status"
- Before starting a batch of work — verify server is healthy
- To check GPU memory, system resources
- When generation seems slow — check if server is overloaded

## When NOT to use this skill

- To check a specific job's progress → use `comfyui-progress`
- To see queue details → use `comfyui-queue-status`
- To check available models → use `comfyui-validate-models`

## Usage

```bash
python3 scripts/run.py
```

## Confirm before running

No confirmation needed — this is a read-only health check.

## External endpoints

| URL | Purpose | Data sent |
|-----|---------|-----------|
| `$COMFY_URL/system_stats` | System/GPU info | None |
| `$COMFY_URL/queue` | Queue state | None |
