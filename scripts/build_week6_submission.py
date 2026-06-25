from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PACKAGE_NAME = "ShiftNotes_Week6_LangGraph_Checkpoint"
STAGING = DIST / PACKAGE_NAME
ZIP_PATH = DIST / f"{PACKAGE_NAME}.zip"

FILES = {
    ROOT / "final_project" / "WEEK6_SUBMISSION_README.md": STAGING / "README.md",
    ROOT / "final_project" / "WEEK6_ARCHITECTURE.md": STAGING / "ARCHITECTURE.md",
    ROOT / "final_project" / "week6_requirements.txt": STAGING / "requirements.txt",
    ROOT / "final_project" / ".env.example": STAGING / "final_project" / ".env.example",
    ROOT / "tests" / "test_jotform_normalize.py": STAGING / "tests" / "test_jotform_normalize.py",
    ROOT / "tests" / "test_langgraph_workflow.py": STAGING / "tests" / "test_langgraph_workflow.py",
}

DIRECTORIES = {
    ROOT / "final_project" / "src" / "shiftnotes": STAGING / "final_project" / "src" / "shiftnotes",
    ROOT / "final_project" / "data" / "demo": STAGING / "final_project" / "data" / "demo",
    ROOT / "final_project" / "evidence" / "week6": STAGING / "evidence",
}


def build() -> Path:
    DIST.mkdir(parents=True, exist_ok=True)
    if STAGING.exists():
        shutil.rmtree(STAGING)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    for source, destination in FILES.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    for source, destination in DIRECTORIES.items():
        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(STAGING.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(DIST))

    return ZIP_PATH


if __name__ == "__main__":
    print(build())
