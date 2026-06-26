# Sprint 2 Model Selection Report

## Objective

The Sprint 2 model-selection task was to compare candidate models for
ShiftNotes and recommend a strategy for turning shift-note reports into
operational intelligence.

ShiftNotes has two different kinds of work:

1. Exact deterministic work:
   dates, kiosk names, ratings, counts, duplicates, missing reports, and waste.
2. Semantic interpretation:
   food concerns, guest issues, recognition, operational notes, and ambiguous
   personnel-sensitive comments.

The model strategy should not use an LLM for everything. Exact calculations
should stay in code, while language models should be used only where language
understanding is needed.

## Candidate Models

The benchmark compared four model/provider strategies:

- OpenAI GPT-class API model
- Anthropic Claude-class API model
- Google Gemini-class API model
- Groq-hosted open model

The comparison criteria were:

- context handling;
- coding ability;
- reasoning quality;
- latency;
- cost fit;
- safety behavior;
- structured output reliability.

## Benchmark Method

The benchmark script is:

```text
benchmark_models.py
```

It uses a ShiftNotes-specific prompt suite:

- normalize a JotForm-style shift report into a typed record;
- explain why missing kiosk reports affect confidence;
- handle an employee complaint without making an automatic accusation;
- extract semantic events as strict JSON with source IDs and evidence excerpts.

The script produces:

```text
benchmark_results.json
benchmark_results.md
```

## Results Summary

| Rank | Candidate | Weighted Score | Interpretation |
| --- | --- | ---: | --- |
| 1 | GPT-class API model | 8.35 | Best overall balance for coding, structured output, and general reasoning. |
| 2 | Claude-class API model | 8.10 | Strongest for long-context review, writing, and cautious analysis. |
| 3 | Gemini-class API model | 8.05 | Strong large-context and multimodal option. |
| 4 | Groq-hosted open model | 7.70 | Fastest and cost-effective for prototype semantic extraction, but needs strict validation. |

## Recommendation

The recommended Sprint 2 strategy is a hybrid architecture:

```text
Deterministic Python metrics
+ replaceable LLM semantic extraction
+ strict source-evidence validation
+ HITL correction flow
```

For the prototype, Groq-hosted semantic extraction is acceptable because it is
fast and practical for experimentation. However, the provider boundary should
remain replaceable so GPT, Claude, or Gemini can be swapped in if benchmark
results, cost, or safety requirements change.

## Why This Fits ShiftNotes

ShiftNotes should never ask a model to calculate simple counts or ratings.
Those tasks are more reliable in code.

The model should only handle the parts that require language understanding:

- “Guests keep asking for poke.”
- “Chicken was short again.”
- “Tony was mentioned in a complaint.”
- “The fryer slowed down the line.”
- “A guest asked about gluten-free options.”

Even then, the model output must be validated against the original report text.
If a claim cannot point back to supporting reports, it should not appear in a
manager briefing.

## Final Selection

Prototype default:

```text
Groq-hosted semantic extraction with strict JSON and source validation.
```

Development/review support:

```text
GPT-class and Claude-class models for coding, architecture review, and report writing.
```

Future benchmark candidate:

```text
Gemini-class model for very large-context document ingestion or multimodal report review.
```

## Sources To Recheck Before Production

- OpenAI model documentation and pricing: `https://platform.openai.com/docs/models`
- Anthropic model documentation and pricing: `https://docs.anthropic.com/`
- Google Gemini model documentation: `https://ai.google.dev/gemini-api/docs/models`
- Groq model documentation: `https://console.groq.com/docs/models`

The prototype recommendation is based on Sprint 2 fit and final project
evidence, not a permanent production procurement decision.
