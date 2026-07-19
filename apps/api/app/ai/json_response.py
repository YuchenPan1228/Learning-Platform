"""Helpers for parsing structured JSON from model chat responses."""

from __future__ import annotations

import json
import re

_FENCE_RE = re.compile(
    r"^\s*```(?:json)?\s*(.*?)\s*```\s*$",
    re.DOTALL | re.IGNORECASE,
)


def loads_model_json(content: str) -> object:
    """Parse JSON from a model response, tolerating markdown fences."""
    stripped = content.strip()
    if not stripped:
        raise json.JSONDecodeError("Expecting value", content, 0)

    candidates = [stripped]
    fenced = _FENCE_RE.match(stripped)
    if fenced is not None:
        candidates.append(fenced.group(1).strip())

    # Fall back to the outermost object/array when prose wraps the payload.
    start_obj = stripped.find("{")
    end_obj = stripped.rfind("}")
    if start_obj != -1 and end_obj > start_obj:
        candidates.append(stripped[start_obj : end_obj + 1])
    start_arr = stripped.find("[")
    end_arr = stripped.rfind("]")
    if start_arr != -1 and end_arr > start_arr:
        candidates.append(stripped[start_arr : end_arr + 1])

    seen: set[str] = set()
    last_error: json.JSONDecodeError | None = None
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc

    if last_error is not None:
        raise last_error
    raise json.JSONDecodeError("Expecting value", content, 0)
