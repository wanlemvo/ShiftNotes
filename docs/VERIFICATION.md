# Verification

## October 8, 2026 Local Update

Environment: Windows, existing project Python 3.13 environment, Streamlit 1.58.0.
No live JotForm fetch, Groq inference, or Gmail send was performed for this update.

| Check | Result | Scope |
| --- | --- | --- |
| Automated suite | 58 passed | Existing ingestion/analysis/AI/email/graph tests plus dashboard and app tests |
| Streamlit AppTest | Passed | Six navigation tabs, date and kiosk changes, custom dates, claim deep link, empty challenge feedback |
| Local browser | Passed | Headless Edge via Playwright: dashboard, three-month/kiosk filters, comparison, briefing preview, and challenge clarification |
| Responsive layout | Passed | 1600x1100 desktop and 390x844 mobile; mobile page and all eight metric tiles fit their width |
| App health | HTTP 200 | Local Streamlit health endpoint |
| Documentation links | Passed | Zero missing local links in current docs, README, and navigation indexes |
| Patch whitespace | Passed | `git diff --check` |

The in-app browser tool failed to start because its Windows sandbox helper could
not initialize. Visual checks used the existing bundled Playwright with installed
Edge instead. The first pytest run also hit an inaccessible Windows temp folder;
the suite passed with a project-local temporary directory:

```powershell
New-Item -ItemType Directory -Force dist/verification-20261008
.venv/Scripts/python -m pytest -q --basetemp=dist/verification-20261008/pytest
```

The ordinary command is `uv run pytest -q`. Screenshots and temporary browser
diagnostics are under ignored `dist/verification-20261008/`; the selected public
dashboard image is under [demo evidence](demo/README.md).

## What These Results Establish

Dashboard totals use valid, deduplicated report data for ratings and lunch counts;
missing and invalid reports are separate. Kiosk/date filters reach the source
sets and comparisons. Monthly versions of weekly claims do not double-count
observations. Confirmed weekly source corrections affect aggregated findings.

Backend tests cover confirmation, cancellation/refusal paths, state persistence,
retry/fallback, source grounding, and Gmail message/send invocation. The browser
check exercised a clarification response, not a real manager's validation or a
new live email delivery. Historical evidence in `demo/evidence/` remains dated
to its original runs and is not claimed as a fresh result.

## Remaining Verification

- Hosted Streamlit deployment and public-link verification after an approved push.
- End-to-end live JotForm-to-rich-briefing integration and scheduled delivery.
- Pilot accuracy, review time, and business impact with real workplace users.
- Long-term hosted correction persistence, concurrency, and access controls.

The dependency manifest and lock were unchanged. The release-capture check below
adds current fresh-environment evidence. A Streamlit deprecation warning remains for the existing HTML
email embedding API; previews rendered successfully in these checks.

## Release Capture and Clean Environment

On October 8, 2026, a fresh source snapshot was created from publishable files,
excluding ignored credentials and runtime state. `uv sync --locked` installed
169 packages into a new environment using Python 3.13.13. The suite passed all
58 tests in 46.05 seconds. This was an isolated environment on the same Windows
machine, not a separate laptop or operating-system validation.

`product-assets --base-url http://localhost:8503` generated 399 claims and 15
email previews in the snapshot. A separate Streamlit process served it for the
public demo captures. The real browser workflow includes source inspection,
the confirmation checkpoint, cancellation, and audit history. No live APIs or
email delivery are invoked by the capture scripts.

The GIF is a sequence of screenshots, and the WebM is the continuous browser
recording. See [media and reproduction](demo/README.md) and the capture manifest
for the specific synthetic claim used. The capture is a scripted demonstration,
not a new non-team-user validation session.
