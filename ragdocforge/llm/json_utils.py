import json
from typing import Any

from pydantic import BaseModel, ValidationError


def extract_first_json_object(text: str) -> dict | list | None:
    cleaned = _strip_markdown_fence(text.strip())
    for start, opening, closing in _json_starts(cleaned):
        depth = 0
        in_string = False
        escape = False
        for index in range(start, len(cleaned)):
            char = cleaned[index]
            if escape:
                escape = False
                continue
            if char == "\\":
                escape = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == opening:
                depth += 1
            elif char == closing:
                depth -= 1
                if depth == 0:
                    candidate = cleaned[start : index + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        break
    return None


def validate_or_warn(model_cls: type[BaseModel], payload: Any, warnings: list[str]) -> BaseModel | None:
    try:
        return model_cls.model_validate(payload)
    except ValidationError as exc:
        warnings.append(f"{model_cls.__name__} validation failed: {exc.errors()[0]['msg']}")
        return None


def _strip_markdown_fence(text: str) -> str:
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text


def _json_starts(text: str) -> list[tuple[int, str, str]]:
    starts: list[tuple[int, str, str]] = []
    for index, char in enumerate(text):
        if char == "{":
            starts.append((index, "{", "}"))
        elif char == "[":
            starts.append((index, "[", "]"))
    return starts
