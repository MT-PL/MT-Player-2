from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional


class GapPolicy(str, Enum):
    STRICT = "strict"
    CLAMP = "clamp"


@dataclass(frozen=True)
class VideoClip:
    path: Path
    camera_label: str
    start_time: datetime
    end_time: datetime
    duration: timedelta

    def contains(self, moment: datetime) -> bool:
        return self.start_time <= moment <= self.end_time


@dataclass(frozen=True)
class CameraClipIndex:
    camera_label: str
    clips: tuple[VideoClip, ...]

    def clip_for_time(self, moment: datetime) -> Optional[VideoClip]:
        for clip in self.clips:
            if clip.contains(moment):
                return clip
        return None


@dataclass(frozen=True)
class ScanSkippedItem:
    path: Path
    reason: str


@dataclass(frozen=True)
class ScanErrorItem:
    path: Optional[Path]
    message: str
    context: Optional[str] = None


@dataclass(frozen=True)
class ScanReport:
    total_files: int
    candidate_video_files: int
    indexed_clips: int
    camera_indexes: tuple[CameraClipIndex, ...]
    skipped: tuple[ScanSkippedItem, ...] = field(default_factory=tuple)
    errors: tuple[ScanErrorItem, ...] = field(default_factory=tuple)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: Optional[datetime] = None

    @property
    def duration(self) -> Optional[timedelta]:
        if self.finished_at is None:
            return None
        return self.finished_at - self.started_at


@dataclass(frozen=True)
class HashReportEntry:
    path: Path
    sha256: str


@dataclass(frozen=True)
class HashReport:
    entries: tuple[HashReportEntry, ...]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_rows(self) -> Iterable[tuple[str, str]]:
        for entry in self.entries:
            yield str(entry.path), entry.sha256
