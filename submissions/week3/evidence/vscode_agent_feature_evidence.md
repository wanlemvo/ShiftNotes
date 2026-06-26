# VSCode Agent Mode Feature Evidence

## Scoped Feature

```text
Build a source-backed weekly analysis feature for ShiftNotes.
The feature should parse JotForm-style shift reports, preserve source IDs,
calculate deterministic metrics, identify recurring operational signals, and
generate a weekly summary.
```

## Prompt Transcript Highlights

```text
User: I want the weekly format to be kiosk-by-kiosk trend analysis.
It should give averages, a general summary of the week, specific statistics,
and trends noticed.

Agent: I will keep exact metrics deterministic and use AI only for semantic
fields such as guest issues, food concerns, recognition, and operational notes.

User: My concern is some of the most important data is semantic.

Agent: Then the pipeline should be hybrid: Python calculates exact numbers,
while the model extracts categorized semantic events with source evidence.
```

## Resulting Diff Summary

The feature case produced the following implementation shape in the final
codebase:

| File / Area | Result |
| --- | --- |
| `final_project/src/shiftnotes/normalize.py` | Normalizes JotForm-style submissions into stable report records. |
| `final_project/src/shiftnotes/baseline.py` | Calculates deterministic metrics, missing reports, and baseline benchmarks. |
| `final_project/src/shiftnotes/semantic.py` | Defines semantic extraction and source evidence validation. |
| `final_project/src/shiftnotes/briefings.py` | Generates weekly/monthly operational briefing content. |
| `final_project/src/shiftnotes/email_preview.py` | Produces HTML and plain-text briefing email previews. |
| `tests/test_final_briefings.py` | Verifies briefing artifacts and source-backed claims. |
| `tests/test_semantic_extraction.py` | Verifies semantic schema validation, evidence checks, and benchmark behavior. |

## Verification Behavior

Verification used the project test suite:

```text
python -m pytest -q
57 passed
```

## Reflection

The strongest result of agent-assisted implementation was the repeated insistence
on source-backed claims. The final product avoids presenting unsupported model
summaries as operational facts.
