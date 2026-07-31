# HITL Validation Evidence

## Non-Team User Validation

**Reviewer:** Ted Snow

**Role:** Intended operational user and T-Mobile Operations General Manager

**Relationship to project:** Workplace stakeholder; not a member of the student
development team

**Evidence:** Email feedback retained privately by the project author

Ted reviewed the ShiftNotes project as its intended operational user. His
review decision was effectively **request changes**, rather than unconditionally
approve the existing output. He asked for:

1. identification of high-priority tasks requiring immediate attention,
   including safety concerns and malfunctioning equipment;
2. prioritization of important tasks that are not urgent; and
3. tracking of employee recognition, including positive feedback and coaching
   opportunities.

This feedback produced downstream changes in the prototype. Weekly and monthly
email previews now contain a prioritized findings section. Equipment-related
disruptions are elevated in the ranking, and employee-recognition findings are
tracked with supporting source reports. Broader safety escalation and coaching
recommendations remain limited or deferred because personnel-sensitive
conclusions require human review.

Ted's email therefore provides non-team validation that the workflow and
briefing concept were understandable, while also documenting a real user
decision and the response actions taken afterward. The original screenshot is
not bundled because it contains personal contact information unrelated to the
course evaluation.

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

## Repeatable Validation Script

The following script can be used to repeat the validation:

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

## Evidence Interpretation

Ted's feedback documents external user review and a request-changes decision.
The bundled execution logs separately demonstrate the software's explicit
LangGraph interrupt, persisted waiting state, approval input, downstream
finalization, retry behavior, and fallback behavior. Together, the user record
and technical logs provide the Week 9 HITL validation evidence without claiming
that Ted personally executed the command-line LangGraph checkpoint.
