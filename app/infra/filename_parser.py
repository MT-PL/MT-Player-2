from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from app.infra.time_utils import to_timezone


@dataclass(frozen=True)
class FilenameParseResult:
    camera_label: str
    timestamp: datetime


_DATETIME_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(?P<date>\d{4}[.-]?\d{2}[.-]?\d{2})[T_\- ]?(?P<time>\d{2}[.-]?\d{2}[.-]?\d{2})"
    ),
    re.compile(r"(?P<date>\d{8})(?P<time>\d{6})"),
)


def parse_timestamp_from_name(path: Path, timezone_name: str) -> Optional[FilenameParseResult]:
    stem = path.stem
    for pattern in _DATETIME_PATTERNS:
        match = pattern.search(stem)
        if not match:
            continue
        date_part = match.group("date")
        time_part = match.group("time")
        digits = re.sub(r"\D", "", f"{date_part}{time_part}")
        if len(digits) != 14:
            continue
        timestamp = datetime.strptime(digits, "%Y%m%d%H%M%S")
        timestamp = to_timezone(timestamp, timezone_name)
        camera_label = _extract_camera_label(stem, match.start())
        return FilenameParseResult(camera_label=camera_label, timestamp=timestamp)
    return None


def _extract_camera_label(stem: str, match_start: int) -> str:
    if match_start > 0:
        candidate = stem[:match_start]
    else:
        candidate = stem
    candidate = re.sub(r"[_\-]+$", "", candidate)
    candidate = candidate.strip()
    if not candidate:
        return "Camera"
    return candidate


def supported_extensions() -> Iterable[str]:
    return {
        ".mp4",
        ".mkv",
        ".avi",
        ".ts",
        ".mpg",
        ".mpeg",
        ".mov",
        ".m2ts",
        ".vob",
        ".wmv",
    }
