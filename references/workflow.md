# Complete planning workflow

Use this for a new plan or a major rebuild. Keep research proportional: once every route slot has a verified primary and practical fallback, stop expanding the pool.

## 1. Normalize the brief

Record destination, exact dates or season, usable days and nights, people, origin, transport windows, budget inclusion, interests, pace, mobility limits, food rules, transport preferences, MUST items, and dislikes. Resolve named holidays to exact dates from a current authoritative source. If first-day arrival or last-day departure is unknown, state explicit working windows.

Create a trip folder with `scripts/init_trip.py` when the plan will be revised or turned into artifacts.

## 2. Build a focused discovery matrix

Combine the destination with: first visit, N days, local recommendation, season, holiday, culture, architecture, nature, citywalk, ordinary local food, breakfast, snacks, dinner, café, avoid, queue, overpriced, closure, rain, heat, cold, wind, and every MUST item. For large regions, search proposed corridors and transfer legs as well as individual places.

Favor user content from the last 90 days; use 90–180 days strongly, 180–365 days as support, and older content as background. For restaurants, cafés, hotels, malls, and nightlife, favor the last six months.

## 3. Build and deduplicate candidates

Capture names, aliases, types, branches, dates, reasons, drawbacks, price, queue, duration, transport clues, ad risk, author context, and image candidates. Increase confidence for concrete routes, prices, queues, tradeoffs, and substantive discussion. Decrease it for sponsorship, uniform copy, polished imagery without lived detail, or repeated campaign language.

Merge aliases only after resolving the POI. Keep different restaurant branches separate. For huge scenic areas, distinguish gates, visitor centers, cableways, parking lots, and trailheads.

## 4. Validate before selecting

Use Dianping for exact restaurant or consumer-venue branches. Record rating, review volume when visible, average spend, frequent dishes, recent positive and negative themes, hours, address, queue or booking, and status.

Use official sources for attractions, museums, temples, memorials, exhibitions, cruises, performances, zoos, theme parks, protected areas, and controlled roads. Verify opening, last entry, tickets, reservations, closure days, holiday notices, road permits, and temporary controls.

Search popular candidates again with avoid, queue, worth it, local resident, overpriced, photo mismatch, closure, and renovation terms. Mark each as strong recommendation, recommendation, convenient stop, not worth a detour, or skip.

## 5. Score the route-compatible pool

MUST items survive scoring. For other attractions use a 100-point model: interest match 20, real-user support 15, local distinctiveness 15, recent sentiment 10, irreplaceability 10, route convenience 10, time cost 5, value 5, experience or photo value 5, seasonal fit 5. Deduct for marketing, repeated warnings, remote travel, queues, and duplicated experiences.

For restaurants compare taste 30%, recent sentiment 15%, local character 15%, value 15%, route fit 15%, and queue cost 10%. A distant viral restaurant should rarely displace a strong nearby choice.

## 6. Build the route

Resolve exact Amap POIs, useful entrances, coordinates, distances, and observed travel times. In a city, build one main area and at most two adjacent areas per day. In a province-scale trip, choose an open-jaw sequence, overnight bases, and transfer days before adding attractions.

Schedule fixed or scarce reservations first, then MUST items, transport, rest, meals, and flexible candidates. Do not fill every minute. Use `references/routing-and-scheduling.md` for long-distance rules and route switching.

## 7. Embed food and lodging

Choose meals after each day's route and next stop are known. Breakfast belongs near the hotel or first stop; lunch near the core attraction or transfer rest point; dinner near the final stop, night district, or hotel. Give one exact primary branch and one nearby backup; add a fast option for likely holiday queues.

Choose lodging after the route is stable. Compare at least three areas by total commute, transit or road access, parking, price, food, evening convenience, station or airport access, safety, and environment. Prefer consecutive nights when they reduce packing without creating wasteful driving.

## 8. Calculate and optimize the budget

Use `references/budget-and-audit.md`. Include all categories in scope, daily totals, total per person, party total, and buffer. Recompute after every material route change.

## 9. Apply date and risk switches

For dates within forecast range, check the forecast; otherwise document seasonal conditions and schedule a refresh. Add holiday buffers for traffic, lodging, queues, reservations, and restaurant waits. Build a concrete alternative when rain, heat, wind, snow, seasonal road closure, or full bookings invalidate the main route.

## 10. Audit, repair, and deliver

Run `scripts/audit_plan.py`. Then manually inspect route shape, map freshness, daily energy, late arrivals, unsafe roads, repeated experiences, image provenance, and unresolved facts. Repair the plan rather than merely listing defects.

Produce only the artifacts the user requested. The clean guide may omit inline citations, but retain the evidence ledger for refreshes.
  
