# Week 4 Submission - Multi-Model Comparison Tool and Recommendation

This folder is a standalone Sprint 2 / Week 4 submission package for
ShiftNotes.

## Required Artifacts

| Requirement | File |
| --- | --- |
| Benchmarking script | `benchmark_models.py` |
| Execution output | `benchmark_results.json`, `benchmark_results.md` |
| Quantitative comparison across at least 3 models | `benchmark_results.md`, `model_selection_report.md` |
| Model recommendation memo | `model_selection_report.md` |
| Decision matrix | `decision_matrix.md` |
| Responsible AI risk analysis and mitigation | `responsible_ai_risk_analysis.md` |

## Candidate Models

The benchmark compares four model/provider strategies:

- OpenAI GPT-class model
- Anthropic Claude-class model
- Google Gemini-class model
- Groq-hosted open model

The recommendation is a hybrid architecture: deterministic Python for exact
operational metrics and a replaceable LLM provider for semantic free-text
extraction.
