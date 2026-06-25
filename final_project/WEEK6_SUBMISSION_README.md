# ShiftNotes Week 6 LangGraph Stateful Agent Checkpoint

This package contains the Week 6 checkpoint implementation and evidence for the
independent ShiftNotes operational-intelligence project.

## Requirements Demonstrated

- Stateful LangGraph workflow with more than three nodes
- Planner, tool/action, and evaluator responsibilities
- Conditional routing based on structured tool output
- Retry loop with an explicit two-retry stop condition
- Fallback route after repeated failures
- Human-in-the-loop interrupt before briefing finalization
- Approve, correct, and reject decisions
- SQLite checkpoint persistence across Python processes
- Safe fixture data that requires no API credentials

## Setup

Python 3.11 or newer is required.

```bash
python -m pip install -r requirements.txt
```

## Run the Demo

Start a run that fails once, recovers, and pauses for human review:

```bash
python final_project/src/shiftnotes/cli.py workflow-start \
  --thread-id week6-demo \
  --mode demo \
  --simulate-failures 1 \
  --max-retries 2 \
  --expected-kiosk "Bowls & Buns"
```

Inspect the persisted checkpoint from a separate process:

```bash
python final_project/src/shiftnotes/cli.py workflow-status week6-demo
```

Approve and resume:

```bash
python final_project/src/shiftnotes/cli.py workflow-resume week6-demo approve
```

Force the fallback route:

```bash
python final_project/src/shiftnotes/cli.py workflow-start \
  --thread-id week6-fallback \
  --mode demo \
  --simulate-failures 3 \
  --max-retries 2
```

## Test

```bash
python -m pytest tests
```

## Package Contents

- `ARCHITECTURE.md`: graph diagram, node roles, routing, retry, and HITL rationale
- `final_project/src/shiftnotes/`: actual ShiftNotes workflow implementation
- `final_project/data/demo/`: safe JotForm-style fixture
- `tests/`: normalization and stateful-orchestration tests
- `evidence/`: captured retry, fallback, persistence, HITL, and test logs

## Privacy

This package does not include:

- JotForm API credentials
- `.env`
- real JotForm API responses
- SQLite checkpoint databases
- workplace reports

The demo mode and live mode use the same graph. Only the ingestion source changes.
