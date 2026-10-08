# Repository and Archive Policy

## Active Version

`streamlit_app.py` launches `demo/app.py`; core code lives in
`demo/src/shiftnotes/`. The package and tests use that source directory. The folder
name `demo` is deliberate: this is a working prototype. The new dashboard is part
of this app, not a second standalone HTML UI.

At the start of the October 8, 2026 cleanup, GitHub `main` pointed to `f3c1bf1`.
The local branch was `codex/final-submission`; its old remote-tracking reference
did not establish a current remote branch. The user subsequently authorized
publishing the integrated dashboard and demonstration media to `main`. Release
commit `89157b1` contains that update and the public media.
Historical remote branches are preserved; no force push or history rewrite is
part of this release. Hosted deployment status is recorded in verification notes.

The prior Streamlit deployment record targets `codex/final-submission` and
`demo/app.py`. That remote branch had been renamed to `main`. A compatibility
branch named `codex/final-submission` was restored at the same release commit
so the existing host can resolve its source. Until the owner retargets Streamlit
to `main`, publish app updates to both refs without letting them diverge.
`main` remains the canonical repository entry point.

## Contents Worth Publishing

- Active app, core modules, tests, generator, dependency manifest and lock.
- Synthetic records, ground truth, briefings, and claims needed to run the demo
  immediately without credentials.
- Product docs, feature evidence, verification notes, and change log.
- Real UI screenshots, an animated stage overview, a continuous WebM recording,
  capture manifest, and optional reproducible capture scripts.
- Class report/checkpoints under `docs/submissions/` and clearly marked history
  under `docs/archive/`.

Generated synthetic outputs remain because the dashboard and offline walkthrough
use them. The teaching graph remains because active CLI commands and tests use it.

## Archive Map

| Location | Historical material |
| --- | --- |
| `docs/archive/team_prototype/` | Shared code, notebook, RAG experiment, and old root environment template |
| `docs/archive/class_docs/` | Planning, backlog, solo work log, review draft, and retired Week 6 packaging helper |
| `docs/archive/old_screenshots/` | Earlier prototype images |
| `docs/archive/design/` | Original HTML dashboard mockup |
| `docs/submissions/final_report/` | Report artifact and distinct earlier drafts/context |

Archives retain historical content and may contain old paths or assumptions.
The retired packaging script is reference material, not an active build command.
Archiving does not erase commit history or reassign authorship.

## Local-Only Material

`.env`, OAuth credentials/tokens, live raw/processed reports, correction history,
SQLite checkpoints, caches, comparison checkouts, test artifacts, and ZIP output
are excluded from Git. Existing secrets and runtime data are not moved into
archives or included as demo evidence. The public app must remain synthetic until
access controls and persistence are designed for workplace data.
