Ran this through a structured adversarial search (generate → independent critique → revise → independent quality gate) rather than free-associating. Two rounds were needed — the first draft leaned on some ideas that were really just industry-standard practice relabeled, and skipped crew-structure and service-model territory the critique caught. Here's what survived.

## Strongest surviving thesis

Route optimization software solves *sequencing* — given today's list of stops, find the shortest path through them. It cannot fix *which* stops are on that list or *why* they're scattered. If your 900 accounts got added to the book in whatever order people called, with visit dates set at signup rather than by geography, the list itself is scattered by construction — no amount of resequencing fixes that. This is a hypothesis, not a finding yet — see the experiment below — but it's the most likely explanation for "helped some but the problem persists," because a routing tool optimizes a path, it doesn't restructure your scheduling policy.

The candidate fix — locking every address to a fixed zone + day of week, independent of signup date — is **not novel**; plenty of home-service trades (lawn care, pool service, some pest control operators) already run this way. So the real question for you isn't "should we invent this," it's "do we actually do this, or did we just assume the routing software made it unnecessary?" That diagnostic question is worth more than the idea itself.

## Most important reframing

You're treating this as a sequencing problem when it's a set-membership problem: which addresses are on the list, and how they're shaped. "Quarterly, scheduled by signup date, organized by town" was never designed — it accreted one sales call at a time. Town boundary as the planning unit is a political fact, not a topological one: two neighborhoods across a town line can be five minutes apart by road while two neighborhoods in the same town sit twenty minutes apart.

## Top opportunities

**1. Zone-locked recurring service days (rebuilt on drive-time geography, not town lines)**
- Mechanism: every address gets a permanent zone + weekday, drawn from actual road-network drive-time clusters and re-cut every 1–2 quarters as the book changes. New signups get sold into the nearest open zone-day (geo-gated), not "next available slot." Existing customers migrate *opt-in* — offer a modest discount (5–10%) for accepting their zone's standing day — rather than forcibly re-dating 900 people, which is a known churn trigger.
- Why it might not be new to you: check whether your CRM/scheduling policy already does this before assuming it doesn't — routing software and scheduling policy are different systems, and it's common to buy one and assume it covers the other.
- Falsifier (quantified): pull 60–90 days of existing GPS/appointment data (already sitting in the routing software) and simulate the same 900 stops re-grouped by pure geographic proximity, ignoring actual visit dates. If simulated windshield time drops ≥10 percentage points vs. actual, this is real and worth the migration cost. If it drops <5 points, your towns are too sparse for scheduling structure to be the lever — the problem is density, not dates, and effort should shift to opportunity 2.

**2. Isolate or prune the geographically indefensible accounts (portfolio + crew structure)**
- Mechanism: compute a fully-loaded cost per account (revenue minus labor minus allocated drive-time cost). Two variants depending on what the math shows: (a) if the bottom decile is net-negative once drive time is loaded in, drop them or sell them as a small standalone book to a rural-focused operator; (b) if they're still margin-positive but routing-incompatible, isolate them onto one dedicated low-cost role — a part-time or contract "infill" tech, paid per-stop rather than salaried, who exclusively absorbs the scattered stops that would otherwise cost every regular route its density. This is a genuine crew-structure change, not just an ops filter: it puts the windshield-time cost on a role designed to carry it, instead of spreading it across every tech's day.
- Why disproportionate value: outlier accounts typically cost far more in windshield time per dollar of revenue than average — a small number can carry a disproportionate share of total drive time (unverified for your specific book, but a common pattern in geographically dispersed service portfolios).
- Falsifier (quantified): run the fully-loaded cost calc on the bottom 10% of accounts by drive-time cost. If their average margin after loading drive cost is negative, act (drop/spin off). If it's still ≥15% margin-positive even loaded, don't touch the portfolio — hire/contract the infill role instead and re-check in two quarters.

**3. Trap/sensor-monitoring substitution for applicable pest categories (service model)**
- Mechanism: for rodent and other trap-based pest categories (not general quarterly perimeter/chemical treatment), install simple sensor-monitored stations so those accounts get a truck roll only when triggered, not every quarter regardless. This reduces total visit count for the subset it applies to — a different lever than reducing drive time per visit.
- Scope caveat: this doesn't touch the majority of a "quarterly service" book if most of your 900 accounts are general perimeter treatment rather than trap-based categories — size the addressable segment before investing.
- Falsifier: tag what fraction of your 900 accounts are trap/rodent-primary vs. general perimeter. If it's under ~15% of the book, the total windshield-time impact is too small to prioritize this quarter; if it's larger, pilot on 20–30 accounts and measure visits-avoided per quarter.

## Most contrarian hypothesis worth testing

Windshield time may be a **sales-acceptance** problem more than an ops problem: accepting every inbound signup regardless of location re-scatters the book faster than any zone-recut or route pass can compensate for. The higher-leverage move may be teaching sales to decline or upcharge heavily on prospects outside currently-dense zones — geography as a sales gate, not an ops afterthought.
Falsifier: track new signups for one quarter by distance from the nearest existing stop. If ≥30% of new signups land outside a tight radius (say, 1 mile) of an existing account, your acquisition process is actively working against every other fix on this list, and gating sales by zone will outperform any scheduling change.

## Cheapest high-information experiment

```
Hypothesis: Windshield time is dominated by date-driven scatter (visit dates set by signup order, not geography), not by genuine 3-town sparsity that no rearrangement could fix.
Critical assumption tested: Re-clustering the existing 900 stops into date-agnostic geographic groups would materially cut drive time.
Experiment: Pull 60–90 days of GPS/appointment data already captured by the routing software. Offline, re-simulate the same 900 stops grouped by pure geographic proximity (ignore actual visit dates) and compute total drive time vs. actual historical drive time.
Resources: A few hours of analyst time. No new tools, spend, or data collection — it's already in the software you're paying for.
Measured outcome: Percentage-point reduction in windshield time, simulated vs. actual.
Success threshold: ≥10 points — commit to the zone-migration plan (opportunity 1).
Failure threshold: <5 points — towns are structurally too sparse for scheduling to be the lever; shift priority to account pruning/isolation (opportunity 2) and sales-side zone gating.
Learned either way: which of the three opportunities is actually worth pursuing first, before spending on any of them.
If validated: begin zone/isochrone redesign and opt-in migration discount.
If falsified: prioritize opportunity 2 and the sales-gating hypothesis; treat current windshield time as closer to a market-density floor.
```

## Compact kill list

- Mileage/distance surcharge for sparse accounts — already standard industry pricing, not a structural change.
- Acquiring a competitor's account book — the pest-control industry's default consolidation playbook; not a non-obvious insight for you specifically.
- Congestion-aware time-of-day zone scheduling — a routing-parameter tweak; exactly the "better software" territory you said hasn't been enough.
- Franchise/owner-operator conversion for outlying zones — this is literally how large pest-control franchise brands are already structured.
- Two-tech "leapfrog" pairing (utility-crew model) — breaks down at typical 10–20 minute pest stops; doubles labor cost per route-day for a marginal drive-time save.

## What may still be missing

- No GPS/appointment data has actually been analyzed — everything above about date-scatter vs. true sparsity is a testable hypothesis until you run the experiment.
- Whether the existing routing software is being used to its full capability (dispatcher overrides, stale data, techs deviating from suggested routes) was never checked — some of the 40% could be an adoption gap rather than a structural ceiling. Worth a quick internal audit alongside the GPS experiment.
- Regulatory specifics for your actual state(s)/towns are unknown and would gate some adjacent ideas not included above: pesticide label/applicator-licensing rules, and any secured-storage/transport requirements if you ever considered take-home vehicles for a zone-resident tech model.
- Real account-level churn/attrition rate is unknown — it determines whether any density-building move can plausibly outpace natural scatter over time.
- Competitor geographic footprint is unknown — relevant if you ever explore referral reciprocity with a nearby operator, which wasn't developed above due to space but is a low-cost, low-trust variant worth a single phone call to test.