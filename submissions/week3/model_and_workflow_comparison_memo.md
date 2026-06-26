# Week 3 Model and Workflow Comparison Memo

## 1. Purpose

ShiftNotes is a workplace-focused operational intelligence prototype. The
system reads JotForm-style shift reports, cleans the structured fields,
interprets semantic notes, preserves source traceability, and produces weekly or
monthly management briefings.

The Week 3 goal was to compare model options and AI-assisted development
workflows before committing to the Sprint 2 implementation strategy.

## 2. Frontier Model Shortlist

| Model | Context / Input Strength | Reasoning Strength | Latency / UX | Cost Fit | Safety Behavior | ShiftNotes Fit |
| --- | --- | --- | --- | --- | --- | --- |
| OpenAI GPT family | Strong general coding, structured output, and tool-use support. | Strong for multi-step software and data reasoning. | Usually responsive enough for IDE and CLI workflows. | Depends on selected model tier; smaller models are better for frequent extraction. | Strong safety behavior and mature API controls. | Good default for agentic development and structured extraction. |
| Anthropic Claude family | Strong long-context reading and careful code/document analysis. | Strong planning, critique, and documentation quality. | Good for CLI review and large-file reasoning; latency can vary. | Higher-end models may be expensive for bulk extraction. | Conservative safety posture, useful for personnel-sensitive workflows. | Strong for architecture review, report writing, and HITL design. |
| Google Gemini family | Large context windows and strong multimodal/document support. | Strong broad reasoning; quality varies by model tier. | Useful when very large documents or screenshots matter. | Flash-tier models can be cost-effective for batch tasks. | Good safety controls but should be tested for refusal consistency. | Good candidate for large-context document ingestion and alternate benchmark. |
| Groq-hosted open models | Very low latency for supported open-weight models. | Quality depends on selected hosted model. | Excellent for quick semantic extraction experiments. | Useful free/low-cost prototype path, subject to quota limits. | Requires stricter application-level validation. | Final prototype selected Groq for semantic extraction behind strict source validation. |

## 3. Concrete Feature Case

The same scoped feature was used to compare IDE workflows:

```text
Implement a source-backed weekly analysis feature for shift notes.

The feature should parse JotForm-style records, preserve source report IDs,
calculate deterministic metrics, identify semantic operational signals, and
produce a summary that links claims back to supporting reports.
```

## 4. VSCode Agent Mode Observations

VSCode agent mode was strongest when the desired change was already scoped.
It worked well for moving through files, making local edits, and keeping the
implementation close to the existing project structure.

Strengths:

- Better for incremental implementation inside the real codebase.
- Easier to inspect diffs and run tests immediately.
- Good fit for adding a narrow feature without redesigning the whole project.
- Lower friction for preserving local style and file organization.

Limitations:

- It still required clear human direction about scope.
- It could over-edit if the prompt was too broad.
- It needed explicit reminders to preserve source traceability and avoid
  unsupported AI claims.

## 5. Cursor Composer Observations

Cursor Composer was strongest for fast ideation and broad edits across several
files. It was useful for comparing alternative implementations and generating a
first-pass structure.

Strengths:

- Good planning flow for a multi-file feature.
- Helpful for quickly sketching an implementation path.
- Strong at explaining proposed edits before applying them.

Limitations:

- More likely to produce a polished-looking plan before enough evidence was
  verified.
- Required careful review to avoid optimistic claims about unimplemented
  features.
- Verification behavior depended heavily on whether the prompt explicitly asked
  it to run tests.

## 6. IDE vs CLI Workflow Takeaway

The best workflow for ShiftNotes was hybrid:

- Use IDE agents for scoped feature implementation.
- Use CLI agents for repository audit, test execution, packaging, and
  documentation consistency checks.
- Require every meaningful AI-generated claim to connect back to code,
  tests, logs, or source records.

## 7. MCP Integration Notes

The MCP trial focused on the planned Gmail/JotForm workflow. The intended
production goal was to let an agent read relevant shift-note messages or
records, then route them into the ShiftNotes pipeline.

Observed value:

- MCP makes external tools available through a consistent agent interface.
- It can reduce custom integration code when the target system already exposes
  reliable tools.
- It supports a clean separation between the agent plan and external action.

Observed limitation:

- Authentication and account setup remain the hard part.
- MCP tool availability does not remove the need for structured validation.
- For ShiftNotes, direct JotForm API access became cleaner than Gmail parsing
  because JotForm stores the structured submission data.

## 8. Provisional Sprint 2 Model Strategy

The recommended Sprint 2 strategy was hybrid:

1. Use deterministic Python code for dates, ratings, counts, duplicates,
   missing reports, and waste metrics.
2. Use a model only for semantic interpretation of free-text fields.
3. Require strict JSON schema output for model results.
4. Reject model outputs that cite missing source IDs or evidence text that does
   not appear in the original report.
5. Keep the model provider replaceable so GPT, Claude, Gemini, or Groq-hosted
   models can be benchmarked without rewriting the product.

This strategy directly shaped the final ShiftNotes implementation.

## 9. Recommendation

For Sprint 2, the best model strategy was not to choose one model for
everything. The best strategy was to separate deterministic computation from
semantic interpretation.

The provisional recommendation:

- Use Claude or GPT-class models for development, architecture review, and
  technical writing.
- Use Groq-hosted semantic extraction for the prototype because it is fast and
  practical for experimentation.
- Keep Gemini as a benchmark candidate for large-context document workflows.
- Validate all model output against source evidence before it can appear in a
  management briefing.
