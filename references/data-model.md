# Reusable trip data

Persist three files so a later budget, date, destination, or preference change can be recomputed instead of researched from scratch.

## `trip-input.json`

```json
{
  "destination": "",
  "dates": {"start": null, "end": null, "season": null},
  "days": 0,
  "nights": 0,
  "people": 1,
  "origin": "",
  "budget": {"amount": 0, "basis": "per_person", "intercity_included": null},
  "pace": "normal",
  "daily_window": {"start": "09:00", "end": "22:00"},
  "transport": [],
  "interests": [],
  "must_go": [],
  "must_eat": [],
  "constraints": [],
  "dislikes": [],
  "assumptions": []
}
```

## `poi-ledger.json`

`budget.intercity_included` is `true`, `false`, or `null` (unresolved). The initializer defaults to `null`; pass `--intercity included` or `--intercity excluded` only when that scope is known. Keep scenario assumptions separate from confirmed user inputs. The audit script checks arithmetic, not whether the budget scope was agreed.

Each POI should contain:

```json
{
  "poi_id": "stable-local-id",
  "name": "",
  "aliases": [],
  "branch": null,
  "type": "attraction|museum|temple|restaurant|cafe|hotel|rest|other",
  "city": "",
  "district": "",
  "area": "",
  "address": "",
  "coordinates": {"lng": null, "lat": null},
  "must": false,
  "xiaohongshu": {"mentions": null, "pros": [], "cons": [], "ad_risk": null, "observed_at": null},
  "dianping": {"rating": null, "review_count": null, "per_person": null, "dishes": [], "recent_notes": [], "observed_at": null},
  "official": {"open": null, "close": null, "last_entry": null, "closed_days": [], "reservation": null, "ticket": null, "notices": [], "observed_at": null},
  "map": {"amap_poi_id": null, "entrance": null, "nearest_transit": null, "observed_at": null},
  "duration_min": null,
  "queue_buffer_min": null,
  "cost_per_person": null,
  "images": [],
  "sources": [],
  "score": null,
  "status": "verified|partially_verified|pending"
}
```

## `plan.json`

Keep per-leg evidence in the POI sources or a companion evidence ledger: exact endpoint POI IDs/entrances, mode, routing policy if available, requested departure time and timezone, retrieval time, observed distance/duration, source URL, status, and separate planning buffer. Preserve conflicting observations with the selected value and rationale. These are research fields for human review, not additional checks performed by `audit_plan.py`.

`scripts/audit_plan.py` accepts:

```json
{
  "trip": {
    "destination": "",
    "days": 1,
    "people": 1,
    "budget_per_person": 0,
    "pace": "normal",
    "earliest_start": "09:00",
    "latest_end": "22:00",
    "max_steps_per_day": 18000,
    "max_drive_min_per_day": null,
    "rest_interval_min": 120,
    "min_rest_min": 20
  },
  "fixed_costs_per_person": {"intercity": 0, "lodging": 0, "vehicle": 0, "other": 0},
  "days": [
    {
      "day": 1,
      "date": null,
      "regions": [],
      "estimated_steps": 0,
      "estimated_drive_min": 0,
      "events": [
        {
          "start": "09:00",
          "end": "10:00",
          "name": "",
          "kind": "attraction|meal|transit|rest|hotel",
          "meal": null,
          "region": "",
          "cost_per_person": 0,
          "must": false,
          "verified": false,
          "open": null,
          "close": null,
          "latest_entry": null,
          "drive_min": 0
        }
      ]
    }
  ]
}
```

Count trip-wide costs only in `fixed_costs_per_person`; count meals, tickets, local transit, fuel, tolls, and day-specific costs in events. Event times use local `HH:MM`. Include each transit and rest leg so the audit sees the true day.

## Audit input and rest rules

`trip.days` and `trip.people` must be positive integers. `days` and each day's `events` must be non-empty lists. Day numbers must be unique and within the declared trip length. The initializer produces an unfinished draft: add actual events before auditing it.

Times must be exactly `HH:MM`, from `00:00` to `23:59`; for example, `10:99`, `24:00`, and `9:00` are invalid. Split overnight events across days. Costs and driving durations must be finite non-negative numbers, and `drive_min` cannot exceed its transit event's duration.

Continuous driving resets only for a `rest` or `meal` event with at least `trip.min_rest_min` non-overlapping minutes (default 20). Short stops, sightseeing, hotel events, and unrecorded gaps do not automatically count as recovery. Add an explicit rest event when a longer stop includes a real break. The 20-minute default is a configurable planning heuristic, not a legal or medical guarantee.

CLI exit codes: `0` for no warnings, `1` for warnings with `--strict`, `2` for invalid input. Warnings without `--strict` are still reported with exit code `0`.
  
