---
name: china-trip-planner
description: Research, verify, route, budget, revise, refresh, and present complete trips in China using Xiaohongshu discovery, Dianping reviews, official rules, and Amap routing. Use for destination itineraries, regional road trips, route or budget changes, weather updates, and travel-guide PPT, DOCX, PDF, or spreadsheet requests; skip isolated facts such as one train time.
---

# China Trip Planner

Produce a trip the traveler can follow without making the core choices again. Support new plans, revisions, volatile-data refreshes, and presentation delivery.

## Read the request once

Extract destination, dates or season, duration, travelers, origin, arrival and departure windows, budget scope, lodging target, interests, pace, walking or driving limits, food rules, transport preferences, MUST GO, MUST EAT, and dislikes.

Begin research when the destination and usable duration are known. Ask only when a missing value materially changes executability. Otherwise state a reasonable assumption and proceed. Useful defaults are normal pace, 09:00–22:00, two to four core experiences daily, medium walking, local food near the route, and public transit plus walking in cities.

Classify explicit requirements as `MUST`; classify discovered places as `CANDIDATE`. Never remove a MUST solely because its score is low. If the requested duration or budget cannot fit every MUST safely, produce the best executable version and state the comfortable duration or budget beside it.

## Choose the operating mode

- **New plan:** execute [references/workflow.md](references/workflow.md).
- **Revise:** reuse the evidence and POI ledger, then recompute affected routes, meals, lodging, risks, and every affected budget category.
- **Refresh:** recheck weather, closures, reservations, opening hours, restaurant status, lodging prices, and transport disruptions.
- **Presentation:** finalize and audit the plan first, then use [references/deliverables.md](references/deliverables.md).

For a large province or multi-city trip, treat the route as an open-jaw or one-way network. Minimize long backtracking while allowing short local returns that improve safety, lodging, or transport reliability. Read [references/routing-and-scheduling.md](references/routing-and-scheduling.md).

## Use evidence by role

- Xiaohongshu: discover places, real experiences, recent trends, photo angles, queue patterns, pitfalls, and route ideas.
- Dianping: verify exact restaurant or venue branches, ratings, average spend, dishes, recent reviews, queues, and operating status.
- Amap: resolve exact POIs and entrances, coordinates, transit, driving, realistic travel time, geographic clusters, and daily route order.
- Official sources: verify opening, last entry, tickets, reservations, closures, holiday rules, performances, road controls, and temporary notices.

Prefer the user's already-open platform tabs when identified. If a platform requires login, CAPTCHA, or user takeover, pause that source only and continue useful work elsewhere. Use public search and official pages as fallback. Never invent posts, ratings, prices, travel times, opening hours, tickets, or reservation rules. Mark unresolved facts `【待确认】`.

Keep a source ledger with URL, retrieval date, observed value, and volatility even when the user wants the final guide without citations. Read [references/evidence-sources.md](references/evidence-sources.md) for extraction and stopping rules.

## Plan in the right order

1. Resolve dates, trip windows, budget inclusion, pace, MUST items, and safety constraints.
2. Discover a focused candidate pool; deduplicate aliases and keep restaurant branches separate.
3. Validate route-critical candidates with the appropriate source.
4. Build a unified POI ledger using [references/data-model.md](references/data-model.md).
5. Cluster by geography and choose daily areas or regional overnight bases.
6. Schedule fixed reservations and MUST items, then travel legs, rest, meals, and flexible stops.
7. Embed nearby restaurants only after the route is stable; choose lodging after daily regions are stable.
8. Calculate the complete budget and optimize if needed.
9. Apply season, weather, holiday, road, and closure switches.
10. Audit and directly repair the plan before delivery.

For long drives, include arrival recovery, fuel or charging opportunities, toilets, food, and a real rest every 90–120 minutes where feasible. Avoid unsafe night driving and do not hide days dominated by transfers.

If the budget is insufficient, do not pretend the full route fits. Give a comfortable recommendation and an executable compressed option with explicit tradeoffs. Preserve core experiences by first reducing unnecessary taxis or car days, adjusting lodging, removing low-value paid stops, choosing practical restaurants, and tightening the route.

## Persist reusable trip state

When a writable workspace exists, create a destination folder containing `trip-input.json`, `poi-ledger.json`, and `plan.json`. Use:

```bash
python3 scripts/init_trip.py <folder> --destination "目的地" --days N --people N --budget-per-person N
```

On later changes, update the input and recompute the existing plan. Start a new folder for a new destination. In a new conversation, use these files or a supplied prior guide; do not assume hidden cross-session memory.

Run the final machine-checkable pass:

```bash
python3 scripts/audit_plan.py <folder>/plan.json
```

The script catches structural, timing, MUST verification, meal, rest, region, walking or driving, and budget issues. Human review must still assess route shape and current map accuracy.

## Call adjacent skills only when needed

Read [references/skill-integration.md](references/skill-integration.md) before creating artifacts. Use Presentations for PPTX, ImageGen for clearly labeled illustrative art, Spreadsheets for dense POI or budget workbooks, Documents for DOCX, and PDF for a final PDF. The travel plan and evidence ledger remain the source of truth.

Lead the final response with the itinerary, route logic, costs, reservations, risks, and fallbacks. Do not narrate the research chronology unless the user asks.
  
