#!/usr/bin/env python3
"""Audit a trip plan for structure, timing, MUST items, meals, rest, and budget."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def minute(value: str) -> int:
    hour, minute_value = value.split(":", 1)
    result = int(hour) * 60 + int(minute_value)
    if result < 0 or result >= 24 * 60:
        raise ValueError(f"invalid time: {value}")
    return result


def warn(items: list[dict], scope: str, issue: str) -> None:
    items.append({"scope": scope, "issue": issue})


def audit(plan: dict) -> dict:
    trip = plan.get("trip", {})
    warnings: list[dict] = []
    total = sum(float(value or 0) for value in plan.get("fixed_costs_per_person", {}).values())
    days = plan.get("days", [])
    declared_days = int(trip.get("days", len(days)))
    people = max(int(trip.get("people", 1)), 1)
    budget = float(trip.get("budget_per_person") or 0)
    max_steps = trip.get("max_steps_per_day")
    max_drive = trip.get("max_drive_min_per_day")
    rest_interval = int(trip.get("rest_interval_min") or 120)
    earliest = minute(trip.get("earliest_start", "00:00"))
    latest = minute(trip.get("latest_end", "23:59"))

    if len(days) != declared_days:
        warn(warnings, "trip", "declared day count differs from scheduled day count")

    for day in days:
        label = f"day {day.get('day', '?')}"
        regions = list(dict.fromkeys(region for region in day.get("regions", []) if region))
        if len(regions) > 2 and not day.get("transfer_day"):
            warn(warnings, label, f"uses {len(regions)} regions: {', '.join(regions)}")

        steps = day.get("estimated_steps")
        if max_steps is not None and steps is not None and float(steps) > float(max_steps):
            warn(warnings, label, f"estimated steps {steps} exceed limit {max_steps}")

        declared_drive = float(day.get("estimated_drive_min") or 0)
        if max_drive is not None and declared_drive > float(max_drive):
            warn(warnings, label, f"estimated driving {declared_drive} minutes exceeds limit {max_drive}")

        events = sorted(day.get("events", []), key=lambda event: minute(event["start"]))
        meals = {"breakfast": False, "lunch": False, "dinner": False}
        previous_end = None
        continuous_drive = 0
        drive_from_events = 0

        for event in events:
            start = minute(event["start"])
            end = minute(event["end"])
            name = event.get("name", "unnamed event")
            kind = event.get("kind")
            total += float(event.get("cost_per_person") or 0)

            if end <= start:
                warn(warnings, label, f"{name} has a non-positive duration")
            if previous_end is not None and start < previous_end:
                warn(warnings, label, f"{name} overlaps the previous event")
            previous_end = max(previous_end or end, end)
            if start < earliest or end > latest:
                warn(warnings, label, f"{name} is outside the traveler's daily window")

            if event.get("open") and start < minute(event["open"]):
                warn(warnings, label, f"{name} starts before opening")
            if event.get("close") and end > minute(event["close"]):
                warn(warnings, label, f"{name} ends after closing")
            if event.get("latest_entry") and start > minute(event["latest_entry"]):
                warn(warnings, label, f"{name} starts after last entry")
            if event.get("must") and not event.get("verified"):
                warn(warnings, label, f"MUST item {name} is not verified")

            if kind == "meal":
                meal = event.get("meal")
                if meal in meals:
                    meals[meal] = True
                elif 5 * 60 <= start < 10 * 60:
                    meals["breakfast"] = True
                elif 10 * 60 <= start < 15 * 60:
                    meals["lunch"] = True
                elif 16 * 60 <= start < 22 * 60:
                    meals["dinner"] = True

            if kind == "transit" and float(event.get("drive_min") or 0) > 0:
                drive = float(event.get("drive_min") or 0)
                continuous_drive += drive
                drive_from_events += drive
                if continuous_drive > rest_interval:
                    warn(warnings, label, f"continuous driving reaches {continuous_drive} minutes before a rest")
            elif kind != "transit":
                continuous_drive = 0

        if declared_drive and abs(drive_from_events - declared_drive) > 15:
            warn(warnings, label, "declared driving time differs from transit-event driving time by more than 15 minutes")
        for meal, present in meals.items():
            if not present and not day.get("meal_waiver", {}).get(meal):
                warn(warnings, label, f"missing {meal}")

    result = {
        "destination": trip.get("destination"),
        "scheduled_days": len(days),
        "estimated_per_person": round(total, 2),
        "estimated_total_party": round(total * people, 2),
        "budget_per_person": round(budget, 2),
        "remaining_per_person": round(budget - total, 2),
        "warning_count": len(warnings),
        "warnings": warnings,
    }
    if budget and total > budget:
        warn(result["warnings"], "budget", f"over budget by {round(total - budget, 2)} per person")
        result["warning_count"] += 1
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--strict", action="store_true", help="exit 1 when warnings exist")
    args = parser.parse_args()
    try:
        data = json.loads(args.plan.read_text(encoding="utf-8"))
        result = audit(data)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if args.strict and result["warning_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
  
