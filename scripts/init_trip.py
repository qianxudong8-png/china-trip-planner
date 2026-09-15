#!/usr/bin/env python3
"""Create reusable trip input, POI ledger, and plan JSON files."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--days", type=int, required=True)
    parser.add_argument("--people", type=int, default=1)
    parser.add_argument("--budget-per-person", type=float, default=0)
    parser.add_argument("--origin", default="")
    parser.add_argument("--intercity", choices=("unknown", "included", "excluded"), default="unknown",
                        help="Whether the budget includes round-trip intercity transport (default: unknown)")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.days < 1 or args.people < 1 or not math.isfinite(args.budget_per_person) or args.budget_per_person < 0:
        parser.error("days and people must be positive; budget must be finite and non-negative")

    args.folder.mkdir(parents=True, exist_ok=True)
    targets = [args.folder / name for name in ("trip-input.json", "poi-ledger.json", "plan.json")]
    existing = [str(path) for path in targets if path.exists()]
    if existing and not args.force:
        parser.error("refusing to overwrite existing files: " + ", ".join(existing))

    trip_input = {
        "destination": args.destination,
        "dates": {"start": None, "end": None, "season": None},
        "days": args.days,
        "nights": max(args.days - 1, 0),
        "people": args.people,
        "origin": args.origin,
        "budget": {"amount": args.budget_per_person, "basis": "per_person",
                   "intercity_included": {"unknown": None, "included": True, "excluded": False}[args.intercity]},
        "pace": "normal",
        "daily_window": {"start": "09:00", "end": "22:00"},
        "transport": [],
        "interests": [],
        "must_go": [],
        "must_eat": [],
        "constraints": [],
        "dislikes": [],
        "assumptions": [],
    }
    plan = {
        "trip": {
            "destination": args.destination,
            "days": args.days,
            "people": args.people,
            "budget_per_person": args.budget_per_person,
            "pace": "normal",
            "earliest_start": "09:00",
            "latest_end": "22:00",
            "max_steps_per_day": 18000,
            "max_drive_min_per_day": None,
            "rest_interval_min": 120,
        },
        "fixed_costs_per_person": {"intercity": 0, "lodging": 0, "vehicle": 0, "other": 0},
        "days": [
            {"day": day, "date": None, "regions": [], "estimated_steps": 0, "estimated_drive_min": 0, "events": []}
            for day in range(1, args.days + 1)
        ],
    }
    write_json(targets[0], trip_input)
    write_json(targets[1], [])
    write_json(targets[2], plan)
    print(json.dumps({"created": [str(path) for path in targets]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
  
