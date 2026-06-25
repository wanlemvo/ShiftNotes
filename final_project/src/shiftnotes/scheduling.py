from __future__ import annotations

import calendar
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


PACIFIC = ZoneInfo("America/Los_Angeles")


@dataclass(frozen=True)
class SchedulePolicy:
    timezone: str = "America/Los_Angeles"
    weekly_weekday: str = "Thursday"
    weekly_time: str = "15:30"
    monthly_rule: str = "day_before_final_expected_reporting_day"
    monthly_time: str = "15:30"


def next_weekly_run(
    after: datetime,
    policy: SchedulePolicy = SchedulePolicy(),
) -> datetime:
    local = after.astimezone(ZoneInfo(policy.timezone))
    target_weekday = 3  # Thursday
    hour, minute = parse_time(policy.weekly_time)
    days_ahead = (target_weekday - local.weekday()) % 7
    candidate_date = local.date() + timedelta(days=days_ahead)
    candidate = datetime.combine(
        candidate_date,
        time(hour, minute),
        tzinfo=ZoneInfo(policy.timezone),
    )
    if candidate <= local:
        candidate += timedelta(days=7)
    return candidate


def monthly_inventory_briefing_date(year: int, month: int) -> date:
    final_day = calendar.monthrange(year, month)[1]
    current = date(year, month, final_day)
    while current.weekday() not in {0, 1, 2, 3}:
        current -= timedelta(days=1)
    return current - timedelta(days=1)


def schedule_metadata(policy: SchedulePolicy = SchedulePolicy()) -> dict:
    return asdict(policy)


def parse_time(value: str) -> tuple[int, int]:
    hour, minute = value.split(":", 1)
    return int(hour), int(minute)
