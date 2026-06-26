# HITL Validation Evidence

## HITL Behavior Demonstrated

ShiftNotes includes two human-in-the-loop patterns:

1. Week 6 / orchestration checkpoint:
   the LangGraph workflow pauses before briefing finalization and waits for a
   human choice: approve, correct, or reject.

2. Final product checkpoint:
   Ted receives a briefing, inspects a claim if needed, challenges it in
   ordinary English, reviews the proposed correction, and confirms or cancels
   before the correction is saved.

## Evidence Files

| Evidence | Purpose |
| --- | --- |
| `evidence/retry_and_hitl.log` | Shows retry behavior followed by HITL pause before briefing finalization. |
| `evidence/persistence_and_approval.log` | Shows persisted workflow approval behavior. |
| `evidence/fallback.log` | Shows failure mode and fallback after retry limit. |
| `evidence/weekly_email_preview.html` | Shows the final email-first briefing surface used for review. |
| `evidence/monthly_email_preview.html` | Shows monthly operational summary format. |

## Key Log Excerpt

```text
Status: awaiting_review
LOG planner: mode=demo; expected_kiosks=['Bowls & Buns']; max_retries=2
LOG ingest_tool: failed; simulated ingestion failure on attempt 1
LOG evaluator: retrying ingestion; retry=1/2
LOG ingest_tool: success
LOG normalize: reports=4; valid=4; needs_review=0
LOG analyze: claims=8; missing_reports=1
LOG draft_briefing: created source-backed briefing
HITL INTERRUPT: workflow paused before briefing finalization.
Review options: approve, correct, reject
```

## Non-Team User Validation Script

Use this script with a non-team reviewer:

1. Open `evidence/weekly_email_preview.html`.
2. Ask the reviewer what the briefing says is most important.
3. Ask whether the source-backed claims are understandable.
4. Demonstrate the challenge concept:
   “If this claim is wrong, Ted can challenge it in ordinary English.”
5. Show that a correction requires confirmation before being saved.
6. Show `evidence/fallback.log` to demonstrate failure/recovery behavior.

## Validation Notes

The implemented system is designed so a human remains responsible for reviewing
claims and confirming corrections. ShiftNotes does not automatically discipline
employees, accuse workers, change future classification rules, or send
personnel-sensitive conclusions without review.

## Remaining Submission Note

If possible, add a screenshot or short written note from a non-team reviewer
confirming that they reviewed the briefing and understood the approve/challenge
flow. The technical evidence is present in this folder, but a course grader may
still expect proof that another person actually performed the validation.
