from pathlib import Path

import pytest

from shiftnotes.ai_benchmark import benchmark_semantic_extractions
from shiftnotes.config import load_groq_settings
from shiftnotes.semantic import (
    DeterministicFallbackProvider,
    estimate_run_cost,
    extract_semantic_signals,
    report_hash,
    validate_semantic_response,
)


def report(source_id="FM-0001", text="Kung Pao chicken ran low before close."):
    return {
        "source_submission_id": source_id,
        "date": "2026-03-02",
        "kiosk": "Bowls & Buns",
        "parse_status": "valid",
        "food_concerns_or_outages": text,
        "team_members_who_did_well": "",
        "guest_issues_for_the_day": "",
        "operational_notes": "",
    }


def response_for(item, excerpt=None):
    evidence = excerpt or item["food_concerns_or_outages"]
    return {
        "reports": [
            {
                "source_submission_id": item["source_submission_id"],
                "signals": [
                    {
                        "category": "food_shortage",
                        "subject": "Kung Pao chicken",
                        "severity": "medium",
                        "confidence": 0.94,
                        "evidence_field": "food_concerns_or_outages",
                        "evidence_excerpt": evidence,
                        "sensitive": False,
                        "rationale": "The report says the item ran low.",
                    }
                ],
            }
        ]
    }


class FakeProvider:
    model = "fake-model"

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def extract(self, reports):
        self.calls += 1
        next_value = self.responses.pop(0)
        if isinstance(next_value, Exception):
            raise next_value
        return next_value, {
            "latency_seconds": 0.25,
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
        }


def test_validates_exact_source_evidence():
    item = report()
    validated = validate_semantic_response(response_for(item), [item])

    assert validated[0]["signals"][0]["category"] == "food_shortage"


def test_rejects_evidence_not_found_in_source():
    item = report()

    with pytest.raises(ValueError, match="Unsupported evidence"):
        validate_semantic_response(
            response_for(item, excerpt="Chicken completely sold out."),
            [item],
        )


def test_rejects_unknown_or_missing_source_ids():
    item = report()
    payload = response_for(item)
    payload["reports"][0]["source_submission_id"] = "FM-9999"

    with pytest.raises(ValueError, match="source IDs"):
        validate_semantic_response(payload, [item])


def test_retry_then_success_records_usage(tmp_path: Path):
    item = report()
    provider = FakeProvider([ValueError("bad response"), response_for(item)])

    run = extract_semantic_signals(
        [item],
        provider,
        tmp_path,
        max_retries=1,
        retry_delay_seconds=0,
        sleep=lambda _: None,
    )

    assert provider.calls == 2
    assert run.retries == 1
    assert run.fallback_batches == 0
    assert run.total_tokens == 15
    assert run.reports[0]["signals"][0]["category"] == "food_shortage"


def test_failed_provider_uses_fallback_without_poisoning_cache(tmp_path: Path):
    item = report()
    provider = FakeProvider([ValueError("bad response")])

    run = extract_semantic_signals(
        [item],
        provider,
        tmp_path,
        max_retries=0,
        sleep=lambda _: None,
        fallback=DeterministicFallbackProvider(),
    )

    assert run.fallback_batches == 1
    assert run.errors == ["bad response"]
    assert list(tmp_path.glob("*.json")) == []
    assert (
        run.reports[0]["signals"][0]["evidence_field"]
        == "food_concerns_or_outages"
    )


def test_recognition_fallback_cites_recognition_field(tmp_path: Path):
    item = report(source_id="FM-0005", text="Food held well throughout service.")
    item["team_members_who_did_well"] = (
        "Maya Chen noticed a prep issue early and coordinated a quick recovery."
    )
    provider = FakeProvider([ValueError("bad response")])

    run = extract_semantic_signals(
        [item],
        provider,
        tmp_path,
        max_retries=0,
        sleep=lambda _: None,
        fallback=DeterministicFallbackProvider(),
    )

    recognition = next(
        signal
        for signal in run.reports[0]["signals"]
        if signal["category"] == "employee_recognition"
    )
    assert recognition["evidence_field"] == "team_members_who_did_well"
    assert recognition["evidence_excerpt"].startswith("Maya Chen")


def test_cache_avoids_repeat_provider_call(tmp_path: Path):
    item = report()
    first_provider = FakeProvider([response_for(item)])
    extract_semantic_signals([item], first_provider, tmp_path, sleep=lambda _: None)

    second_provider = FakeProvider([])
    run = extract_semantic_signals([item], second_provider, tmp_path, sleep=lambda _: None)

    assert second_provider.calls == 0
    assert run.cache_hits == 1


def test_benchmark_calculates_precision_and_recall():
    extractions = response_for(report())["reports"]
    truth = {
        "events": {
            "food_shortage:kung_pao_chicken": {
                "source_records": [{"source_submission_id": "FM-0001"}]
            }
        }
    }

    result = benchmark_semantic_extractions(extractions, truth, {"FM-0001"})

    assert result["summary"]["micro_precision"] == 100.0
    assert result["summary"]["micro_recall"] == 100.0


def test_benchmark_does_not_call_broad_recognition_a_maya_false_positive():
    extractions = [
        {
            "source_submission_id": "FM-0002",
            "signals": [
                {
                    "category": "employee_recognition",
                    "subject": "Sam",
                }
            ],
        }
    ]
    truth = {
        "events": {
            "recognition:maya_chen": {
                "source_records": [{"source_submission_id": "FM-0005"}]
            }
        }
    }

    result = benchmark_semantic_extractions(extractions, truth, {"FM-0002"})
    category = result["categories"]["recognition:maya_chen"]

    assert category["false_positive_count"] == 0
    assert category["valid_but_out_of_scope_source_ids"] == ["FM-0002"]


def test_benchmark_excludes_portion_observations_outside_trend_scope():
    extractions = [
        {
            "source_submission_id": "FM-0001",
            "signals": [
                {
                    "category": "portion_complaint",
                    "subject": "portion size",
                }
            ],
        }
    ]
    truth = {
        "events": {
            "cross_kiosk:portion_complaints_weeks_9_10": {
                "source_records": [{"source_submission_id": "FM-0193"}]
            }
        }
    }

    result = benchmark_semantic_extractions(extractions, truth, {"FM-0001"})
    category = result["categories"][
        "cross_kiosk:portion_complaints_weeks_9_10"
    ]

    assert category["false_positive_count"] == 0
    assert category["valid_but_out_of_scope_source_ids"] == ["FM-0001"]


def test_missing_groq_key_has_clear_error(tmp_path: Path):
    env_path = tmp_path / ".env"
    env_path.write_text("GROQ_MODEL=openai/gpt-oss-20b\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Missing GROQ_API_KEY"):
        load_groq_settings(env_path)


def test_cost_estimate_uses_selected_model_pricing():
    assert estimate_run_cost("openai/gpt-oss-20b", 1_000_000, 1_000_000) == 0.375
    assert estimate_run_cost("unknown-model", 100, 100) is None


def test_cache_hash_changes_when_prompt_version_changes(monkeypatch):
    item = report()
    original = report_hash(item, "fake-model")
    monkeypatch.setattr("shiftnotes.semantic.PROMPT_VERSION", "new-version")

    assert report_hash(item, "fake-model") != original
