# Sprint 2 Decision Matrix

## Criteria Weights

| Criterion | Weight | Rationale |
| --- | ---: | --- |
| Reasoning quality | 20% | The system must interpret operational meaning from messy notes. |
| Context handling | 15% | Reports, sources, and summaries may require multi-document context. |
| Coding ability | 15% | The model also supports development and refactoring work. |
| Cost fit | 15% | ShiftNotes may process many reports over time. |
| Safety behavior | 15% | Personnel-sensitive content requires cautious behavior. |
| Latency | 10% | Briefing generation should be practical and responsive. |
| Structured output reliability | 10% | Semantic extraction must return valid JSON with source evidence. |

## Weighted Scores

| Candidate | Context | Coding | Reasoning | Latency | Cost | Safety | Structured Output | Weighted Score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-class API model | 8 | 9 | 9 | 7 | 7 | 9 | 9 | 8.35 |
| Claude-class API model | 9 | 8 | 9 | 7 | 6 | 9 | 8 | 8.10 |
| Gemini-class API model | 10 | 7 | 8 | 8 | 8 | 8 | 7 | 8.05 |
| Groq-hosted open model | 7 | 7 | 7 | 10 | 9 | 7 | 8 | 7.70 |

## Interpretation

The highest overall score belongs to the GPT-class candidate because it balances
coding, reasoning, safety, and structured outputs. Claude is close behind
because it is especially strong for careful review and long-context reasoning.
Gemini remains attractive for very large-context and multimodal workflows.
Groq-hosted models score lower overall but are highly useful for fast,
cost-conscious prototype extraction.

## Final Decision

The project should not lock itself into one model for all tasks.

Decision:

```text
Use deterministic Python for exact metrics.
Use a replaceable LLM provider for semantic extraction.
Use source validation and HITL confirmation as non-negotiable safeguards.
```

Prototype provider:

```text
Groq-hosted open model
```

Reason:

Groq is fast and practical for the prototype, and the final project validates
its semantic output against source report text. If production needs higher
reasoning quality or stricter enterprise controls, GPT-class or Claude-class
models can be substituted behind the same provider boundary.
