# Evidence source rules

## Xiaohongshu discovery record

Capture post date, place, exact branch or area, recommendation, concrete experience, negative feedback, price clues, queue, visit duration, transport clues, author context, ad suspicion, image candidate, and source URL. Treat likes and frequency as discovery signals, not proof of quality. Never summarize a post that was not actually accessed.

## Dianping consumer record

Capture exact branch, address, business district, rating, visible review volume, average spend, recommended or frequently mentioned dishes, recent positive and negative themes, hours, queue, booking, group deal, status, observed date, and source URL. Do not transfer one branch's rating, price, or menu to another branch.

## Amap spatial record

Capture POI name and ID when visible, address, district, coordinates, useful entrance, nearest transit, route mode, distance, observed duration, estimated fare or toll, and lookup date. For scenic areas, route to the correct gate or visitor center. Map times are observations; refresh them for current traffic or seasonal roads.

## Official rule record

Capture the issuing organization, official page or account, publication date, opening and closure, last entry, ticket, reservation, holiday arrangement, road rule, special event, and temporary notice. Prefer the attraction, local government, transport operator, railway, airline, or park authority itself.

## Confidence and conflict handling

Label each fact as `confirmed`, `estimated`, or `pending`. When sources conflict:

1. Use the official source for rules and access.
2. Use current Amap data for spatial routing.
3. Use current Dianping data for consumer decisions.
4. Use recent Xiaohongshu posts for lived experience and emerging issues.

Record both values and the reason for choosing one. If the conflict remains material, use `【待确认】` and give a safe fallback.

## Access failure

When login, CAPTCHA, or user takeover is required, continue other sources and preserve a short pending list for the blocked platform. Use official and public search fallbacks. A single inaccessible site must not stop the trip.

## Research stopping rule

Stop broad discovery when every itinerary slot has:

- one route-compatible primary;
- one practical nearby fallback when failure would disrupt the day;
- verified access rules for MUST and time-sensitive items;
- enough evidence to estimate time and cost.

Continue only for unresolved choices that could change route, safety, or budget.
  
