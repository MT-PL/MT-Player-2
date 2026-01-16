from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from app.domain.interfaces import ClipScanner, ScanProgress
from app.domain.models import CameraClipIndex, ScanErrorItem, ScanReport, ScanSkippedItem, VideoClip
from app.infra.duration_probe import DurationProbe, FFprobeDurationProbe
from app.infra.filename_parser import parse_timestamp_from_name, supported_extensions
from app.infra.scan_cache import ScanCache


class FileSystemClipScanner(ClipScanner):
    def __init__(
        self,
        duration_probe: DurationProbe | None = None,
        cache: ScanCache | None = None,
    ) -> None:
        self._duration_probe = duration_probe or FFprobeDurationProbe()
        self._cache = cache

    def scan(self, root: Path, timezone_name: str) -> ScanReport:
        return self.scan_with_progress(root, timezone_name, lambda _: None, lambda: False)

    def scan_with_progress(
        self,
        root: Path,
        timezone_name: str,
        progress_callback: Callable[[ScanProgress], None],
        should_cancel: Callable[[], bool],
    ) -> ScanReport:
        if not root.exists():
            raise FileNotFoundError(f"Root directory not found: {root}")

        candidates = [path for path in root.rglob("*") if path.is_file()]
        total_files = len(candidates)
        video_extensions = {ext.lower() for ext in supported_extensions()}

        skipped: list[ScanSkippedItem] = []
        errors: list[ScanErrorItem] = []
        clips: list[VideoClip] = []
        processed = 0
        candidate_video_files = 0

        for path in candidates:
            if should_cancel():
                break
            processed += 1
            if processed % 25 == 0 or processed == total_files:
                progress_callback(
                    ScanProgress(
                        processed=processed,
                        total=total_files,
                        message=f"Przetwarzanie: {path.name}",
                    )
                )

            if path.suffix.lower() not in video_extensions:
                skipped.append(ScanSkippedItem(path=path, reason="Nieobsługiwane rozszerzenie"))
                continue
            candidate_video_files += 1

            cached_clip = self._cache.load(path, timezone_name) if self._cache else None
            if cached_clip is not None:
                clips.append(
                    VideoClip(
                        path=cached_clip.path,
                        camera_label=cached_clip.camera_label,
                        start_time=cached_clip.start_time,
                        end_time=cached_clip.start_time + timedelta(seconds=cached_clip.duration_seconds),
                        duration=timedelta(seconds=cached_clip.duration_seconds),
                    )
                )
                continue

            parsed = parse_timestamp_from_name(path, timezone_name)
            if parsed is None:
                skipped.append(ScanSkippedItem(path=path, reason="Brak znacznika czasu w nazwie pliku"))
                continue

            duration_result = self._duration_probe.probe(path)
            if duration_result is None:
                errors.append(
                    ScanErrorItem(path=path, message="Nie udało się odczytać długości klipu")
                )
                duration_seconds = 0.0
            else:
                duration_seconds = duration_result.duration_seconds
            duration = timedelta(seconds=duration_seconds)
            clip = VideoClip(
                path=path,
                camera_label=parsed.camera_label,
                start_time=parsed.timestamp,
                end_time=parsed.timestamp + duration,
                duration=duration,
            )
            clips.append(clip)
            if self._cache:
                self._cache.save(clip, timezone_name)

        camera_map: dict[str, list[VideoClip]] = defaultdict(list)
        for clip in clips:
            camera_map[clip.camera_label].append(clip)

        camera_indexes = tuple(
            CameraClipIndex(
                camera_label=camera_label,
                clips=tuple(sorted(items, key=lambda item: item.start_time, reverse=True)),
            )
            for camera_label, items in sorted(camera_map.items())
        )

        report = ScanReport(
            total_files=total_files,
            candidate_video_files=candidate_video_files,
            indexed_clips=len(clips),
            camera_indexes=camera_indexes,
            skipped=tuple(skipped),
            errors=tuple(errors),
            finished_at=datetime.now(timezone.utc),
        )
        return report
