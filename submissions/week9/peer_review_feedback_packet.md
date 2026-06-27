# Peer Review Feedback Packet

## Review Context

The Week 8 team prototype was reviewed as the baseline for the independent
ShiftNotes final implementation. The review focused on architecture coherence,
requirement traceability, error handling, source evidence, reproducibility,
security, and responsible AI safeguards.

This packet also records feedback from student reviewer Jayden Lawson and
workplace stakeholder Ted Snow. Jayden's feedback was originally delivered in
conversation and implemented before a formal review record was created. The
entry below is therefore a retrospective reconstruction by the project author,
not a verbatim quotation. Ted's feedback is supported by an email retained by
the project author; its contact details are intentionally excluded from this
submission.

The team-prototype review is documented in the root project file:

```text
TEAM_PROTOTYPE_REVIEW.md
```

## Student Peer Review: Jayden Lawson

**Reviewer:** Jayden Lawson

**Role:** Student peer reviewer

**Record type:** Retrospective summary of previously received verbal feedback

Jayden's feedback emphasized that the manager-facing result should do more than
repeat or summarize every shift report. The briefing should help the manager
identify what deserves attention first and should make it possible to inspect
the reports supporting an important finding. This feedback helped move the
implementation toward prioritized, source-backed findings instead of a
dashboard containing undifferentiated summaries.

### Response Actions

| Peer feedback | Implemented response |
| --- | --- |
| Make the output easier for a manager to act on rather than presenting every observation with equal weight. | Added a priority-findings section and category-based ordering to the weekly and monthly email previews. |
| Let the user verify important findings instead of expecting them to trust an AI summary. | Added source IDs, evidence excerpts, source-inspection links, and a claim-challenge workflow. |
| Keep the demonstration focused on the manager's real workflow. | Made briefing email previews the primary interface and retained Streamlit as an optional inspection surface. |

The resulting changes are visible in
`final_project/src/shiftnotes/email_preview.py`,
`final_project/data/final_mock/email_previews/`, and
`final_project/src/shiftnotes/correction_graph.py`.

## Workplace Stakeholder Feedback: Ted Snow

**Reviewer:** Ted Snow

**Role:** Intended operational user and T-Mobile Operations General Manager

**Evidence type:** Email feedback retained privately by the project author

Ted wrote that the project was progressing well and identified three
capabilities that would be beneficial to him as a user:

1. Identify high-priority tasks needing immediate attention, including safety
   concerns and malfunctioning equipment.
2. Prioritize other tasks that are important but not urgent.
3. Track employee recognition, including positive feedback and coaching
   opportunities.

### Response Status

| Stakeholder request | Status | Project response |
| --- | --- | --- |
| Identify urgent equipment or safety concerns. | Partially implemented | Equipment failures and operational disruptions are extracted, ranked highly, and shown with source evidence. A dedicated safety-escalation classification remains future work. |
| Prioritize important non-urgent tasks. | Implemented in prototype | Email previews rank source-backed findings by operational category and limit the main attention section to the most relevant findings. |
| Track positive employee recognition. | Implemented in prototype | Employee-recognition signals are extracted from the appropriate JotForm field and included in source-backed weekly and monthly findings. |
| Identify coaching opportunities. | Partially implemented with safeguards | Sensitive personnel notes can be identified for human review, but ShiftNotes deliberately refuses automatic accusations or disciplinary recommendations. A validated coaching-opportunity workflow remains future work. |

Ted's feedback confirms that prioritization and employee recognition are not
only class-project features; they correspond to needs identified by the intended
workplace user. The incomplete portions are retained as known limitations rather
than presented as finished functionality.

## Feedback Received / Identified

| Feedback | Response Action |
| --- | --- |
| The prototype dataset was useful, but too narrow and too focused on one recurring request. | Expanded the final dataset to three months of JotForm-style reports with broader guest feedback, operational issues, employee recognition, dietary questions, waste, and missing reports. |
| The dashboard was useful, but not Ted's main workflow. | Reframed the product around weekly/monthly briefing emails as the primary interface, with Streamlit only as an optional inspection surface. |
| Some features were described aspirationally rather than proven. | Added generated artifacts, tests, benchmark files, email previews, and known limitations to separate implemented behavior from future production work. |
| The original prototype needed clearer source traceability. | Added source-backed claim IDs, supporting report references, evidence excerpts, and claim challenge behavior. |
| HITL needed to be visible and auditable. | Added a LangGraph checkpoint demonstration plus a post-delivery claim correction flow requiring human confirmation before saving corrections. |
| Personnel-sensitive content needed safeguards. | Added a safety policy refusing automatic accusations, discipline recommendations, termination recommendations, or distribution of unverified personnel allegations. |
| Missing reports should be treated as an operational signal. | Added expected reporting schedule checks and missing kiosk/date detection. |
| Reproducibility needed to be stronger. | Added setup documentation, `.env.example`, deterministic fixture data, and automated tests. |

## Resulting Implementation Direction

The final independent project treats the Week 8 team implementation as a
prototype artifact and builds a more focused operational intelligence flow:

```text
JotForm-style reports
-> normalization and validation
-> missing report detection
-> deterministic metrics
-> semantic extraction
-> source-backed claims
-> weekly/monthly briefing emails
-> optional HITL claim challenge and correction
```

## Evidence Note

Jayden's original feedback was not recorded at the time it was given, so this
packet identifies it transparently as a retrospective summary rather than
presenting reconstructed language as a contemporaneous transcript. Ted's
original email remains available to the project author if an instructor asks to
verify the stakeholder feedback. The email image is not bundled because it
contains personal contact information unrelated to the project evaluation.
