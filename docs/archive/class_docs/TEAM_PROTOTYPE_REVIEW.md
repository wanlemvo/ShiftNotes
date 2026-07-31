# Team Prototype Review

## Purpose

This document records the review of the GitHub/team implementation after the Week 8 checkpoint.

The goal is not to criticize the team work. The goal is to decide what is useful for my independent version of ShiftNotes and what should remain as prototype evidence.

## Current Position

The team implementation should be treated as a prototype artifact.

It contains meaningful work, including a mock dataset, notebook, dashboard, signal classifier, agent pipeline, tests, screenshots, and Week 8 report materials. However, the independent project is now focused on a specific operational problem at my job, so the team implementation should not automatically become the final implementation.

## What Appears Useful

- The mock dataset is a strong starting point for demonstrating the idea.
- The dataset includes 100 reports across six kiosks.
- The dataset includes patterns related to poke requests, chicken shortages, waste, recognition, and operational issues.
- The dataset follows the general shape of the shift-note form: date, kiosk, lead name, food quality, food quantity, food concerns, recognition, guest issues, operational notes, and unclaimed lunches.
- The form structure itself is valuable because the operational questions are already built into the intake process. This means the data is cleaner than a generic pile of emails or notes would be.
- Several fields are already structured enough for straightforward analysis, especially ratings, kiosk, date/week, lead name, and unclaimed lunches.
- The dashboard shows that shift-note data can be summarized visually.
- The signal classifier demonstrates a first attempt at extracting operational signals.
- The tests show that at least part of the classifier behavior is covered.
- The screenshots and Week 8 report are useful evidence for prototype progress.

## What Needs Careful Review

- The mock reports may not fully reflect how real operational reports are written.
- The mock dataset currently focuses too much on poke as the main guest-request pattern. This proves the trend-detection concept, but it is too narrow for the final independent project.
- Guest feedback should include a wider range of realistic comments: product requests, complaints, praise, confusion, service concerns, menu questions, dietary questions, and repeated non-poke themes.
- Food concerns and operational notes also need more semantic variety because those fields are likely to contain the most meaningful operational intelligence.
- The team implementation may be broader than the workplace-specific problem I am trying to solve.
- Some documentation describes planned or partially implemented features as if they are complete.
- The app, RAG, Gmail, HITL, and Streamlit flows need clearer separation between working features and future goals.
- The dashboard may be useful, but Ted's actual need may be closer to a passive weekly summary than an interactive tool.
- The current implementation has multiple overlapping files and paths that may need consolidation if adopted.
- A larger dataset, potentially three to six months of reports, may be more useful for proving cost savings, operational efficiency, labor planning, and RAG-style historical retrieval.

## Working Findings From Initial Review

- The dataset exists and contains 100 reports.
- The dataset covers six kiosks.
- Poke appears as a recurring guest request.
- Kiosk B has the highest waste pattern.
- Kiosk F appears to have lower quantity consistency.
- The test suite passed locally with 10 tests.
- The tests mainly cover the signal classifier and state schema.
- The tests do not fully validate the Streamlit app, Gmail integration, RAG behavior, or complete pipeline behavior.

## Dataset Review Notes

The shift-note form is strong because it already asks for the operational categories leadership cares about.

Structured or mostly structured fields:

- Food quality rating
- Food quantity rating
- Kiosk
- Date and week
- Lead name
- Number of unclaimed lunches

Semantic fields:

- Food concerns or outages
- Team members who did well
- Guest issues for the day
- Operational notes

The semantic fields are where the most meaningful analysis will happen. Recognition can be counted by employee mentions, but food concerns, guest issues, and operational notes require more interpretation.

The current mock data is useful for proving the basic idea, but it is too clean and too focused on poke requests. The final independent version should use more varied guest feedback and more realistic operational language.

Potential dataset improvements:

- Expand from one month to three or six months.
- Add more varied guest requests beyond poke.
- Include repeated complaints and positive feedback, not only requests.
- Add more realistic ambiguous notes and short entries such as "N/A" or "nothing to report."
- Include labor and workflow signals such as rush periods, line slowdowns, staffing gaps, and recovery notes.
- Make waste and labor-efficiency patterns visible over time.
- Preserve source report IDs so final insights can be traced back to the notes that produced them.

## Provisional Decision

Do not edit the team implementation directly yet.

Instead:

1. Preserve it as prototype evidence.
2. Review which parts actually support the workplace-specific use case.
3. Define the independent final-project scope.
4. Create a backlog.
5. Only then create or refactor the final implementation.

## Questions To Answer Before Adoption

- Do the mock reports sound like real shift notes from my environment?
- Are the report fields aligned with the actual form or workflow?
- Are the detected signals the right operational signals?
- Does the dashboard answer the questions Ted would actually ask?
- Would a passive weekly summary be more valuable than an interactive dashboard?
- Which parts of the team prototype are worth copying into the independent implementation?
- Which parts should remain as Week 8 prototype evidence only?
