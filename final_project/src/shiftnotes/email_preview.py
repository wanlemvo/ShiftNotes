from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any


COLORS = {
    "ink": "#17212b",
    "muted": "#5f6b76",
    "line": "#dce2e7",
    "paper": "#ffffff",
    "canvas": "#f4f6f7",
    "teal": "#0f766e",
    "teal_soft": "#e7f5f2",
    "amber": "#a16207",
    "amber_soft": "#fef3c7",
    "red": "#b42318",
    "red_soft": "#fee4e2",
}


def render_weekly_email(
    weekly_markdown: str,
    claims: list[dict[str, Any]],
    *,
    base_url: str = "http://localhost:8501",
) -> dict[str, str]:
    period = extract_line(weekly_markdown, "Week ")
    reporting = extract_bullet(weekly_markdown, "Reporting:")
    quality = extract_bullet(weekly_markdown, "Average food quality:")
    quantity = extract_bullet(weekly_markdown, "Average food quantity:")
    unclaimed = extract_bullet(weekly_markdown, "Unclaimed lunches:")
    attention_claims = priority_claims(claims, limit=4)
    subject = weekly_subject(period, attention_claims)
    html_body = email_shell(
        eyebrow="Weekly operations briefing",
        title=period or "Weekly Operations Briefing",
        intro=(
            "A concise view of reporting health, kiosk performance, and the "
            "source-backed trends that may need attention."
        ),
        metrics=[
            ("Reporting", reporting),
            ("Food quality", quality),
            ("Food quantity", quantity),
            ("Unclaimed lunches", unclaimed),
        ],
        sections=(
            attention_section(attention_claims, base_url)
            + action_links(base_url)
            + limits_section()
        ),
    )
    return {
        "subject": subject,
        "html": html_body,
        "text": plain_text_email(
            title=period or "Weekly Operations Briefing",
            intro="Reporting health, kiosk performance, and source-backed trends.",
            metrics=[
                ("Reporting", reporting),
                ("Food quality", quality),
                ("Food quantity", quantity),
                ("Unclaimed lunches", unclaimed),
            ],
            claims=attention_claims,
            base_url=base_url,
        ),
    }


def render_monthly_email(
    monthly_markdown: str,
    claims: list[dict[str, Any]],
    *,
    base_url: str = "http://localhost:8501",
) -> dict[str, str]:
    lines = [line.strip() for line in monthly_markdown.splitlines() if line.strip()]
    period = lines[1] if len(lines) > 1 else "Monthly Operations Briefing"
    reporting = extract_bullet(monthly_markdown, "Reporting:")
    quality = extract_bullet(monthly_markdown, "Average food quality:")
    quantity = extract_bullet(monthly_markdown, "Average food quantity:")
    waste = extract_bullet(
        monthly_markdown,
        "Unclaimed lunches per valid report:",
    )
    attention_claims = priority_claims(claims, limit=5)
    subject = monthly_subject(period, monthly_markdown)
    html_body = email_shell(
        eyebrow="Monthly operations briefing",
        title=period,
        intro=(
            "Month-over-month direction, possible cost-saving signals, and "
            "management priorities before inventory planning."
        ),
        metrics=[
            ("Reporting", reporting),
            ("Food quality", quality),
            ("Food quantity", quantity),
            ("Unclaimed / report", waste),
        ],
        sections=(
            cost_signal_section(monthly_markdown)
            + attention_section(attention_claims, base_url)
            + action_links(base_url)
            + limits_section()
        ),
    )
    return {
        "subject": subject,
        "html": html_body,
        "text": plain_text_email(
            title=period,
            intro="Month-over-month direction, cost signals, and inventory planning priorities.",
            metrics=[
                ("Reporting", reporting),
                ("Food quality", quality),
                ("Food quantity", quantity),
                ("Unclaimed / report", waste),
            ],
            claims=attention_claims,
            base_url=base_url,
            extra_note=extract_bullet(monthly_markdown, "Possible impact:"),
        ),
    }


def write_email_preview(
    output_dir: Path,
    name: str,
    preview: dict[str, str],
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / f"{name}.html"
    text_path = output_dir / f"{name}.txt"
    html_path.write_text(preview["html"], encoding="utf-8")
    text_path.write_text(
        f"Subject: {preview['subject']}\n\n{preview['text']}",
        encoding="utf-8",
    )
    return html_path, text_path


def email_shell(
    *,
    eyebrow: str,
    title: str,
    intro: str,
    metrics: list[tuple[str, str]],
    sections: str,
) -> str:
    metric_cells = "".join(
        f"""
        <td style="width:25%;padding:12px 10px;border-right:1px solid {COLORS['line']};vertical-align:top">
          <div style="font-size:11px;text-transform:uppercase;color:{COLORS['muted']};font-weight:700">{html.escape(label)}</div>
          <div style="margin-top:5px;font-size:18px;color:{COLORS['ink']};font-weight:700">{html.escape(value or 'N/A')}</div>
        </td>
        """
        for label, value in metrics
    )
    return f"""<!doctype html>
<html>
<body style="margin:0;background:{COLORS['canvas']};font-family:Arial,Helvetica,sans-serif;color:{COLORS['ink']}">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:{COLORS['canvas']};padding:28px 12px">
    <tr><td align="center">
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="width:100%;max-width:680px;background:{COLORS['paper']};border:1px solid {COLORS['line']}">
        <tr><td style="padding:24px 30px 18px;border-bottom:4px solid {COLORS['teal']}">
          <div style="font-size:12px;letter-spacing:1px;text-transform:uppercase;color:{COLORS['teal']};font-weight:700">{html.escape(eyebrow)}</div>
          <h1 style="font-size:26px;line-height:1.2;margin:8px 0 8px">{html.escape(title)}</h1>
          <p style="font-size:15px;line-height:1.6;margin:0;color:{COLORS['muted']}">{html.escape(intro)}</p>
        </td></tr>
        <tr><td style="padding:0 20px">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>{metric_cells}</tr></table>
        </td></tr>
        <tr><td style="padding:22px 30px 30px">{sections}</td></tr>
        <tr><td style="padding:18px 30px;background:#eef2f3;color:{COLORS['muted']};font-size:12px;line-height:1.5">
          ShiftNotes summarizes submitted operational reports. Source reports remain available for inspection.
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def attention_section(
    claims: list[dict[str, Any]],
    base_url: str,
) -> str:
    if not claims:
        return section("Priority findings", "<p>No source-backed priority finding was selected.</p>")
    rows = []
    for claim in claims:
        tone = COLORS["red"] if claim["sensitive"] else COLORS["teal"]
        soft = COLORS["red_soft"] if claim["sensitive"] else COLORS["teal_soft"]
        source_ids = list(claim.get("source_submission_ids", []))
        visible_sources = ", ".join(source_ids[:6])
        if len(source_ids) > 6:
            visible_sources += f", +{len(source_ids) - 6} more"
        rows.append(
            f"""
            <div style="margin:0 0 12px;padding:14px 16px;border-left:4px solid {tone};background:{soft}">
              <div style="font-size:15px;font-weight:700">{html.escape(claim['claim_text'])}</div>
              <div style="margin-top:7px;font-size:13px;color:{COLORS['muted']}">
                {claim['source_count']} supporting {'report' if claim['source_count'] == 1 else 'reports'}
                {f" | Sources: {html.escape(visible_sources)}" if visible_sources else ""}
              </div>
              <div style="margin-top:10px">
                <a href="{base_url}?claim={claim['claim_id']}" style="color:{tone};font-weight:700;text-decoration:none">View sources</a>
                &nbsp;&nbsp;
                <a href="{base_url}?claim={claim['claim_id']}&action=challenge" style="color:{tone};font-weight:700;text-decoration:none">Challenge this claim</a>
              </div>
            </div>
            """
        )
    return section("Priority findings", "".join(rows))


def priority_claims(claims: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    concrete = [
        claim
        for claim in claims
        if "other_operational_issue" not in str(claim.get("category", ""))
    ]
    pool = concrete if len(concrete) >= limit else claims
    return sorted(
        pool,
        key=lambda claim: (
            bool(claim.get("sensitive")),
            int(claim.get("source_count", 0)),
            category_priority(str(claim.get("category", ""))),
        ),
        reverse=True,
    )[:limit]


def category_priority(category: str) -> int:
    if "sensitive_personnel" in category:
        return 100
    if "high_waste_or_overproduction" in category or "waste" in category:
        return 90
    if "food_shortage" in category:
        return 85
    if "equipment_failure" in category or "register_disruption" in category:
        return 80
    if "inventory_inconsistency" in category:
        return 78
    if "dietary_or_allergy_question" in category:
        return 72
    if "portion_complaint" in category:
        return 70
    if "beverage_request" in category:
        return 60
    if "employee_recognition" in category:
        return 45
    return 10


def plain_text_email(
    *,
    title: str,
    intro: str,
    metrics: list[tuple[str, str]],
    claims: list[dict[str, Any]],
    base_url: str,
    extra_note: str = "",
) -> str:
    lines = [
        title,
        "",
        intro,
        "",
        "At a glance",
    ]
    lines.extend(f"- {label}: {value or 'N/A'}" for label, value in metrics)
    if extra_note:
        lines.extend(["", "Cost and inventory signal", f"- {extra_note}"])
    lines.extend(["", "Priority findings"])
    if not claims:
        lines.append("- No source-backed priority finding was selected.")
    for claim in claims:
        sources = ", ".join(claim.get("source_submission_ids", [])[:8])
        if len(claim.get("source_submission_ids", [])) > 8:
            sources += f", +{len(claim['source_submission_ids']) - 8} more"
        lines.append(f"- {claim['claim_text']}")
        lines.append(f"  Sources: {sources or 'N/A'}")
        lines.append(f"  Inspect/challenge: {base_url}?claim={claim['claim_id']}")
    lines.extend(
        [
            "",
            "Open full briefing:",
            base_url,
            "",
            "Interpretation note: menu findings reflect only dishes explicitly named in reports. Financial impact remains a possible opportunity until meal-cost, volume, and labor data are available.",
        ]
    )
    return "\n".join(lines)


def cost_signal_section(markdown: str) -> str:
    signal = extract_bullet(markdown, "Possible impact:")
    if not signal:
        signal = (
            "Review per-report waste and preparation patterns before making "
            "inventory or production changes."
        )
    return section(
        "Cost and inventory signal",
        f"""<div style="padding:14px 16px;background:{COLORS['amber_soft']};border-left:4px solid {COLORS['amber']}">
        <strong>Possible opportunity</strong><br>
        <span style="font-size:14px;line-height:1.6;color:{COLORS['ink']}">{html.escape(signal)}</span>
        </div>""",
    )


def action_links(base_url: str) -> str:
    return f"""
    <div style="margin-top:24px;padding-top:20px;border-top:1px solid {COLORS['line']}">
      <a href="{base_url}" style="display:inline-block;padding:11px 16px;background:{COLORS['teal']};color:white;text-decoration:none;font-weight:700">Open full briefing</a>
      <a href="{base_url}?view=sources" style="display:inline-block;margin-left:8px;padding:10px 14px;border:1px solid {COLORS['teal']};color:{COLORS['teal']};text-decoration:none;font-weight:700">Inspect sources</a>
    </div>
    """


def limits_section() -> str:
    return section(
        "Interpretation note",
        (
            "<p style=\"font-size:12px;line-height:1.6;color:#5f6b76\">"
            "Menu findings reflect only dishes explicitly named in reports. "
            "Financial impact remains a possible opportunity until meal-cost, "
            "volume, and labor data are available.</p>"
        ),
    )


def section(title: str, body: str) -> str:
    return (
        f"<h2 style=\"font-size:17px;margin:24px 0 12px\">{html.escape(title)}</h2>"
        + body
    )


def extract_bullet(markdown: str, prefix: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith(f"- {prefix}"):
            return stripped[len(prefix) + 2 :].strip()
    return ""


def extract_line(markdown: str, prefix: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped
    return ""


def weekly_subject(period: str, claims: list[dict[str, Any]]) -> str:
    attention = len({claim["kiosk"] for claim in claims})
    return (
        f"ShiftNotes Weekly Briefing: {attention} "
        f"{'kiosk' if attention == 1 else 'kiosks'} need attention | {period}"
    )


def monthly_subject(period: str, markdown: str) -> str:
    quality = "Food quality updated"
    waste = "waste trend available"
    if "Food quality decreased" in markdown:
        quality = "Food quality declined"
    elif "Food quality increased" in markdown:
        quality = "Food quality improved"
    if "Unclaimed lunches per valid report decreased" in markdown:
        waste = "waste decreased"
    elif "Unclaimed lunches per valid report increased" in markdown:
        waste = "waste increased"
    return f"ShiftNotes Monthly Briefing: {waste}, {quality.lower()} | {period}"


def markdown_to_text(markdown: str) -> str:
    text = re.sub(r"^#{1,6}\s*", "", markdown, flags=re.MULTILINE)
    text = text.replace("**", "").replace("`", "")
    return text.strip()
