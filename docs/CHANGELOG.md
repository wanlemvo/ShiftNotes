# Change Log

Significant independent changes after the class submission are recorded here.
Earlier decisions remain in the [solo work log](archive/class_docs/SOLO_WORK_LOG.md).

## 2026-10-08 - Dashboard Integration and Repository Presentation

Requested: give ShiftNotes the clear product/documentation structure used in
NetOps, integrate the newer dashboard design, archive inactive material, and
prepare changes locally without pushing.

- Added a data-backed dashboard with date/kiosk filters, eight metrics,
  prioritized findings, trend charts, comparison/export, recognition, missing
  dates, and links to the existing correction workflow.
- Reused the priority and deduplication rules. Aggregated weekly claims once per
  category/source to avoid double-counting monthly summaries.
- Preserved email-first delivery and human confirmation. Escaped claim text in
  HTML, hid correction proposals belonging to another selected claim, and fixed
  the challenge button's input/disabled interaction with blank-input feedback.
- Added regression coverage for filtering, missing-versus-invalid handling,
  duplicates, corrected sources, and empty periods.
- Rewrote the README; added documentation navigation, origins/ownership,
  compatibility boundaries, feature evidence, metric definitions, and publication
  policy. Updated stale setup links and clarified live-data integration gaps.
- Archived the standalone mockup, obsolete root environment template, class
  packaging helper, and interview response draft. Moved report-generation
  material alongside the class report. Preserved the earlier team archive.

Reason: make the repository legible to managers, collaborators, and hiring
reviewers, and make source inspection useful during leadership meetings.

Publication: local changes only. No push, merge, email send, or live provider run
was performed for this update. See [verification](VERIFICATION.md).

## 2026-10-08 - Public Demo Media and Release

The user subsequently authorized pushing this version and requested the same
at-a-glance presentation as NetOps.

- Added screenshots of briefings, analytics, comparison, sources, correction
  proposals, and history; an animated overview; and a continuous UI recording.
- Captured from an isolated synthetic dataset with no credentials or pre-existing
  local corrections. The scripted proposal is canceled, not accepted as a real
  correction or represented as user-validation evidence.
- Added reproducible capture scripts and linked media from the product README.
- Replaced the source drawer's JSON-style display with readable report fields
  so managers can inspect the notes directly during the demo.
- Installed the locked environment in a fresh source snapshot and ran all 58
  tests successfully. Generated 399 claims and 15 email previews there without
  provider calls or sending email.
- Published release `89157b1` to GitHub `main`, preserving existing commit history and
  older branches. See verification notes for the remote and hosting results.
- Found that the recorded Streamlit source branch, `codex/final-submission`, had
  been renamed to `main`. Restored it at the same commit as a hosting compatibility
  branch; the canonical project remains on `main`.
