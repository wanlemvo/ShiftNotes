from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
FINAL_PROJECT_DIR = ROOT / "final_project"
ENV_PATH = FINAL_PROJECT_DIR / ".env"
ALT_ENV_PATH = FINAL_PROJECT_DIR / "final_project.env"


@dataclass(frozen=True)
class Settings:
    jotform_api_key: str
    jotform_form_id: str


@dataclass(frozen=True)
class GroqSettings:
    api_key: str
    model: str = "openai/gpt-oss-20b"


def _read_env_file(path: Path = ENV_PATH) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_settings(path: Path = ENV_PATH) -> Settings:
    env_path = path
    if not env_path.exists() and path == ENV_PATH:
        env_path = ALT_ENV_PATH

    values = _read_env_file(env_path)
    api_key = values.get("JOTFORM_API_KEY", "")
    form_id = values.get("JOTFORM_FORM_ID", "")

    missing = []
    if not api_key:
        missing.append("JOTFORM_API_KEY")
    if not form_id:
        missing.append("JOTFORM_FORM_ID")
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            f"Missing {joined}. Copy final_project/.env.example to final_project/.env "
            "or final_project/final_project.env "
            "and fill in your JotForm credentials."
        )

    return Settings(jotform_api_key=api_key, jotform_form_id=form_id)


def load_groq_settings(path: Path = ENV_PATH) -> GroqSettings:
    env_path = path
    if not env_path.exists() and path == ENV_PATH:
        env_path = ALT_ENV_PATH

    values = _read_env_file(env_path)
    api_key = values.get("GROQ_API_KEY", "")
    model = values.get("GROQ_MODEL", "openai/gpt-oss-20b")
    if not api_key:
        raise RuntimeError(
            "Missing GROQ_API_KEY. Add it to final_project/.env. "
            "Do not commit that file."
        )
    return GroqSettings(api_key=api_key, model=model)
