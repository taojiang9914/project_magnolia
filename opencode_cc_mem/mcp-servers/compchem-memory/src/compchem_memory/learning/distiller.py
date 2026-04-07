"""Session distillation: extract learnings from session logs."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def distill_session(session_path: str) -> list[dict[str, Any]]:
    path = Path(session_path)
    if not path.exists():
        return []

    events = []
    with open(path) as f:
        for line in f:
            try:
                events.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue

    candidates = []

    error_resolution_pairs = _find_error_resolutions(events)
    for err, resolution in error_resolution_pairs:
        candidates.append(
            {
                "type": "error_resolution",
                "title": f"Resolved: {err[:80]}",
                "content": f"## Error\n{err}\n\n## Resolution\n{resolution}",
                "tags": ["error-resolution", "auto"],
                "source": "auto",
                "confidence": 0.8,
            }
        )

    non_default_params = _find_non_default_params(events)
    for param_info in non_default_params:
        candidates.append(
            {
                "type": "parameter_choice",
                "title": f"Non-default parameter: {param_info['param']}",
                "content": f"Tool: {param_info['tool']}\nParameter: {param_info['param']}\nValue: {param_info['value']}\nDefault: {param_info['default']}",
                "tags": ["parameter", param_info["tool"]],
                "source": "auto",
                "confidence": 0.6,
            }
        )

    return candidates


def _find_error_resolutions(events: list[dict[str, Any]]) -> list[tuple[str, str]]:
    pairs = []
    errors = {}
    for ev in events:
        etype = ev.get("event_type", "")
        if etype == "tool_error":
            tool = ev.get("tool", "unknown")
            error_msg = ev.get("error", "")
            errors[tool] = error_msg
        elif etype == "tool_success" and ev.get("tool") in errors:
            tool = ev.get("tool")
            pairs.append(
                (errors[tool], ev.get("result_summary", "Retried successfully"))
            )
            del errors[tool]
    return pairs


def _find_non_default_params(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    params = []
    for ev in events:
        if ev.get("event_type") == "tool_call" and ev.get("non_default_params"):
            for p in ev["non_default_params"]:
                params.append(p)
    return params
