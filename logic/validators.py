"""Input checks shared by every module. Pure Python, no Flask."""
from datetime import date


def clean_text(value, field="Text", max_len=100):
    """Return the text without outer spaces, or raise ValueError if empty/too long."""
    value = (value or "").strip()
    if not value:
        raise ValueError(f"{field} cannot be empty.")
    if len(value) > max_len:
        raise ValueError(f"{field} must be at most {max_len} characters.")
    return value


def parse_date(value):
    """Turn 'YYYY-MM-DD' into a date, or raise ValueError."""
    try:
        return date.fromisoformat((value or "").strip())
    except ValueError:
        raise ValueError("Date must look like 2026-11-24.") from None
