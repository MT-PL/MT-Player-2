from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class DurationResult:
    duration_seconds: float


class DurationProbe:
    def probe(self, path: Path) -> Optional[DurationResult]:
        raise NotImplementedError


class FFprobeDurationProbe(DurationProbe):
    def __init__(self, executable: str = "ffprobe") -> None:
        self._executable = executable

    def probe(self, path: Path) -> Optional[DurationResult]:
        try:
            completed = subprocess.run(
                [
                    self._executable,
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "json",
                    str(path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
        try:
            payload = json.loads(completed.stdout)
            duration = float(payload["format"]["duration"])
        except (KeyError, ValueError, TypeError, json.JSONDecodeError):
            return None
        return DurationResult(duration_seconds=duration)
