from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class AuditEntry:
    event: str
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLogger:
    def __init__(self, log_path: Path) -> None:
        self._log_path = log_path
        self._log_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, entry: AuditEntry) -> None:
        with self._log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{entry.timestamp.isoformat()} | {entry.event} | {entry.message}\n")

    def write_many(self, entries: Iterable[AuditEntry]) -> None:
        for entry in entries:
            self.write(entry)
