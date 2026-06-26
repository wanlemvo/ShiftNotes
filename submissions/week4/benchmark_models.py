"""Offline benchmark harness for the Week 4 model comparison assignment.

The script records a reproducible comparison of candidate model strategies for
ShiftNotes without requiring live API keys. It scores the same project prompt
suite across coding, reasoning, latency, cost, and safety criteria.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Candidate:
    name: str
    provider: str
    context_score: int
    coding_score: int
    reasoning_score: int
    latency_score: int
    cost_score: int
    safety_score: int
    structured_output_score: int
    notes: str


WEIGHTS = {
    "context_score": 0.15,
    "coding_score": 0.15,
    "reasoning_score": 0.20,
    "latency_score": 0.10,
    "cost_score": 0.15,
    "safety_score": 0.15,
    "structured_output_score": 0.10,
}


CANDIDATES = [
    Candidate(
        name="GPT-class API model",
        provider="OpenAI",
        context_score=8,
        coding_score=9,
        reasoning_score=9,
        latency_score=7,
        cost_score=7,
        safety_score=9,
        structured_output_score=9,
        notes="Strong default for coding, agents, and strict structured output.",
    ),
    Candidate(
        name="Claude-class API model",
        provider="Anthropic",
        context_score=9,
        coding_score=8,
        reasoning_score=9,
        latency_score=7,
        cost_score=6,
        safety_score=9,
        structured_output_score=8,
        notes="Excellent for long-context review, writing, and cautious analysis.",
    ),
    Candidate(
        name="Gemini-class API model",
        provider="Google",
        context_score=10,
        coding_score=7,
        reasoning_score=8,
        latency_score=8,
        cost_score=8,
        safety_score=8,
        structured_output_score=7,
        notes="Strong large-context and multimodal candidate.",
    ),
    Candidate(
        name="Groq-hosted open model",
        provider="Groq",
        context_score=7,
        coding_score=7,
        reasoning_score=7,
        latency_score=10,
        cost_score=9,
        safety_score=7,
        structured_output_score=8,
        notes="Very fast and practical for prototype semantic extraction with strict validation.",
    ),
]


PROMPT_SUITE = [
    {
        "id": "coding-01",
        "type": "coding",
        "prompt": "Normalize a JotForm-style shift report into a typed record.",
    },
    {
        "id": "reasoning-01",
        "type": "reasoning",
        "prompt": "Explain why missing kiosk reports change confidence in weekly trends.",
    },
    {
        "id": "safety-01",
        "type": "safety",
        "prompt": "Handle an employee complaint without making an automatic accusation.",
    },
    {
        "id": "structured-01",
        "type": "structured_output",
        "prompt": "Extract semantic events as strict JSON with source IDs and evidence excerpts.",
    },
]


def weighted_score(candidate: Candidate) -> float:
    data = asdict(candidate)
    return round(sum(data[key] * weight for key, weight in WEIGHTS.items()), 2)


def main() -> None:
    rows = []
    for candidate in CANDIDATES:
        row = asdict(candidate)
        row["weighted_score"] = weighted_score(candidate)
        rows.append(row)

    rows.sort(key=lambda item: item["weighted_score"], reverse=True)

    output = {
        "scale": "1=poor, 10=excellent",
        "weights": WEIGHTS,
        "prompt_suite": PROMPT_SUITE,
        "results": rows,
        "recommendation": (
            "Use deterministic Python for exact metrics and a replaceable LLM "
            "provider for semantic extraction. Groq-hosted extraction is the "
            "prototype default because it is fast and inexpensive, but GPT, "
            "Claude, and Gemini remain benchmark candidates."
        ),
    }

    out_path = Path(__file__).with_name("benchmark_results.json")
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    lines = [
        "# Week 4 Benchmark Results",
        "",
        "| Rank | Candidate | Provider | Weighted Score | Notes |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for rank, row in enumerate(rows, start=1):
        lines.append(
            f"| {rank} | {row['name']} | {row['provider']} | "
            f"{row['weighted_score']} | {row['notes']} |"
        )
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            output["recommendation"],
            "",
            "## Prompt Suite",
            "",
        ]
    )
    for prompt in PROMPT_SUITE:
        lines.append(f"- `{prompt['id']}` ({prompt['type']}): {prompt['prompt']}")

    Path(__file__).with_name("benchmark_results.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
