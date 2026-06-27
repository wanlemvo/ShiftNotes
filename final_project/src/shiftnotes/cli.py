from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

from langgraph.types import Command

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shiftnotes.config import load_gmail_settings, load_groq_settings, load_settings
from shiftnotes.ai_benchmark import benchmark_semantic_extractions
from shiftnotes.analysis import analyze_reports, render_weekly_briefing
from shiftnotes.baseline import (
    build_baseline_analysis,
    load_schedule,
    render_baseline_briefing,
)
from shiftnotes.briefings import load_and_generate
from shiftnotes.email_preview import (
    render_monthly_email,
    render_weekly_email,
    write_email_preview,
)
from shiftnotes.graph import build_persistent_graph
from shiftnotes.gmail_delivery import (
    authorize_gmail,
    load_email_preview,
    send_briefing,
)
from shiftnotes.jotform_client import fetch_form_submissions
from shiftnotes.normalize import normalize_submissions
from shiftnotes.product import build_claim_catalog, save_claim_catalog
from shiftnotes.scheduling import schedule_metadata
from shiftnotes.semantic import (
    GroqSemanticProvider,
    estimate_run_cost,
    extract_semantic_signals,
)
from shiftnotes.storage import (
    load_normalized_reports,
    save_analysis,
    save_briefing,
    save_normalized_reports,
    save_raw_submissions,
    read_json,
    write_json,
)


ROOT = Path(__file__).resolve().parents[3]
FINAL_MOCK_DIR = ROOT / "final_project" / "data" / "final_mock"


def fetch_command(args: argparse.Namespace) -> int:
    settings = load_settings()
    raw = fetch_form_submissions(
        settings.jotform_api_key,
        settings.jotform_form_id,
        limit=args.limit,
    )
    reports = normalize_submissions(raw)

    raw_path = save_raw_submissions(raw)
    reports_path = save_normalized_reports(reports)

    valid_count = sum(1 for report in reports if report["parse_status"] == "valid")
    review_count = len(reports) - valid_count

    print(f"Fetched {len(reports)} submissions from JotForm.")
    print(f"Valid records: {valid_count}")
    print(f"Needs review: {review_count}")
    print(f"Saved raw response: {raw_path}")
    print(f"Saved normalized reports: {reports_path}")
    return 0


def analyze_command(args: argparse.Namespace) -> int:
    reports = load_normalized_reports(args.input)
    expected_kiosks = args.expected_kiosk or None
    analysis = analyze_reports(reports, expected_kiosks=expected_kiosks)
    briefing = render_weekly_briefing(analysis)

    analysis_path = save_analysis(analysis)
    briefing_path = save_briefing(briefing)

    print(f"Analyzed {analysis['summary']['total_reports']} valid reports.")
    print(f"Generated {len(analysis['claims'])} source-backed claims.")
    print(f"Missing report flags: {len(analysis['missing_reports'])}")
    print(f"Saved analysis: {analysis_path}")
    print(f"Saved briefing: {briefing_path}")
    return 0


def baseline_command(args: argparse.Namespace) -> int:
    dataset_dir = args.dataset_dir
    reports = read_json(dataset_dir / "normalized_reports.json")
    schedule = load_schedule(dataset_dir / "expected_reporting_schedule.csv")
    ground_truth = read_json(dataset_dir / "ground_truth.json")

    analysis = build_baseline_analysis(reports, schedule, ground_truth)
    briefing = render_baseline_briefing(analysis)

    outputs = {
        "baseline_analysis.json": analysis,
        "weekly_summaries.json": analysis["weekly_summaries"],
        "monthly_summaries.json": analysis["monthly_summaries"],
        "reporting_completeness.json": analysis["reporting_completeness"],
        "benchmark_results.json": analysis["benchmark"],
    }
    for filename, value in outputs.items():
        write_json(dataset_dir / filename, value)
    briefing_path = dataset_dir / "baseline_briefing.md"
    briefing_path.write_text(briefing, encoding="utf-8")

    completeness = analysis["reporting_completeness"]
    benchmark = analysis["benchmark"]["summary"]
    print(f"Analyzed {analysis['dataset']['valid_unique_reports']} valid unique reports.")
    print(f"Removed duplicates: {analysis['cleaning']['duplicates_removed']}")
    print(f"Malformed reports: {completeness['malformed_report_count']}")
    print(f"Missing kiosk/date reports: {completeness['missing_report_count']}")
    print(
        "Exact event category matches: "
        f"{benchmark['exact_event_category_matches']}/"
        f"{benchmark['event_categories_scored']}"
    )
    print(f"Saved baseline artifacts: {dataset_dir}")
    return 0


def briefings_command(args: argparse.Namespace) -> int:
    generated = load_and_generate(args.dataset_dir)
    print(f"Generated weekly briefings: {len(generated['weekly'])}")
    print(f"Generated monthly briefings: {len(generated['monthly'])}")
    print(f"Saved briefings: {args.dataset_dir / 'briefings'}")
    return 0


def product_assets_command(args: argparse.Namespace) -> int:
    dataset_dir = args.dataset_dir
    reports = read_json(dataset_dir / "normalized_reports.json")
    schedule = load_schedule(dataset_dir / "expected_reporting_schedule.csv")
    ai_path = dataset_dir / "ai_extractions.json"
    semantic_extractions = read_json(ai_path) if ai_path.exists() else None
    claims = build_claim_catalog(
        reports,
        schedule,
        semantic_extractions=semantic_extractions,
    )
    save_claim_catalog(dataset_dir / "claims.json", claims)

    preview_dir = dataset_dir / "email_previews"
    manifest: list[dict] = []
    weekly_dir = dataset_dir / "briefings" / "weekly"
    monthly_dir = dataset_dir / "briefings" / "monthly"

    for path in sorted(weekly_dir.glob("week_*.md")):
        period = path.stem.replace("_", "-")
        period_claims = [
            claim
            for claim in claims
            if claim["period_type"] == "weekly" and claim["period"] == period
        ]
        preview = render_weekly_email(
            path.read_text(encoding="utf-8"),
            period_claims,
            base_url=args.base_url,
        )
        html_path, text_path = write_email_preview(
            preview_dir / "weekly",
            path.stem,
            preview,
        )
        manifest.append(
            {
                "type": "weekly",
                "period": period,
                "subject": preview["subject"],
                "html_path": str(html_path.relative_to(dataset_dir)),
                "text_path": str(text_path.relative_to(dataset_dir)),
            }
        )

    for path in sorted(monthly_dir.glob("*.md")):
        period = path.stem
        period_claims = [
            claim
            for claim in claims
            if claim["period_type"] == "monthly" and claim["period"] == period
        ]
        preview = render_monthly_email(
            path.read_text(encoding="utf-8"),
            period_claims,
            base_url=args.base_url,
        )
        html_path, text_path = write_email_preview(
            preview_dir / "monthly",
            path.stem,
            preview,
        )
        manifest.append(
            {
                "type": "monthly",
                "period": period,
                "subject": preview["subject"],
                "html_path": str(html_path.relative_to(dataset_dir)),
                "text_path": str(text_path.relative_to(dataset_dir)),
            }
        )

    write_json(dataset_dir / "email_manifest.json", manifest)
    write_json(
        ROOT / "final_project" / "schedule_policy.json",
        schedule_metadata(),
    )
    print(f"Generated claims: {len(claims)}")
    print(f"Generated email previews: {len(manifest)}")
    print(f"Saved product assets: {dataset_dir}")
    return 0


def ai_run_command(args: argparse.Namespace) -> int:
    dataset_dir = args.dataset_dir
    reports = read_json(dataset_dir / "normalized_reports.json")
    valid_reports = [
        report for report in reports
        if report.get("parse_status") == "valid"
    ]
    if args.limit is not None:
        valid_reports = valid_reports[: args.limit]

    try:
        settings = load_groq_settings()
    except RuntimeError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    provider = GroqSemanticProvider(
        api_key=settings.api_key,
        model=settings.model,
    )
    run = extract_semantic_signals(
        valid_reports,
        provider,
        cache_dir=ROOT / "final_project" / "data" / "ai_cache",
        batch_size=args.batch_size,
        max_retries=args.max_retries,
        retry_delay_seconds=args.retry_delay,
    )
    ground_truth = read_json(dataset_dir / "ground_truth.json")
    analyzed_ids = {
        str(result["source_submission_id"])
        for result in run.reports
    }
    benchmark = benchmark_semantic_extractions(
        run.reports,
        ground_truth,
        analyzed_ids,
    )
    write_json(dataset_dir / "ai_extractions.json", run.reports)
    run_summary = {
        key: value
        for key, value in run.to_dict().items()
        if key != "reports"
    }
    run_summary["estimated_cost_usd"] = estimate_run_cost(
        run.model,
        run.prompt_tokens,
        run.completion_tokens,
    )
    write_json(dataset_dir / "ai_run_summary.json", run_summary)
    write_json(dataset_dir / "ai_benchmark_results.json", benchmark)

    summary = benchmark["summary"]
    print(f"Semantic reports processed: {len(run.reports)}")
    print(f"Groq model: {run.model}")
    print(f"Cache hits: {run.cache_hits}")
    print(f"Retries: {run.retries}")
    print(f"Fallback batches: {run.fallback_batches}")
    print(f"Total tokens: {run.total_tokens}")
    print(f"Estimated API cost: ${run_summary['estimated_cost_usd'] or 0:.6f}")
    print(f"Micro precision: {summary['micro_precision']}%")
    print(f"Micro recall: {summary['micro_recall']}%")
    print(f"Saved AI artifacts: {dataset_dir}")
    return 0


def gmail_auth_command(args: argparse.Namespace) -> int:
    settings = load_gmail_settings()
    credentials = authorize_gmail(
        settings.client_secret_path,
        settings.token_path,
    )
    print("Gmail authorization succeeded.")
    print(f"Token saved locally: {settings.token_path}")
    print(f"Authorized scopes: {', '.join(credentials.scopes or [])}")
    return 0


def gmail_send_command(args: argparse.Namespace) -> int:
    if not args.confirm_send:
        print(
            "Refusing to send without --confirm-send. "
            "Use gmail-preview to inspect the selected message.",
            file=sys.stderr,
        )
        return 2

    settings = load_gmail_settings()
    recipient = args.to or settings.default_recipient
    if not recipient:
        print(
            "Missing recipient. Use --to or set GMAIL_DEFAULT_RECIPIENT.",
            file=sys.stderr,
        )
        return 2

    try:
        preview = load_email_preview(
            args.dataset_dir,
            args.type,
            args.period,
        )
        credentials = authorize_gmail(
            settings.client_secret_path,
            settings.token_path,
        )
        result = send_briefing(
            recipient=recipient,
            subject=preview["subject"],
            text_body=preview["text"],
            html_body=preview["html"],
            credentials=credentials,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"Gmail delivery error: {exc}", file=sys.stderr)
        return 2

    print(f"Sent {args.type} briefing to {recipient}.")
    print(f"Gmail message ID: {result.get('id', 'unknown')}")
    return 0


def gmail_preview_command(args: argparse.Namespace) -> int:
    try:
        preview = load_email_preview(
            args.dataset_dir,
            args.type,
            args.period,
        )
    except (RuntimeError, ValueError) as exc:
        print(f"Email preview error: {exc}", file=sys.stderr)
        return 2
    settings = load_gmail_settings()
    recipient = args.to or settings.default_recipient or "(not configured)"
    print(f"To: {recipient}")
    print(f"Subject: {preview['subject']}")
    print(f"HTML bytes: {len(preview['html'].encode('utf-8'))}")
    print(f"Plain-text bytes: {len(preview['text'].encode('utf-8'))}")
    print("No email was sent.")
    return 0


def workflow_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def print_workflow_result(result: dict, thread_id: str) -> None:
    print(f"Thread ID: {thread_id}")
    print(f"Status: {result.get('status', 'unknown')}")
    for entry in result.get("execution_log", []):
        print(f"LOG {entry}")

    interrupts = result.get("__interrupt__", [])
    if interrupts:
        request = interrupts[0].value
        print("HITL INTERRUPT: workflow paused before briefing finalization.")
        print(f"Review options: {', '.join(request.get('options', []))}")
        print("Resume with:")
        print(
            "python final_project/src/shiftnotes/cli.py workflow-resume "
            f"{thread_id} approve"
        )


def workflow_start_command(args: argparse.Namespace) -> int:
    thread_id = args.thread_id or f"shiftnotes-{uuid.uuid4().hex[:8]}"
    initial_state = {
        "thread_id": thread_id,
        "mode": args.mode,
        "reporting_period": args.reporting_period,
        "expected_kiosks": args.expected_kiosk or ["Bowls & Buns"],
        "limit": args.limit,
        "max_retries": args.max_retries,
        "retry_count": 0,
        "simulate_failures": args.simulate_failures,
        "execution_log": [],
    }

    with build_persistent_graph() as runtime:
        result = runtime.graph.invoke(initial_state, workflow_config(thread_id))
    print_workflow_result(result, thread_id)
    return 1 if result.get("status") == "failed" else 0


def workflow_resume_command(args: argparse.Namespace) -> int:
    response = {"decision": args.decision, "note": args.note or ""}
    with build_persistent_graph() as runtime:
        result = runtime.graph.invoke(
            Command(resume=response),
            workflow_config(args.thread_id),
        )

    print_workflow_result(result, args.thread_id)
    if result.get("final_briefing"):
        briefing_path = save_briefing(
            result["final_briefing"],
            filename=f"weekly_briefing_{args.thread_id}.md",
        )
        print(f"Saved finalized briefing: {briefing_path}")
    return 1 if result.get("status") in {"failed", "rejected"} else 0


def workflow_status_command(args: argparse.Namespace) -> int:
    with build_persistent_graph() as runtime:
        snapshot = runtime.graph.get_state(workflow_config(args.thread_id))

    if not snapshot.values:
        print(f"No checkpoint found for thread: {args.thread_id}")
        return 1

    print(f"Thread ID: {args.thread_id}")
    print(f"Status: {snapshot.values.get('status', 'unknown')}")
    print(f"Next nodes: {', '.join(snapshot.next) if snapshot.next else 'none'}")
    for entry in snapshot.values.get("execution_log", []):
        print(f"LOG {entry}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ShiftNotes final project CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch = subparsers.add_parser("fetch", help="Fetch and normalize JotForm submissions")
    fetch.add_argument("--limit", type=int, default=100)
    fetch.set_defaults(func=fetch_command)

    analyze = subparsers.add_parser("analyze", help="Analyze normalized reports and generate a briefing")
    analyze.add_argument("--input", type=Path, default=None)
    analyze.add_argument(
        "--expected-kiosk",
        action="append",
        help="Expected kiosk name. Repeat for multiple kiosks to enable missing-report checks.",
    )
    analyze.set_defaults(func=analyze_command)

    baseline = subparsers.add_parser(
        "baseline",
        help="Run schedule-aware cleaning, summaries, and ground-truth benchmarking",
    )
    baseline.add_argument(
        "--dataset-dir",
        type=Path,
        default=FINAL_MOCK_DIR,
    )
    baseline.set_defaults(func=baseline_command)

    briefings = subparsers.add_parser(
        "briefings",
        help="Generate final weekly and monthly management briefings",
    )
    briefings.add_argument(
        "--dataset-dir",
        type=Path,
        default=FINAL_MOCK_DIR,
    )
    briefings.set_defaults(func=briefings_command)

    product_assets = subparsers.add_parser(
        "product-assets",
        help="Generate claim catalog, email previews, and schedule policy",
    )
    product_assets.add_argument(
        "--dataset-dir",
        type=Path,
        default=FINAL_MOCK_DIR,
    )
    product_assets.add_argument(
        "--base-url",
        default="http://localhost:8501",
    )
    product_assets.set_defaults(func=product_assets_command)

    ai_run = subparsers.add_parser(
        "ai-run",
        help="Extract source-backed semantic signals with Groq and benchmark them",
    )
    ai_run.add_argument(
        "--dataset-dir",
        type=Path,
        default=FINAL_MOCK_DIR,
    )
    ai_run.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only the first N valid reports for a controlled validation run.",
    )
    ai_run.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Reports per Groq request. One is the reliability-first default.",
    )
    ai_run.add_argument("--max-retries", type=int, default=2)
    ai_run.add_argument("--retry-delay", type=float, default=1.0)
    ai_run.set_defaults(func=ai_run_command)

    gmail_auth = subparsers.add_parser(
        "gmail-auth",
        help="Authorize ShiftNotes to send Gmail messages",
    )
    gmail_auth.set_defaults(func=gmail_auth_command)

    gmail_preview = subparsers.add_parser(
        "gmail-preview",
        help="Inspect the exact generated briefing selected for Gmail delivery",
    )
    gmail_preview.add_argument("--type", choices=("weekly", "monthly"), required=True)
    gmail_preview.add_argument("--period", required=True)
    gmail_preview.add_argument("--to")
    gmail_preview.add_argument(
        "--dataset-dir",
        type=Path,
        default=FINAL_MOCK_DIR,
    )
    gmail_preview.set_defaults(func=gmail_preview_command)

    gmail_send = subparsers.add_parser(
        "gmail-send",
        help="Send a generated briefing through the Gmail API",
    )
    gmail_send.add_argument("--type", choices=("weekly", "monthly"), required=True)
    gmail_send.add_argument("--period", required=True)
    gmail_send.add_argument("--to")
    gmail_send.add_argument(
        "--dataset-dir",
        type=Path,
        default=FINAL_MOCK_DIR,
    )
    gmail_send.add_argument(
        "--confirm-send",
        action="store_true",
        help="Required acknowledgement that this command sends a real email.",
    )
    gmail_send.set_defaults(func=gmail_send_command)

    workflow_start = subparsers.add_parser(
        "workflow-start",
        help="Start the persistent LangGraph workflow and pause for HITL review",
    )
    workflow_start.add_argument("--thread-id")
    workflow_start.add_argument("--mode", choices=("demo", "live"), default="demo")
    workflow_start.add_argument("--reporting-period", default="weekly")
    workflow_start.add_argument("--expected-kiosk", action="append")
    workflow_start.add_argument("--limit", type=int, default=100)
    workflow_start.add_argument("--max-retries", type=int, default=2)
    workflow_start.add_argument("--simulate-failures", type=int, default=0)
    workflow_start.set_defaults(func=workflow_start_command)

    workflow_resume = subparsers.add_parser(
        "workflow-resume",
        help="Resume a paused LangGraph workflow with a human decision",
    )
    workflow_resume.add_argument("thread_id")
    workflow_resume.add_argument("decision", choices=("approve", "correct", "reject"))
    workflow_resume.add_argument("--note")
    workflow_resume.set_defaults(func=workflow_resume_command)

    workflow_status = subparsers.add_parser(
        "workflow-status",
        help="Inspect the persisted state of a LangGraph workflow",
    )
    workflow_status.add_argument("thread_id")
    workflow_status.set_defaults(func=workflow_status_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
