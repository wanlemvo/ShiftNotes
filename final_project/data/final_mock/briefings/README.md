# Generated Final Briefings

This directory contains:

- `weekly/week_01.md` through `weekly/week_12.md`
- `monthly/2026-03.md` through `monthly/2026-05.md`

Regenerate them from the repository root:

```bash
python final_project/src/shiftnotes/cli.py briefings
```

The weekly format is kiosk-centered. The monthly format emphasizes normalized
waste, operational trends, reporting compliance, and cautious management
priorities.

These Markdown files feed the implemented HTML/plain-text email renderer,
source-inspection workspace, claim-challenge flow, and optional Gmail delivery.
Hosted source links and automatic scheduling remain future work.
