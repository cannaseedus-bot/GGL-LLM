# K'uhul PoC (Python)

## 1) Folder role
Python proof-of-concept event-driven UI/state engine with command handling, state snapshots, session logging, and SVG rendering.

## 2) Current maturity/status
**PoC (executable)**: runnable CLI and core modules exist for creating/replaying simple UI state transitions and exporting SVG outputs.

## 3) Key entry points
- `kuhul_poc/cli.py`
  - Main command-line entry for `create`, `theme`, `export-svg`, and `replay`.
- `kuhul_poc/engine.py`
  - Command application and event/state transition logic.
- `kuhul_poc/state.py`
  - In-memory state model.
- `kuhul_poc/bus.py`, `kuhul_poc/session_log.py`
  - Event bus and JSONL log persistence.
- `kuhul_poc/svg_renderer.py`
  - SVG export rendering.
- `kuhul_poc/schemas/*.json`
  - Command/event schema contracts.

## 4) Relationship to other folders
- Represents a practical Python-side execution PoC complementary to the more spec/verification-oriented folders.
- Can be used to generate concrete command/event traces that bridge tooling or future runtimes can validate against.

## 5) Minimal usage/dev notes
- Run from repo root, e.g.:
  - `python -m kuhul_poc.cli create --component button --text "Hello"`
  - `python -m kuhul_poc.cli theme dark`
  - `python -m kuhul_poc.cli replay`
- Outputs default to `out/` with per-session command/event logs and SVG artifacts.
- JSON schemas in `schemas/` document expected command/event payload shapes.
