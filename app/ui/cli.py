from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from app.app.use_cases import HashFilesUseCase, HashRequest, ScanClipsUseCase, ScanRequest
from app.domain.models import VideoClip
from app.infra.audit_log import AuditEntry, AuditLogger
from app.infra.clip_exporter import ClipExporter, create_evidence_package
from app.infra.clip_scanner import FileSystemClipScanner
from app.infra.hash_calculator import Sha256HashCalculator
from app.infra.scan_cache import ScanCache
from app.infra.time_utils import to_timezone


def build_scanner(root: Path) -> FileSystemClipScanner:
    cache_path = root / ".mtv_cache.sqlite"
    cache = ScanCache(cache_path)
    return FileSystemClipScanner(cache=cache)


def run_scan(root: Path, timezone_name: str) -> tuple[list[VideoClip], str]:
    scanner = build_scanner(root)
    use_case = ScanClipsUseCase(scanner)
    report = use_case.execute(ScanRequest(root=root, timezone_name=timezone_name))
    clips: list[VideoClip] = []
    for index in report.camera_indexes:
        clips.extend(index.clips)
    summary = (
        f"Zeskanowano: {report.total_files} plików, "
        f"wideo: {report.candidate_video_files}, "
        f"klipy: {report.indexed_clips}, "
        f"pominiete: {len(report.skipped)}, "
        f"błędy: {len(report.errors)}"
    )
    return clips, summary


def list_cameras(root: Path, timezone_name: str) -> None:
    scanner = build_scanner(root)
    report = ScanClipsUseCase(scanner).execute(ScanRequest(root=root, timezone_name=timezone_name))
    for index in report.camera_indexes:
        print(index.camera_label)


def list_clips(root: Path, timezone_name: str, camera: str) -> None:
    scanner = build_scanner(root)
    report = ScanClipsUseCase(scanner).execute(ScanRequest(root=root, timezone_name=timezone_name))
    for index in report.camera_indexes:
        if index.camera_label == camera:
            for clip in index.clips:
                print(f"{clip.start_time.isoformat()} -> {clip.end_time.isoformat()} | {clip.path}")
            return
    print(f"Brak kamery: {camera}")


def clip_at(root: Path, timezone_name: str, timestamp: str) -> None:
    scanner = build_scanner(root)
    report = ScanClipsUseCase(scanner).execute(ScanRequest(root=root, timezone_name=timezone_name))
    moment = to_timezone(datetime.fromisoformat(timestamp), timezone_name)
    for index in report.camera_indexes:
        clip = index.clip_for_time(moment)
        if clip:
            print(f"{index.camera_label}: {clip.path}")


def export_evidence(
    root: Path,
    timezone_name: str,
    camera: str,
    start: str,
    end: str,
    output_dir: Path,
) -> None:
    scanner = build_scanner(root)
    report = ScanClipsUseCase(scanner).execute(ScanRequest(root=root, timezone_name=timezone_name))
    start_time = to_timezone(datetime.fromisoformat(start), timezone_name)
    end_time = to_timezone(datetime.fromisoformat(end), timezone_name)

    selected: VideoClip | None = None
    for index in report.camera_indexes:
        if index.camera_label != camera:
            continue
        selected = index.clip_for_time(start_time)
        break

    if selected is None:
        raise SystemExit("Nie znaleziono klipu w podanym zakresie.")

    output_dir.mkdir(parents=True, exist_ok=True)
    exported_clip_path = output_dir / selected.path.name

    offset_seconds = (start_time - selected.start_time).total_seconds()
    duration_seconds = (end_time - start_time).total_seconds()

    exporter = ClipExporter()
    try:
        exporter.export_segment(selected.path, exported_clip_path, offset_seconds, duration_seconds)
        export_note = "Wyeksportowano fragment przez ffmpeg"
    except RuntimeError:
        exported_clip_path.write_bytes(selected.path.read_bytes())
        export_note = "ffmpeg niedostępny, zapisano cały plik"

    hash_report = HashFilesUseCase(Sha256HashCalculator()).execute(
        HashRequest(paths=(exported_clip_path,))
    )

    metadata = {
        "camera": camera,
        "start": start_time.isoformat(),
        "end": end_time.isoformat(),
        "offset_seconds": offset_seconds,
        "duration_seconds": duration_seconds,
        "source": str(selected.path),
        "exported": str(exported_clip_path),
    }

    audit_entries = [
        AuditEntry(event="evidence_export", message=export_note),
        AuditEntry(event="evidence_export", message=f"Hash: {hash_report.entries[0].sha256}"),
    ]

    create_evidence_package(
        output_dir=output_dir,
        clip_path=exported_clip_path,
        hash_report=hash_report,
        metadata=metadata,
        audit_entries=audit_entries,
    )

    logger = AuditLogger(output_dir / "audit.log")
    logger.write(AuditEntry(event="scan_summary", message="Pakiet dowodowy utworzony"))

    print(f"Pakiet zapisano w {output_dir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MTV - Modular Timeline Viewer CLI")
    parser.add_argument("--root", type=Path, required=True, help="Katalog z nagraniami")
    parser.add_argument("--timezone", default="Europe/Warsaw", help="Strefa czasowa")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("scan", help="Skanuj katalog")

    subparsers.add_parser("list-cameras", help="Lista kamer")

    list_clips_parser = subparsers.add_parser("list-clips", help="Lista klipów dla kamery")
    list_clips_parser.add_argument("--camera", required=True)

    clip_at_parser = subparsers.add_parser("clip-at", help="Znajdź klip dla czasu")
    clip_at_parser.add_argument("--timestamp", required=True, help="ISO datetime")

    evidence_parser = subparsers.add_parser("evidence", help="Eksportuj pakiet dowodowy")
    evidence_parser.add_argument("--camera", required=True)
    evidence_parser.add_argument("--start", required=True, help="ISO datetime")
    evidence_parser.add_argument("--end", required=True, help="ISO datetime")
    evidence_parser.add_argument("--output", type=Path, required=True)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "scan":
        _, summary = run_scan(args.root, args.timezone)
        print(summary)
    elif args.command == "list-cameras":
        list_cameras(args.root, args.timezone)
    elif args.command == "list-clips":
        list_clips(args.root, args.timezone, args.camera)
    elif args.command == "clip-at":
        clip_at(args.root, args.timezone, args.timestamp)
    elif args.command == "evidence":
        export_evidence(args.root, args.timezone, args.camera, args.start, args.end, args.output)
    else:
        raise SystemExit("Nieznana komenda")


if __name__ == "__main__":
    main()
