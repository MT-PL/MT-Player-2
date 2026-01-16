from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from app.domain.models import VideoClip


@dataclass(frozen=True)
class CachedClip:
    path: Path
    camera_label: str
    start_time: datetime
    duration_seconds: float


class ScanCache:
    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self._database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS clip_cache (
                    path TEXT PRIMARY KEY,
                    size INTEGER NOT NULL,
                    mtime REAL NOT NULL,
                    camera_label TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    duration_seconds REAL NOT NULL,
                    timezone_name TEXT NOT NULL
                )
                """
            )

    def load(self, path: Path, timezone_name: str) -> Optional[CachedClip]:
        stat = path.stat()
        with sqlite3.connect(self._database_path) as connection:
            cursor = connection.execute(
                """
                SELECT camera_label, start_time, duration_seconds
                FROM clip_cache
                WHERE path = ? AND size = ? AND mtime = ? AND timezone_name = ?
                """,
                (str(path), stat.st_size, stat.st_mtime, timezone_name),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        camera_label, start_time, duration_seconds = row
        return CachedClip(
            path=path,
            camera_label=camera_label,
            start_time=datetime.fromisoformat(start_time),
            duration_seconds=duration_seconds,
        )

    def save(self, clip: VideoClip, timezone_name: str) -> None:
        stat = clip.path.stat()
        with sqlite3.connect(self._database_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO clip_cache (
                    path, size, mtime, camera_label, start_time, duration_seconds, timezone_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(clip.path),
                    stat.st_size,
                    stat.st_mtime,
                    clip.camera_label,
                    clip.start_time.isoformat(),
                    clip.duration.total_seconds(),
                    timezone_name,
                ),
            )

    def save_many(self, clips: Iterable[VideoClip], timezone_name: str) -> None:
        for clip in clips:
            self.save(clip, timezone_name)
