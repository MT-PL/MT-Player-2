from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from app.domain.models import HashReport
from app.infra.audit_log import AuditEntry, AuditLogger


@dataclass(frozen=True)
class EvidencePackage:
    output_dir: Path
    clip_path: Path
    hash_report: HashReport
    metadata_path: Path
    audit_log_path: Path


class ClipExporter:
    def __init__(self, ffmpeg_executable: str = "ffmpeg") -> None:
        self._ffmpeg_executable = ffmpeg_executable

    def export_segment(
        self,
        input_path: Path,
        output_path: Path,
        start_offset_seconds: float,
        duration_seconds: float,
    ) -> None:
        if shutil.which(self._ffmpeg_executable) is None:
            raise RuntimeError("ffmpeg nie jest dostępny")
        safe_duration = max(0.0, duration_seconds)
        safe_start = max(0.0, start_offset_seconds)
        subprocess.run(
            [
                self._ffmpeg_executable,
                "-y",
                "-ss",
                f"{safe_start:.3f}",
                "-i",
                str(input_path),
                "-t",
                f"{safe_duration:.3f}",
                "-c",
                "copy",
                str(output_path),
            ],
            check=True,
            capture_output=True,
        )


def write_hash_report(report: HashReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("path,sha256\n")
        for path, digest in report.to_rows():
            handle.write(f"{path},{digest}\n")


def write_metadata(output_path: Path, payload: dict) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def create_evidence_package(
    output_dir: Path,
    clip_path: Path,
    hash_report: HashReport,
    metadata: dict,
    audit_entries: Iterable[AuditEntry],
) -> EvidencePackage:
    output_dir.mkdir(parents=True, exist_ok=True)
    hash_path = output_dir / "hashes.csv"
    metadata_path = output_dir / "metadata.json"
    audit_log_path = output_dir / "audit.log"

    write_hash_report(hash_report, hash_path)
    write_metadata(metadata_path, metadata)

    logger = AuditLogger(audit_log_path)
    logger.write_many(audit_entries)

    return EvidencePackage(
        output_dir=output_dir,
        clip_path=clip_path,
        hash_report=hash_report,
        metadata_path=metadata_path,
        audit_log_path=audit_log_path,
    )
