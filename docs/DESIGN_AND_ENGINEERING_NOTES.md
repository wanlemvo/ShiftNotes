# Design And Engineering Notes

This document captures the project-review context that is useful for future
walkthroughs, interviews, portfolio review, and product conversations.

## Design Ownership

ShiftNotes was designed around a real operational issue I observed at work.
Shift-note reports were already being created, but managers still had to read
many individual reports to identify recurring issues, missing submissions,
recognition patterns, shortages, guest requests, and waste signals.

I designed the product concept, email-first workflow, source-backed claim model,
human review behavior, and adoption strategy. AI assistance helped translate
that design into working code, tests, documentation, and implementation
iterations. I used AI as a technical collaborator, similar to asking a professor
or senior engineer for feedback, but the workflow and product direction came
from my understanding of the workplace problem.

## Most Important Architecture Decision

The biggest architecture decision was whether ShiftNotes should become a
centralized dashboard or quietly improve the workflow Ted already uses.

A dashboard would be a cleaner software surface, but it might create adoption
friction. Ted already works through email, so the prototype is email-first: he
receives a weekly or monthly briefing and only opens the Streamlit workspace
when he wants to inspect sources, challenge a claim, or review correction
history.

## Grounding And Validation

ShiftNotes separates exact calculations from semantic interpretation.

Python handles deterministic metrics such as dates, ratings, missing reports,
duplicates, and unclaimed lunch counts. The LLM is limited to interpreting
free-text fields such as food concerns, guest issues, operational notes, and
employee recognition.

Each semantic signal must include a source submission ID, field name, and exact
evidence excerpt. If the excerpt is not present in the original report field,
the signal is rejected. The mock dataset also includes planted ground-truth
patterns so model output can be evaluated against known source-level evidence.

## Failure Handling

Malformed AI output, empty responses, provider errors, unsupported evidence, and
timeout-style failures are treated as extraction failures. The system retries
failed calls, records retry events, and falls back to deterministic rules after
the retry limit is reached. Failed provider responses are not cached as valid
results.

Gmail sending is intentionally explicit. The system can preview the exact
HTML/plain-text message, and live delivery requires the `--confirm-send` flag.

## Test Coverage

The active prototype test suite covers:

- JotForm normalization and malformed report handling;
- missing report and final mock dataset behavior;
- semantic extraction, source validation, retry, fallback, caching, and
  benchmark calculations;
- weekly and monthly briefing generation;
- Gmail message construction and send invocation;
- LangGraph stateful workflow behavior;
- source-backed claim inspection and HITL correction.

## External Feedback

The prototype was reviewed by Ted, the intended workplace user. His feedback
emphasized priority handling, urgent versus non-urgent tasks, employee
recognition, and coaching opportunities. That feedback shaped the priority
sections, recognition handling, and safety guardrails.

## Measurable Value

The prototype demonstrates value by converting hundreds of individual
shift-note-style reports into source-backed briefings. Useful measures include:

- number of reports summarized;
- source-backed claims generated;
- missing reports detected;
- planted ground-truth patterns recovered;
- semantic precision and recall;
- manual review time avoided;
- number of claims a manager can inspect or challenge without searching through
  every report.

## Scaling Beyond The Prototype

To support a large user base, ShiftNotes would need production architecture:
authentication, tenant isolation, hosted database storage, background jobs,
queues, API rate-limit handling, monitoring, secret management, audit logging,
and stronger privacy controls for employee-related content.

The current prototype demonstrates the workflow. Measured business value and
production scale remain separate validation and engineering phases.

## What I Would Redesign Next

I would keep the email-first direction, but move persistence from local JSON and
SQLite into a database, make correction history more formal, split scheduled
jobs from the dashboard, and use real-world correction data to improve
evaluation over time.
