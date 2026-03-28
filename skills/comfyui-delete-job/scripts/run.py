#!/usr/bin/env python3
"""Delete/cancel a ComfyUI generation job from the queue."""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from comfy_lib import check_env, make_request, COMFY_URL


def delete_job(prompt_id):
    """Cancel a job by removing it from the queue or interrupting it."""
    # First check if the job is currently running
    queue_data = make_request(f"{COMFY_URL}/queue")
    running = queue_data.get("queue_running", [])
    pending = queue_data.get("queue_pending", [])

    is_running = False
    for job in running:
        if len(job) > 1 and job[1] == prompt_id:
            is_running = True
            break

    is_pending = False
    for job in pending:
        if len(job) > 1 and job[1] == prompt_id:
            is_pending = True
            break

    if is_running:
        # Interrupt the currently running job
        make_request(f"{COMFY_URL}/interrupt", data={}, method="POST")
        return {
            "status": "success",
            "prompt_id": prompt_id,
            "message": "Running job interrupted",
        }
    elif is_pending:
        # Delete from pending queue
        make_request(
            f"{COMFY_URL}/queue",
            data={"delete": [prompt_id]},
            method="POST",
        )
        return {
            "status": "success",
            "prompt_id": prompt_id,
            "message": "Pending job cancelled",
        }
    else:
        return {
            "status": "warning",
            "prompt_id": prompt_id,
            "message": "Job not found in running or pending queue (may have already completed)",
        }


def main():
    parser = argparse.ArgumentParser(description="Cancel a ComfyUI generation job")
    parser.add_argument("prompt_id", help="The prompt ID of the job to cancel")
    args = parser.parse_args()

    check_env()

    result = delete_job(args.prompt_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
