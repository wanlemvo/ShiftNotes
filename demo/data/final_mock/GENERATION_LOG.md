# Final Mock Dataset Generation Log

Generated deterministically for ShiftNotes.

- Seed: `20260621`
- Expected schedule rows: `288`
- Payload submissions: `273`
- Duplicate submissions: `3`
- Scheduled statuses: `{'malformed': 3, 'missing': 18, 'valid': 267}`
- Normalized statuses: `{'needs_review': 3, 'valid': 270}`
- Weeks: `12`
- Reporting dates: `48`

The generator can be rerun with:

```bash
python scripts/generate_final_mock_dataset.py
```
