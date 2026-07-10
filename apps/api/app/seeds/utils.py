def slugify(name: str) -> str:
    normalized = name.lower().replace("&", "and").replace("'", "").replace("+", "plus")
    return "-".join(part for part in normalized.split() if part)
