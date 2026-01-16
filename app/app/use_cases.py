from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.domain.interfaces import ClipScanner, HashCalculator
from app.domain.models import HashReport, ScanReport


@dataclass(frozen=True)
class ScanRequest:
    root: Path
    timezone_name: str = "Europe/Warsaw"


class ScanClipsUseCase:
    def __init__(self, scanner: ClipScanner) -> None:
        self._scanner = scanner

    def execute(self, request: ScanRequest) -> ScanReport:
        return self._scanner.scan(request.root, request.timezone_name)


@dataclass(frozen=True)
class HashRequest:
    paths: tuple[Path, ...]


class HashFilesUseCase:
    def __init__(self, calculator: HashCalculator) -> None:
        self._calculator = calculator

    def execute(self, request: HashRequest) -> HashReport:
        return self._calculator.compute_hashes(request.paths)


class HashingPlan:
    def __init__(self, paths: Iterable[Path]) -> None:
        self._paths = tuple(paths)

    def to_request(self) -> HashRequest:
        return HashRequest(paths=self._paths)
