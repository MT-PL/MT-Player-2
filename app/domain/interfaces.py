from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, Protocol

from app.domain.models import HashReport, ScanReport


@dataclass(frozen=True)
class ScanProgress:
    processed: int
    total: int
    message: str


class ClipScanner(Protocol):
    def scan(self, root: Path, timezone_name: str) -> ScanReport:
        ...

    def scan_with_progress(
        self,
        root: Path,
        timezone_name: str,
        progress_callback: Callable[[ScanProgress], None],
        should_cancel: Callable[[], bool],
    ) -> ScanReport:
        ...


class HashCalculator(Protocol):
    def compute_hashes(self, paths: Iterable[Path]) -> HashReport:
        ...


class Clock(Protocol):
    def now(self) -> datetime:
        ...
