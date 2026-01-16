# MT-Player-2

ChronoView (MTV — Modular Timeline Viewer) is a Windows-first offline forensic CCTV review application.

## Architecture

The project follows Clean Architecture with strict boundaries:

- `app/domain`: Entities, value objects, and interfaces.
- `app/app`: Use cases that orchestrate domain workflows.
- `app/infra`: Concrete implementations (OCR, ffprobe, hashing, VLC).
- `app/ui`: PySide6 widgets and view models.

## CLI (working MVP)

Run the CLI module with Python:

```bash
python -m app --root "D:/nagrania" scan
python -m app --root "D:/nagrania" list-cameras
python -m app --root "D:/nagrania" list-clips --camera "CAM1"
python -m app --root "D:/nagrania" clip-at --timestamp "2024-05-20T14:05:30"
python -m app --root "D:/nagrania" evidence --camera "CAM1" --start "2024-05-20T14:05:30" --end "2024-05-20T14:06:00" --output "D:/export"
```

The scanner uses filename timestamps (priority) and caches scan results in `.mtv_cache.sqlite` inside the root directory.

## Product requirements

See `docs/requirements.md` for the current product requirements captured from stakeholder input.

## Status

This repository currently defines the core domain models and use cases. Infrastructure adapters and UI components are implemented incrementally.
