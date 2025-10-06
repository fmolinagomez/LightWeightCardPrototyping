import re


def slugify(value: str) -> str:
    """Convert arbitrary text into a filesystem-friendly slug."""
    value = (value or '').strip()
    value = re.sub(r'\s+', '_', value)
    value = re.sub(r'[^A-Za-z0-9_-]', '', value)
    return value or 'card'
