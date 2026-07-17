import hashlib
import json
from typing import Any


def compute_prompt_hash(
    *,
    prompt_template_version: str,
    prompt_payload: dict[str, Any] | str,
) -> str:
    """Hash prompt template version plus stable prompt payload for cache keys."""
    if isinstance(prompt_payload, str):
        serialized = prompt_payload
    else:
        serialized = json.dumps(prompt_payload, sort_keys=True, separators=(",", ":"))
    material = f"{prompt_template_version}\n{serialized}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()
