import re


def normalize_line_endings(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def stable_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
    return slug or "document"


def unique_sorted(values: list[str]) -> list[str]:
    seen: set[str] = set()
    results: list[str] = []
    for value in values:
        cleaned = value.strip()
        key = cleaned.upper()
        if cleaned and key not in seen:
            seen.add(key)
            results.append(cleaned.upper())
    return sorted(results)
