# ShiftNotes Follow-Up Questions: Response Draft

## Which portions did you personally design before using AI assistance?

I personally designed the overall product idea, workflow, architecture, and user experience. The problem came from my workplace: shift-note reports were already being submitted, but the information was scattered across individual reports and required manual reading to find patterns.

My design decision was that ShiftNotes should not force the manager to learn an entirely new workflow. Instead, the system should ingest JotForm-style shift notes, normalize the data, analyze trends across kiosks, preserve source traceability, and send the manager a weekly or monthly briefing by email. The dashboard is supporting evidence, not the main interface.

AI assistance helped me turn that design into working code, documentation, tests, and implementation details. I used AI in the same way I would use a senior engineer or professor for feedback: to pressure-test architectural decisions, help write code faster, identify risks, and refine the implementation. The product direction, operational problem, adoption strategy, and core flow were mine.

## What was the hardest bug or architectural decision in the project?

The hardest architectural decision was whether to create a completely new centralized app for the manager or to optimize the workflow he already uses.

The more technically obvious solution would have been to build a dashboard where all reports, briefings, and analytics live in one place. That would have made the system feel more like a traditional software product. But I questioned whether that would actually be adopted in the workplace. Ted already receives and manages reports through email, so asking him to check a separate app every day could create friction.

I decided the better architecture was email-first. ShiftNotes does the work in the background and sends Ted one or two high-value briefing emails. He only opens the dashboard when he wants to inspect a claim, review source reports, or challenge something the system said. That choice made the system more practical because it improves his current workflow instead of replacing it.

The hardest technical issue was grounding semantic AI claims. Some useful signals, like guest complaints, employee recognition, equipment issues, or coaching concerns, cannot be captured by simple counting alone. The system had to use an LLM for interpretation while still requiring exact source evidence for every claim.

## How do you validate that an LLM response is correct and grounded?

I validate LLM responses in several layers.

First, I require structured output. The semantic extraction step returns a defined schema instead of free-form text. That makes the output easier to validate automatically.

Second, I require source-backed evidence. If the model identifies a signal, it must include the source submission ID, the field where the evidence came from, and an exact excerpt from the original report. The system rejects evidence excerpts that are not actually present in the source text.

Third, I compare the output against planted ground-truth patterns in the mock dataset. The final dataset intentionally includes known trends, missing reports, urgent issues, recognition patterns, and ambiguous personnel comments. That allows me to measure whether the system finds the patterns it is supposed to find instead of only producing plausible summaries.

Fourth, I use tests and benchmarks. The project includes tests for semantic extraction, source validation, fallback behavior, briefing generation, Gmail delivery, JotForm normalization, and the final mock dataset.

Finally, I include human review. The manager can inspect the source reports behind a claim and challenge the system in ordinary English. That creates a human-in-the-loop correction path for cases where the AI is wrong or overstates something.

An industry-standard way to describe this is: structured outputs, source-grounded validation, golden datasets, precision/recall benchmarking, automated regression tests, and human-in-the-loop review.

## What happens when the API times out or returns malformed output?

The semantic extraction flow has retry and fallback behavior.

If the AI provider times out, returns malformed JSON, returns an empty response, or produces evidence that cannot be verified against the source report, the system treats that as a failed extraction. It records the error, retries up to the configured retry limit, and logs retry events.

If the provider still fails, the system falls back to a deterministic rule-based extractor. That fallback is less flexible than the LLM, but it prevents the entire briefing pipeline from breaking. Importantly, failed provider responses are not cached as valid results, so a bad response does not poison future runs.

The Gmail delivery flow also validates the recipient address and builds a proper multipart email with both plain-text and HTML versions. If the Gmail API fails, that error is surfaced instead of silently pretending the email was sent.

## What tests would fail if the core workflow broke?

If the core workflow broke, several test groups would catch it.

If JotForm ingestion or cleaning broke, `test_jotform_normalize.py` would fail because it checks that JotForm-style submissions become normalized shift reports with the correct fields, ratings, dates, kiosk names, source IDs, and validation errors.

If the semantic AI layer broke, `test_semantic_extraction.py` would fail. Those tests check exact source evidence validation, rejection of unsupported evidence, unknown source IDs, retry behavior, fallback behavior, caching, missing API key errors, and benchmark calculations.

If the briefing generation broke, `test_final_briefings.py` would fail. Those tests verify that the system generates twelve weekly briefings and three monthly briefings, keeps briefings kiosk-centered, includes source-backed claims, handles sensitive personnel notes carefully, and includes challenge links.

If the email delivery flow broke, `test_gmail_delivery.py` would fail. Those tests verify that the system builds multipart email messages, loads generated preview files, validates recipients, and calls Gmail's send method with an encoded MIME message.

If the LangGraph/stateful workflow broke, `test_langgraph_workflow.py` and `test_state.py` would be relevant because they cover the agent-style workflow, conditional routing, persistence, and checkpoint behavior.

## Which project has been used by someone other than you?

ShiftNotes has been reviewed and demoed outside of just me. I showed the project to Ted, the operations general manager who experiences the shift-note problem directly. He gave feedback that the system should identify high-priority tasks, separate urgent from non-urgent issues, and track employee recognition or coaching opportunities.

That feedback influenced the final version. The system now handles urgent/safety-style signals, operational issues, employee recognition, sensitive personnel notes, and source-backed inspection. The project is not fully deployed in production yet, but it has been validated with the intended user and is being shaped around his actual workflow.

## What measurable result proves the product solves its stated problem?

The main measurable result is reduction in manual report review.

Instead of reading hundreds of individual shift notes, the manager can read a weekly or monthly briefing that summarizes trends, missing reports, urgent issues, food shortages, waste indicators, guest feedback, employee recognition, and kiosk-specific patterns.

The final dataset contains about three months of expected reports across six kiosks, with intentionally missing reports and known planted trends. A useful measurement is whether ShiftNotes correctly identifies those planted patterns and presents them with source links.

Other measurable indicators include:

- Number of reports summarized per briefing.
- Number of source-backed claims generated.
- Percentage of planted ground-truth patterns detected.
- Precision and recall of semantic event extraction.
- Number of missing kiosk reports detected.
- Time saved compared with manually reading each report.
- Whether Ted can inspect and challenge claims without needing to search through every email manually.

The strongest current proof is that the system can turn many individual reports into source-backed operational summaries and deliver them in the same email-based workflow the manager already uses.

## What would need to change before the system could handle 1,000 users?

To support 1,000 users, ShiftNotes would need to move from a prototype/demo architecture to a multi-tenant production architecture.

The main changes would be:

- User accounts and tenant separation so each customer only sees their own reports.
- A database instead of local JSON files for reports, claims, corrections, audit logs, and briefing history.
- Background job scheduling for ingestion, analysis, and email delivery.
- A queue system so large batches do not block the app.
- Rate-limit handling for JotForm, Gmail, and AI provider APIs.
- Centralized logging, monitoring, and alerting.
- Secure secret management instead of local environment files.
- Role-based access control for managers, admins, and reviewers.
- Stronger privacy controls for employee-related comments.
- Deployment infrastructure that can scale independently for the web app, background workers, and storage.

The current project proves the workflow and value. Scaling to 1,000 users would require production engineering around reliability, security, isolation, and operations.

## Which parts would you redesign now, and why?

I would keep the email-first product direction, because that still fits the user's real workflow. But I would redesign some internals.

First, I would move persistent data out of local files and into a real database. JSON files are useful for a prototype, but a database would make searching, filtering, auditing, and multi-user access much cleaner.

Second, I would make the correction workflow more formal. Right now, the manager can challenge a claim, but a production version should preserve the full correction history, show before-and-after claim versions, and require confirmation before changing future classification behavior.

Third, I would separate the dashboard, ingestion jobs, AI extraction jobs, and email delivery more clearly. That would make the system easier to deploy and debug.

Fourth, I would improve evaluation. The current project has a ground-truth dataset and tests, but a production system should track real-world false positives, false negatives, user corrections, and recurring failure modes over time.

## Can you implement and explain a feature without relying on generated code?

Yes. I can implement and explain features without relying on generated code. AI helped me move faster, but I still need to understand the code well enough to debug it, explain the architecture, validate the outputs, and make design decisions.

For example, I can explain the core workflow manually:

1. Retrieve JotForm-style submissions.
2. Normalize them into a consistent shift-report schema.
3. Validate required fields and flag malformed reports.
4. Analyze structured metrics like ratings, unclaimed lunches, kiosks, dates, and missing submissions.
5. Use semantic extraction for free-text fields.
6. Require each AI signal to cite an exact source excerpt.
7. Generate weekly and monthly briefings.
8. Send the briefing through Gmail.
9. Let the manager inspect or challenge source-backed claims.

If I had to implement a small feature manually, such as adding a new briefing section for “highest priority operational issues,” I would first define the data needed, write the logic to filter high-severity signals, add tests for expected output, update the briefing renderer, and verify the result through the email preview and dashboard.

