from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "final_project" / "data" / "raw"
PROCESSED_DIR = ROOT / "final_project" / "data" / "processed"
BRIEFINGS_DIR = ROOT / "final_project" / "data" / "briefings"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def reports_path() -> Path:
    return PROCESSED_DIR / "reports.json"


def save_raw_submissions(data: dict) -> Path:
    path = RAW_DIR / "jotform_submissions.json"
    write_json(path, data)
    return path


def save_normalized_reports(reports: list[dict]) -> Path:
    path = reports_path()
    write_json(path, reports)
    return path


def load_normalized_reports(path: Path | None = None) -> list[dict]:
    target = path or reports_path()
    return read_json(target)


def save_analysis(data: dict) -> Path:
    path = PROCESSED_DIR / "weekly_analysis.json"
    write_json(path, data)
    return path


def save_briefing(text: str, filename: str = "weekly_briefing.md") -> Path:
    path = BRIEFINGS_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
