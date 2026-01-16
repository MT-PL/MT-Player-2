# MT-Player-2

ChronoView (MTV — Modular Timeline Viewer) is a Windows-first offline forensic CCTV review application.

## Architecture

The project follows Clean Architecture with strict boundaries:

- `app/domain`: Entities, value objects, and interfaces.
- `app/app`: Use cases that orchestrate domain workflows.
- `app/infra`: Concrete implementations (OCR, ffprobe, hashing, VLC).
- `app/ui`: PySide6 widgets and view models.

## Status

This repository currently defines the core domain models and use cases. Infrastructure adapters and UI components are implemented incrementally.
