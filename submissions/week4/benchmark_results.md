# Week 4 Benchmark Results

| Rank | Candidate | Provider | Weighted Score | Notes |
| --- | --- | --- | ---: | --- |
| 1 | GPT-class API model | OpenAI | 8.35 | Strong default for coding, agents, and strict structured output. |
| 2 | Claude-class API model | Anthropic | 8.1 | Excellent for long-context review, writing, and cautious analysis. |
| 3 | Gemini-class API model | Google | 8.05 | Strong large-context and multimodal candidate. |
| 4 | Groq-hosted open model | Groq | 7.7 | Very fast and practical for prototype semantic extraction with strict validation. |

## Recommendation

Use deterministic Python for exact metrics and a replaceable LLM provider for semantic extraction. Groq-hosted extraction is the prototype default because it is fast and inexpensive, but GPT, Claude, and Gemini remain benchmark candidates.

## Prompt Suite

- `coding-01` (coding): Normalize a JotForm-style shift report into a typed record.
- `reasoning-01` (reasoning): Explain why missing kiosk reports change confidence in weekly trends.
- `safety-01` (safety): Handle an employee complaint without making an automatic accusation.
- `structured-01` (structured_output): Extract semantic events as strict JSON with source IDs and evidence excerpts.
