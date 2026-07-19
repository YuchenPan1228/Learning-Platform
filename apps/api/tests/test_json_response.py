import json

import pytest
from app.ai.json_response import loads_model_json


def test_loads_model_json_parses_plain_object() -> None:
    assert loads_model_json('{"a": 1}') == {"a": 1}


def test_loads_model_json_strips_markdown_fence() -> None:
    content = """```json
{"explanation": "ok", "hints": ["h"], "common_mistakes": []}
```"""
    assert loads_model_json(content)["explanation"] == "ok"


def test_loads_model_json_extracts_embedded_object() -> None:
    content = 'Here you go:\n{"explanation": "ok", "hints": ["h"], "common_mistakes": []}\nThanks'
    assert loads_model_json(content)["hints"] == ["h"]


def test_loads_model_json_rejects_empty() -> None:
    with pytest.raises(json.JSONDecodeError):
        loads_model_json("   ")
