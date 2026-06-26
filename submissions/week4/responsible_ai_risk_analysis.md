# Responsible AI Risk Analysis and Mitigation Plan

## Risk 1: Unsupported Operational Claims

Risk:

The model may summarize a trend that is not actually supported by the source
reports.

Mitigation:

- Require every meaningful claim to store supporting source report IDs.
- Require exact evidence excerpts for semantic signals.
- Reject model output that cites text not present in the source field.
- Show source links or report references in the briefing.

## Risk 2: Personnel-Sensitive False Accusations

Risk:

Shift notes may contain employee names, complaints, praise, or ambiguous
comments. A model-generated summary could unfairly frame an employee.

Mitigation:

- Do not allow automatic accusations.
- Do not recommend discipline or termination.
- Flag sensitive personnel comments for human review.
- Require human confirmation before saving any correction.
- Treat confirmed corrections as audit records, not automatic rule changes.

## Risk 3: Privacy and Logging Exposure

Risk:

Operational reports may contain names, workplace details, and sensitive
business information. API calls, logs, or screenshots could expose data.

Mitigation:

- Use synthetic data for class demos.
- Do not commit `.env` files or API keys.
- Keep raw production data out of public artifacts.
- Document production setup separately from demo fixtures.
- Minimize logs to source IDs and validation status where possible.

## Risk 4: Overtrust in AI Summaries

Risk:

Managers may trust the briefing too much and stop checking source reports when a
claim seems surprising or consequential.

Mitigation:

- Make the briefing source-backed.
- Include missing-report completeness warnings.
- Provide an inspection workflow for source review.
- Make known limitations visible in documentation.
- Preserve a challenge/correction path.

## Risk 5: Missing Reports Distort Trends

Risk:

If a kiosk fails to submit reports, weekly or monthly trends may look better or
worse than reality.

Mitigation:

- Maintain an expected reporting schedule.
- Detect missing kiosk/date pairs.
- Report completeness before interpreting trends.
- Treat missing reports as an operational signal.

## Risk 6: Model Refusal or Safety Mismatch

Risk:

Different models may refuse, over-answer, or mishandle borderline personnel
requests differently.

Mitigation:

- Keep safety policy in application code.
- Use provider-independent validation.
- Benchmark refusal behavior with personnel-sensitive prompts.
- Route unsafe requests to human review rather than autonomous output.

## Risk 7: API Quotas and Reliability

Risk:

Model APIs can fail, rate limit, or produce malformed responses.

Mitigation:

- Use retry logic with explicit stop conditions.
- Route repeated failures to deterministic fallback.
- Cache successful model results.
- Label fallback results clearly.
- Keep local fixtures for reproducible demos.

## Conclusion

The safest ShiftNotes architecture is not “let the model decide.” The safer
architecture is:

```text
deterministic metrics
+ model-assisted semantic extraction
+ source validation
+ missing-report warnings
+ human review
+ correction history
```

This keeps the model useful while preventing it from becoming the final
authority on operational or personnel-sensitive decisions.
