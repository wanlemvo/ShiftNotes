# Peer Review Feedback Packet

## Review Context

The Week 8 team prototype was reviewed as the baseline for the independent
ShiftNotes final implementation. The review focused on architecture coherence,
requirement traceability, error handling, source evidence, reproducibility,
security, and responsible AI safeguards.

The review is documented in the root project file:

```text
TEAM_PROTOTYPE_REVIEW.md
```

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

## Remaining Review Gap

If the course requires an explicitly external cross-team review artifact, attach
that review comment, screenshot, or message to this packet before submission.
The current packet documents the implemented response actions based on the
team-prototype review and final-project QA review.
