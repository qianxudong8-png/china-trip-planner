#!/usr/bin/env python3
"""Audit a trip plan for structure, timing, MUST items, meals, rest, and budget."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


def minute(value: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]", value):
        raise ValueError(f"invalid time: {value}")
    hour, minute_value = value.split(":")
    return int(hour) * 60 + int(minute_value)


def positive_integer(value: object, field: str) -> None:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{field} must be a positive integer")


def nonnegative_number(value: object, field: str) -> None:
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{field} must be a finite non-negative number")


def validate_plan(plan: object) -> None:
    if not isinstance(plan, dict):
        raise ValueError("plan must be an object")
    trip = plan.get("trip")
    if not isinstance(trip, dict):
        raise ValueError("trip must be an object")
    for field in ("days", "people"):
        positive_integer(trip.get(field), f"trip.{field}")
    for field in ("rest_interval_min", "min_rest_min"):
        if field in trip:
            positive_integer(trip[field], f"trip.{field}")
    for field in ("budget_per_person", "max_steps_per_day", "max_drive_min_per_day"):
        if trip.get(field) is not None:
            nonnegative_number(trip[field], f"trip.{field}")
    if minute(trip.get("earliest_start", "00:00")) >= minute(trip.get("latest_end", "23:59")):
        raise ValueError("daily window must end after it starts; split overnight events across days")
    fixed = plan.get("fixed_costs_per_person", {})
    if not isinstance(fixed, dict):
        raise ValueError("fixed_costs_per_person must be an object")
    for field, value in fixed.items():
        nonnegative_number(value, f"fixed_costs_per_person.{field}")
    days = plan.get("days")
    if not isinstance(days, list) or not days:
        raise ValueError("days must be a non-empty list")
    seen_days = set()
    for day in days:
        if not isinstance(day, dict):
            raise ValueError("each day must be an object")
        positive_integer(day.get("day"), "day.day")
        if day["day"] in seen_days or day["day"] > trip["days"]:
            raise ValueError("day numbers must be unique and within trip.days")
        seen_days.add(day["day"])
        regions = day.get("regions", [])
        if not isinstance(regions, list) or any(not isinstance(r, str) for r in regions):
            raise ValueError("regions must be a list of strings")
        if not isinstance(day.get("meal_waiver", {}), dict):
            raise ValueError("meal_waiver must be an object")
        for field in ("estimated_steps", "estimated_drive_min"):
            if day.get(field) is not None:
                nonnegative_number(day[field], field)
        events = day.get("events")
        if not isinstance(events, list) or not events:
            raise ValueError(f"day {day['day']} events must be a non-empty list; finish the draft before auditing")
        for event in events:
            if not isinstance(event, dict):
                raise ValueError("each event must be an object")
            start, end = minute(event.get("start")), minute(event.get("end"))
            for field in ("open", "close", "latest_entry"):
                if event.get(field) is not None:
                    minute(event[field])
            for field in ("cost_per_person", "drive_min"):
                if field in event:
                    nonnegative_number(event[field], field)
            drive = event.get("drive_min", 0)
            if drive and (event.get("kind") != "transit" or drive > end - start):
                raise ValueError("drive_min must fit inside a transit event")


def warn(items: list[dict], scope: str, issue: str) -> None:
    items.append({"scope": scope, "issue": issue})


def audit(plan: dict) -> dict:
    validate_plan(plan)
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
    min_rest = trip.get("min_rest_min", 20)
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
            # Only the non-overlapping portion of a named rest or meal counts.
            available_rest = end - max(start, previous_end if previous_end is not None else start)
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
            elif kind in ("rest", "meal") and available_rest >= min_rest:
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
  
