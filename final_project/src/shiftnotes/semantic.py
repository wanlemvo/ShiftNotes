from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from shiftnotes.analysis import TEXT_FIELDS
from shiftnotes.baseline import detect_baseline_events


SemanticCategory = Literal[
    "food_shortage",
    "high_waste_or_overproduction",
    "dietary_or_allergy_question",
    "equipment_failure",
    "employee_recognition",
    "inventory_inconsistency",
    "register_disruption",
    "portion_complaint",
    "beverage_request",
    "sensitive_personnel_note",
    "other_operational_issue",
]
EvidenceField = Literal[
    "food_concerns_or_outages",
    "team_members_who_did_well",
    "guest_issues_for_the_day",
    "operational_notes",
]


class SemanticSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: SemanticCategory
    subject: str
    severity: Literal["low", "medium", "high"]
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_field: EvidenceField
    evidence_excerpt: str
    sensitive: bool
    rationale: str


class ReportSemanticResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_submission_id: str
    signals: list[SemanticSignal]


class SemanticBatchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reports: list[ReportSemanticResult]


class SemanticProvider(Protocol):
    model: str

    def extract(self, reports: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
        """Return a parsed response payload and provider metadata."""


@dataclass
class ExtractionRun:
    reports: list[dict[str, Any]]
    model: str
    batches: int = 0
    retries: int = 0
    fallback_batches: int = 0
    cache_hits: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)
    retry_events: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PROMPT_VERSION = "2026-06-22.2"

SYSTEM_PROMPT = """You extract source-backed operational signals from kiosk shift notes.
Use only the supplied free-text fields. Do not infer facts from ratings, counts, names,
or outside knowledge. Every signal must quote a short exact substring from one supplied
field. Return every input source_submission_id exactly once, even when signals is empty.
Use sensitive_personnel_note for ambiguous or potentially harmful personnel allegations.
Do not make disciplinary recommendations.

Category guidance:
- employee_recognition: any clearly positive description of a team member's performance,
  including noticing and resolving a prep problem. When praise is the main meaning, do not
  relabel the praised action as other_operational_issue.
- beverage_request: a guest asks for a beverage or additional beverage option.
- food_shortage: an item ran low, sold out, or lacked sufficient prep.
- high_waste_or_overproduction: prepared food remained or production exceeded demand.
- portion_complaint: a guest says a serving is too small or changed.
- other_operational_issue: use only when no more specific category applies."""

MODEL_PRICING_PER_MILLION = {
    "openai/gpt-oss-20b": {
        "input": 0.075,
        "output": 0.30,
    },
}


def report_payload(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_submission_id": str(report.get("source_submission_id", "")),
        "date": str(report.get("date", "")),
        "kiosk": str(report.get("kiosk", "")),
        **{field: str(report.get(field, "") or "") for field in TEXT_FIELDS},
    }


def report_hash(report: dict[str, Any], model: str) -> str:
    payload = {
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "report": report_payload(report),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def validate_semantic_response(
    payload: dict[str, Any],
    reports: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    parsed = SemanticBatchResponse.model_validate(payload)
    expected = {
        str(report.get("source_submission_id", "")): report
        for report in reports
    }
    returned_ids = [result.source_submission_id for result in parsed.reports]
    if len(returned_ids) != len(set(returned_ids)):
        raise ValueError("Semantic response contains duplicate source IDs.")
    if set(returned_ids) != set(expected):
        raise ValueError("Semantic response source IDs do not match the requested batch.")

    validated: list[dict[str, Any]] = []
    for result in parsed.reports:
        source = expected[result.source_submission_id]
        signals = []
        for signal in result.signals:
            source_text = str(source.get(signal.evidence_field, "") or "")
            if not signal.evidence_excerpt.strip():
                raise ValueError("Semantic evidence excerpts cannot be empty.")
            if signal.evidence_excerpt not in source_text:
                raise ValueError(
                    f"Unsupported evidence for {result.source_submission_id}: "
                    "excerpt is not present in the named source field."
                )
            signals.append(signal.model_dump())
        validated.append(
            {
                "source_submission_id": result.source_submission_id,
                "signals": signals,
            }
        )
    return validated


class GroqSemanticProvider:
    def __init__(
        self,
        api_key: str,
        model: str = "openai/gpt-oss-20b",
        client: Any | None = None,
    ) -> None:
        if client is None:
            try:
                from groq import Groq
            except ImportError as exc:
                raise RuntimeError(
                    "The groq package is not installed. Run python -m pip install -e ."
                ) from exc
            client = Groq(api_key=api_key)
        self.client = client
        self.model = model

    def extract(self, reports: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
        started = time.perf_counter()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {"reports": [report_payload(report) for report in reports]},
                        separators=(",", ":"),
                    ),
                },
            ],
            temperature=0,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "shift_note_semantic_batch",
                    "strict": True,
                    "schema": SemanticBatchResponse.model_json_schema(),
                },
            },
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Groq returned an empty response.")
        usage = getattr(response, "usage", None)
        metadata = {
            "latency_seconds": round(time.perf_counter() - started, 4),
            "prompt_tokens": int(getattr(usage, "prompt_tokens", 0) or 0),
            "completion_tokens": int(getattr(usage, "completion_tokens", 0) or 0),
            "total_tokens": int(getattr(usage, "total_tokens", 0) or 0),
        }
        return json.loads(content), metadata


class DeterministicFallbackProvider:
    model = "deterministic-fallback"

    CATEGORY_MAP = {
        "food_shortage:kung_pao_chicken": "food_shortage",
        "waste:high_unclaimed_lunches": "high_waste_or_overproduction",
        "guest_theme:dietary_or_allergy_question": "dietary_or_allergy_question",
        "operational_issue:equipment_failure": "equipment_failure",
        "recognition:maya_chen": "employee_recognition",
        "inventory:inconsistent_prep": "inventory_inconsistency",
        "cross_kiosk:register_disruption_week_7": "register_disruption",
        "cross_kiosk:portion_complaints_weeks_9_10": "portion_complaint",
        "guest_request:beverage_variety": "beverage_request",
        "sensitive_personnel:ambiguous_comment": "sensitive_personnel_note",
    }

    def extract(self, reports: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
        events = detect_baseline_events(reports)
        signals_by_id: dict[str, list[dict[str, Any]]] = {
            str(report["source_submission_id"]): [] for report in reports
        }
        lookup = {
            str(report["source_submission_id"]): report for report in reports
        }
        for event_category, records in events.items():
            category = self.CATEGORY_MAP.get(event_category)
            if not category:
                continue
            for record in records:
                source_id = str(record["source_submission_id"])
                report = lookup[source_id]
                field, evidence = fallback_evidence(report, category)
                signals_by_id[source_id].append(
                    {
                        "category": category,
                        "subject": event_category.split(":", 1)[1].replace("_", " "),
                        "severity": "medium",
                        "confidence": 1.0,
                        "evidence_field": field,
                        "evidence_excerpt": evidence,
                        "sensitive": category == "sensitive_personnel_note",
                        "rationale": "Matched by the deterministic fallback rule set.",
                    }
                )
        return {
            "reports": [
                {"source_submission_id": source_id, "signals": signals}
                for source_id, signals in signals_by_id.items()
            ]
        }, {"latency_seconds": 0.0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


FALLBACK_CATEGORY_FIELDS: dict[str, tuple[EvidenceField, ...]] = {
    "food_shortage": ("food_concerns_or_outages", "operational_notes"),
    "high_waste_or_overproduction": ("operational_notes", "food_concerns_or_outages"),
    "dietary_or_allergy_question": ("guest_issues_for_the_day",),
    "equipment_failure": ("operational_notes",),
    "employee_recognition": ("team_members_who_did_well",),
    "inventory_inconsistency": ("food_concerns_or_outages", "operational_notes"),
    "register_disruption": ("operational_notes",),
    "portion_complaint": ("guest_issues_for_the_day",),
    "beverage_request": ("guest_issues_for_the_day",),
    "sensitive_personnel_note": ("operational_notes", "team_members_who_did_well"),
}


def fallback_evidence(
    report: dict[str, Any],
    category: str,
) -> tuple[EvidenceField, str]:
    for field in FALLBACK_CATEGORY_FIELDS.get(category, tuple(TEXT_FIELDS)):
        value = str(report.get(field, "") or "")
        if value:
            return field, value
    for field in TEXT_FIELDS:
        value = str(report.get(field, "") or "")
        if value:
            return field, value
    return "operational_notes", "N/A"


def extract_semantic_signals(
    reports: list[dict[str, Any]],
    provider: SemanticProvider,
    cache_dir: Path,
    batch_size: int = 1,
    max_retries: int = 2,
    retry_delay_seconds: float = 1.0,
    sleep: Callable[[float], None] = time.sleep,
    fallback: SemanticProvider | None = None,
) -> ExtractionRun:
    eligible = [
        report for report in reports
        if report.get("parse_status") == "valid"
    ]
    fallback = fallback or DeterministicFallbackProvider()
    cache_dir.mkdir(parents=True, exist_ok=True)
    collected: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    run = ExtractionRun(reports=collected, model=provider.model)

    for report in eligible:
        cache_path = cache_dir / f"{report_hash(report, provider.model)}.json"
        if cache_path.exists():
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            cached_validated = validate_semantic_response(cached, [report])
            for item in cached_validated:
                item.setdefault("semantic_provider", provider.model)
            collected.extend(cached_validated)
            run.cache_hits += 1
        else:
            pending.append(report)

    for offset in range(0, len(pending), batch_size):
        batch = pending[offset : offset + batch_size]
        run.batches += 1
        last_error: Exception | None = None
        validated: list[dict[str, Any]] | None = None
        used_fallback = False
        for attempt in range(max_retries + 1):
            try:
                payload, metadata = provider.extract(batch)
                validated = validate_semantic_response(payload, batch)
                run.latency_seconds += float(metadata.get("latency_seconds", 0))
                run.prompt_tokens += int(metadata.get("prompt_tokens", 0))
                run.completion_tokens += int(metadata.get("completion_tokens", 0))
                run.total_tokens += int(metadata.get("total_tokens", 0))
                break
            except Exception as exc:
                last_error = exc
                if attempt < max_retries:
                    run.retries += 1
                    run.retry_events.append(
                        {
                            "batch": run.batches,
                            "attempt": attempt + 1,
                            "error_type": type(exc).__name__,
                            "reason": str(exc),
                        }
                    )
                    sleep(retry_delay_seconds * (attempt + 1))

        if validated is None:
            run.fallback_batches += 1
            used_fallback = True
            run.errors.append(str(last_error or "Unknown provider failure"))
            fallback_payload, _ = fallback.extract(batch)
            validated = validate_semantic_response(fallback_payload, batch)
            for item in validated:
                item["semantic_provider"] = fallback.model
        else:
            for item in validated:
                item["semantic_provider"] = provider.model

        by_id = {item["source_submission_id"]: item for item in validated}
        for report in batch:
            result = by_id[str(report["source_submission_id"])]
            if not used_fallback:
                cache_path = cache_dir / f"{report_hash(report, provider.model)}.json"
                cache_payload = {
                    "reports": [
                        {
                            "source_submission_id": result["source_submission_id"],
                            "signals": result["signals"],
                        }
                    ]
                }
                cache_path.write_text(
                    json.dumps(cache_payload, indent=2),
                    encoding="utf-8",
                )
            collected.append(result)

    collected.sort(key=lambda item: item["source_submission_id"])
    run.latency_seconds = round(run.latency_seconds, 4)
    return run


def estimate_run_cost(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float | None:
    pricing = MODEL_PRICING_PER_MILLION.get(model)
    if not pricing:
        return None
    cost = (
        (prompt_tokens / 1_000_000) * pricing["input"]
        + (completion_tokens / 1_000_000) * pricing["output"]
    )
    return round(cost, 6)
