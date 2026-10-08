"""Source-backed dashboard projections; no provider calls or persistence."""

from collections import defaultdict
from datetime import date, timedelta
from statistics import mean

from shiftnotes.baseline import deduplicate_reports
from shiftnotes.email_preview import claim_urgency


def is_recognition(claim: dict) -> bool:
    return "recognition" in claim["category"]


def dashboard_snapshot(reports, schedule, claims, start: date, end: date, kiosk=None):
    if end < start:
        raise ValueError("End date must be on or after start date.")
    start_text, end_text = start.isoformat(), end.isoformat()

    def included(row):
        return (start_text <= str(row.get("date", "")) <= end_text
                and (kiosk is None or row.get("kiosk") == kiosk))

    scoped = [r for r in reports if included(r)]
    unique, duplicates = deduplicate_reports(scoped)
    valid = [r for r in unique if r.get("parse_status") == "valid"]
    lookup = {str(r["source_submission_id"]): r for r in valid}
    slots = {(r["kiosk"], r["date"]): r for r in schedule if included(r)}
    received = {(r["kiosk"], r["date"]) for r in unique}
    missing = [r for slot, r in sorted(slots.items()) if slot not in received]

    # Weekly claims are the single counting basis; monthly claims repeat sources.
    groups = {}
    for claim in claims:
        if claim["period_type"] != "weekly":
            continue
        ids = set(claim["source_submission_ids"]) & lookup.keys()
        if not ids:
            continue
        key = (claim["kiosk"], claim["category"])
        group = groups.setdefault(key, {
            "kiosk": claim["kiosk"], "category": claim["category"],
            "label": claim["label"], "source_ids": set(), "claim_ids": [],
            "sensitive": False,
        })
        group["source_ids"].update(ids)
        group["claim_ids"].append(claim["claim_id"])
        group["sensitive"] |= claim.get("sensitive", False)

    findings = []
    for group in groups.values():
        dates = {lookup[s]["date"] for s in group["source_ids"]}
        weeks = {
            (date.fromisoformat(d) - timedelta(days=date.fromisoformat(d).weekday())).isoformat()
            for d in dates
        }
        finding = {**group, "source_ids": sorted(group["source_ids"]),
                   "source_count": len(group["source_ids"]),
                   "reporting_days": len(dates), "weeks_observed": len(weeks)}
        finding["priority"] = claim_urgency(finding)
        finding["recognition"] = is_recognition(finding)
        findings.append(finding)
    rank = {"urgent": 0, "important": 1, "monitor": 2}
    findings.sort(key=lambda f: (rank[f["priority"]], -f["source_count"], f["kiosk"], f["label"]))
    issues = [f for f in findings if not f["recognition"]]
    recognition_ids = {s for f in findings if f["recognition"] for s in f["source_ids"]}

    def metrics(rows):
        def average(field):
            values = [r[field] for r in rows if r.get(field) is not None]
            return round(mean(values), 2) if values else None
        return {"valid_reports": len(rows), "quality": average("food_quality_rating"),
                "quantity": average("food_quantity_rating"),
                "unclaimed": sum(r.get("number_of_unclaimed_lunches") or 0 for r in rows)}

    summary = {**metrics(valid), "received": len(unique), "expected": len(slots),
               "received_slots": len(received & slots.keys()), "missing": len(missing),
               "duplicates": len(duplicates), "invalid": len(unique) - len(valid),
               "urgent": sum(f["priority"] == "urgent" for f in issues),
               "recurring": sum(f["reporting_days"] >= 2 for f in issues),
               "recognition": len(recognition_ids)}

    kiosks = sorted({r["kiosk"] for r in unique} | {r["kiosk"] for r in slots.values()})
    comparison = []
    for name in kiosks:
        rows = [r for r in valid if r["kiosk"] == name]
        row_metrics = metrics(rows)
        comparison.append({"Kiosk": name, "Valid reports": len(rows),
                           "Quality": row_metrics["quality"], "Quantity": row_metrics["quantity"],
                           "Unclaimed": row_metrics["unclaimed"],
                           "Unclaimed / report": round(row_metrics["unclaimed"] / len(rows), 2) if rows else None,
                           "Missing": sum(r["kiosk"] == name for r in missing),
                           "Urgent findings": sum(f["kiosk"] == name and f["priority"] == "urgent" for f in issues)})

    daily = (end - start).days < 14
    def bucket(value):
        day = date.fromisoformat(value)
        return (day if daily else day - timedelta(days=day.weekday())).isoformat()

    buckets = sorted({bucket(r["date"]) for r in slots.values()} | {bucket(r["date"]) for r in unique})
    event_ids = defaultdict(set)
    for finding in issues:
        for source_id in finding["source_ids"]:
            event_ids[bucket(lookup[source_id]["date"])].add((finding["category"], source_id))
    trends = []
    for period in buckets:
        rows = [r for r in valid if bucket(r["date"]) == period]
        trends.append({"Date": period, **metrics(rows),
                       "missing": sum(bucket(r["date"]) == period for r in missing),
                       "issues": len(event_ids[period])})

    return {"summary": summary, "findings": findings, "comparison": comparison,
            "trends": trends, "missing": missing, "valid_reports": valid,
            "invalid_reports": [r for r in unique if r.get("parse_status") != "valid"],
            "daily": daily}
