from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def to_timezone(timestamp: datetime, timezone_name: str) -> datetime:
    timezone = ZoneInfo(timezone_name)
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=timezone)
    return timestamp.astimezone(timezone)
