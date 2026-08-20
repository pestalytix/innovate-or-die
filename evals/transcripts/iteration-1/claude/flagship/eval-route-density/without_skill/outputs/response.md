Route optimization solves sequencing. Your problem is almost certainly **composition** — which accounts land on a given day's list in the first place. An optimizer can only order the stops you hand it; if today's list spans three towns, there's no good order.

## The arithmetic first

900 accounts × 4 visits = 3,600 stops/year. Over ~250 working days that's **~14.4 stops/day for the entire company**. So:

- If you're running 2 techs, that's ~7 stops each — brutally low density, and 40% drive time is the inevitable result.
- If it's 1 tech plus overflow, you're closer to right-sized and the fix is different.

Worth confirming which, because "we have more truck capacity than route density" is a totally different problem than "our days are geographically scattered."

## What usually causes the scatter

**Service dates are anchored to sale dates, not geography.** Every account's next-service date drifts from whenever it was sold. Three years in, your Tuesday list is a random sample of all three towns. The fix is *route days*: assign every account to a fixed day-of-week and week-of-quarter based on where it sits, then migrate accounts onto that grid over 2–3 cycles ("we're moving your service to the second Tuesday"). Most customers don't care. This is the single biggest lever and it's a data/scheduling change, not a software purchase.

**Customer-chosen time windows.** If people pick appointment times, routing is dead on arrival. Quarterly residential should be exterior-by-default — no one home required, no windows, no lockouts. If you're still doing interior-on-request-only, say so on the schedule and treat interiors as the exception.

**Lockouts and reschedules.** A re-visit to one house is the worst mile you drive all quarter. If your lockout rate is above ~5%, that alone can be several points of windshield time.

**Sales sold outside the envelope.** New accounts get written wherever the lead came from. If reps aren't capped to defined territory polygons — or the outlier accounts aren't priced for the drive — density erodes a little every month.

**Shop time.** Techs driving to the yard, loading, then driving to stop one. Take-home trucks and night-before loading recovers 45–60 min/day and never shows up in routing software.

## What to measure

Stop counting miles. Track:
- **Drive minutes per stop** (good residential runs 6–10; you're likely 15+)
- **Stops per tech per day**, by day-of-week — this exposes the bad days
- **Revenue per route hour** including drive time, by account — this exposes the accounts to reprice or release
- **Density**: for each account, how many other accounts sit within 2 miles

## The uncomfortable one

At 900 accounts across three towns, you may be spread over more geography than the book supports. Two real options: densify (concentrate sales in the tightest town until it's saturated) or reprice the outliers to cover their true cost. Cutting drive time by better routing has a floor; changing the shape of the book doesn't.

---

If you've got service history in BigQuery, I can pull the actual numbers — stops/day by tech, drive time by day-of-week, and a density score per account — and tell you which of the above is actually biting you rather than guessing. Want me to look? And how many techs are you running?