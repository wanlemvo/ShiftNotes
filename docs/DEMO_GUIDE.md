# ShiftNotes Demo Guide

This demo should feel email-first. The dashboard is supporting evidence, not the
main workplace interface.

## Primary Story

Ted already receives shift-note reports. ShiftNotes reads JotForm-style report
data, cleans it, identifies source-backed trends, and sends a weekly or monthly
briefing. Ted only opens the dashboard when he wants to inspect evidence or
challenge a claim.

## Recommended Demo Flow

1. Open the hosted app:

   ```text
   https://shiftnotes.streamlit.app
   ```

2. Start with a weekly briefing and explain the source data:

   ```text
   demo/data/final_mock/email_previews/weekly/week_01.html
   ```

3. Point out the briefing sections:

   - reporting completeness;
   - average food quality and quantity;
   - unclaimed lunch / waste indicators;
   - immediate-attention findings;
   - important follow-up findings;
   - monitor and recognition findings;
   - source links for inspection.

4. Open a source-backed claim in the Streamlit workspace.

5. Show the original source reports supporting the claim.

6. Challenge a claim in ordinary English, for example:

   ```text
   This is wrong. Remove FM-0001 because that report was praise, not a complaint.
   ```

7. Show that ShiftNotes proposes a correction first.

8. Confirm or cancel the correction to demonstrate the human-in-the-loop
   checkpoint.

9. Show correction history.

10. Explain Gmail delivery:

   ```bash
   python demo/src/shiftnotes/cli.py gmail-preview --type weekly --period week-01
   python demo/src/shiftnotes/cli.py gmail-send --type weekly --period week-01 --confirm-send
   ```

## What To Emphasize

- The useful product is the email briefing.
- Every claim is traceable to source reports.
- The manager can inspect claims instead of trusting the model blindly.
- Sensitive personnel notes are treated as private review items, not automatic
  accusations.
- The prototype uses synthetic data for safety, but the records match the
  JotForm-style structure used in the workplace.

## Setup Explanation For Ted

For a workplace pilot, setup would require:

- access to the JotForm account or form API key;
- a Google OAuth client for Gmail sending;
- a configured recipient email;
- a scheduled weekly/monthly job;
- synthetic demo data replaced with Ted's real form submissions;
- authentication before using real source reports in the dashboard.

