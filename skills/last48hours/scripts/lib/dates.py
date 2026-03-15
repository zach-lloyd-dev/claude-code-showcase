"""Date utilities for last48hours skill (48-hour window focus)."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple


def get_date_range(hours: int = 48) -> Tuple[str, str]:
    """Get the date range for the last N hours.

    Returns:
        Tuple of (from_date, to_date) as YYYY-MM-DD strings.
        Note: uses dates not datetimes since source APIs work with dates.
    """
    now = datetime.now(timezone.utc)
    from_dt = now - timedelta(hours=hours)
    return from_dt.date().isoformat(), now.date().isoformat()


def get_datetime_range(hours: int = 48) -> Tuple[datetime, datetime]:
    """Get exact datetime range for the last N hours."""
    now = datetime.now(timezone.utc)
    return now - timedelta(hours=hours), now


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse a date string in various formats."""
    if not date_str:
        return None

    # Try Unix timestamp
    try:
        ts = float(date_str)
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except (ValueError, TypeError):
        pass

    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y%m%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def hours_ago(date_str: Optional[str]) -> Optional[float]:
    """Calculate how many hours ago a date/datetime is."""
    if not date_str:
        return None
    dt = parse_date(date_str)
    if not dt:
        return None
    now = datetime.now(timezone.utc)
    delta = now - dt
    return delta.total_seconds() / 3600


def hours_ago_label(h: Optional[float]) -> str:
    """Human-readable label for hours ago."""
    if h is None:
        return "unknown"
    if h < 1:
        return f"{int(h * 60)}m ago"
    if h < 24:
        return f"{int(h)}h ago"
    days = h / 24
    return f"{days:.1f}d ago"


def recency_score(date_str: Optional[str], max_hours: int = 48) -> int:
    """Calculate recency score (0-100) for 48-hour window.

    0 hours ago = 100, max_hours ago = 0, clamped.
    """
    h = hours_ago(date_str)
    if h is None:
        return 0
    if h < 0:
        return 100
    if h >= max_hours:
        return 0
    return int(100 * (1 - h / max_hours))


def is_within_window(date_str: Optional[str], hours: int = 48) -> bool:
    """Check if a date is within the last N hours."""
    h = hours_ago(date_str)
    if h is None:
        return False
    return 0 <= h <= hours


def get_date_confidence(date_str: Optional[str], from_date: str, to_date: str) -> str:
    """Determine confidence level for a date."""
    if not date_str:
        return "low"
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        start = datetime.strptime(from_date, "%Y-%m-%d").date()
        end = datetime.strptime(to_date, "%Y-%m-%d").date()
        if start <= dt <= end:
            return "high"
        return "low"
    except ValueError:
        return "low"
