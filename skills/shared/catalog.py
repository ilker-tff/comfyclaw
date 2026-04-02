#!/usr/bin/env python3
"""Workflow catalog: search, lookup, and load curated ComfyUI workflow JSONs."""

import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_CATALOG_PATH = os.path.join(_HERE, "catalog.json")
_SKILLS_ROOT = os.path.dirname(_HERE)  # parent of shared/ = skills/


def _load_catalog():
    with open(_CATALOG_PATH, "r") as f:
        return json.load(f)["workflows"]


def list_workflows(family=None, tag=None):
    """List available workflows, optionally filtered by family or tag."""
    workflows = _load_catalog()
    if family:
        workflows = [w for w in workflows if w["family"] == family]
    if tag:
        workflows = [w for w in workflows if tag in w["tags"]]
    return workflows


def find_workflow(workflow_id):
    """Find a workflow by its ID. Returns the catalog entry or None."""
    for w in _load_catalog():
        if w["id"] == workflow_id:
            return w
    return None


def search_workflows(query):
    """Search workflows by matching query terms against name, family, and tags."""
    query_terms = query.lower().split()
    results = []
    for w in _load_catalog():
        searchable = f"{w['name']} {w['family']} {' '.join(w['tags'])}".lower()
        score = sum(1 for term in query_terms if term in searchable)
        if score > 0:
            results.append((score, w))
    results.sort(key=lambda x: -x[0])
    return [w for _, w in results]


def load_workflow_json(workflow_id=None, file_path=None):
    """Load a workflow JSON file by catalog ID or direct file path.

    Returns (workflow_dict, defaults_dict).
    defaults_dict is empty if loaded by file path.
    """
    if workflow_id:
        entry = find_workflow(workflow_id)
        if not entry:
            raise ValueError(f"Unknown workflow ID: {workflow_id}")
        path = os.path.join(_SKILLS_ROOT, entry["file"])
        defaults = entry.get("defaults", {})
    elif file_path:
        path = file_path
        defaults = {}
    else:
        raise ValueError("Provide either workflow_id or file_path")

    with open(path, "r") as f:
        workflow = json.load(f)
    return workflow, defaults


def apply_overrides(workflow, overrides):
    """Apply parameter overrides to a workflow template.

    Replaces {{placeholder}} strings in the workflow with actual values.
    Also handles numeric types: if the template value is a string like "{{width}}"
    and the override is an int/float, the value is set directly.
    """
    workflow_str = json.dumps(workflow)

    for key, value in overrides.items():
        placeholder = "{{" + key + "}}"
        if placeholder in workflow_str:
            if isinstance(value, (int, float)):
                # Replace "{{key}}" (with quotes) with the raw number
                workflow_str = workflow_str.replace(f'"{placeholder}"', str(value))
                # Also replace without quotes in case it appears unquoted
                workflow_str = workflow_str.replace(placeholder, str(value))
            elif isinstance(value, bool):
                workflow_str = workflow_str.replace(f'"{placeholder}"', str(value).lower())
            else:
                workflow_str = workflow_str.replace(placeholder, str(value))

    return json.loads(workflow_str)
