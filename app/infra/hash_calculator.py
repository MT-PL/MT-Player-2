from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

from app.domain.interfaces import HashCalculator
from app.domain.models import HashReport, HashReportEntry


class Sha256HashCalculator(HashCalculator):
    def compute_hashes(self, paths: Iterable[Path]) -> HashReport:
        entries: list[HashReportEntry] = []
        for path in paths:
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            entries.append(HashReportEntry(path=path, sha256=digest.hexdigest()))
        return HashReport(entries=tuple(entries))
