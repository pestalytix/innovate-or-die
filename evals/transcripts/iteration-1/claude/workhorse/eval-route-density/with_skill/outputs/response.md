Gate caught a real gap — three of four finalists lacked falsifiable experiments. Adding those now, then delivering.

## What the routing software couldn't touch

**Strongest thesis:** Route software solves "shortest path through a fixed list of stops." That was never your binding constraint. What's binding is *which* stops exist and where (density you don't manage), *how often* each gets visited (uniform quarterly, regardless of actual pest pressure), and *who has skin in the game* on drive time (currently: nobody — not sales, not the tech, not the customer). A pathing algorithm can't fix a density problem, a cadence problem, or an incentive problem. That's why it helped "a bit" and stalled.

**Most important reframing:** You're treating this as a routing problem because that's the tool category you already own. A "visit" is currently a fixed-duration, identical, calendar-triggered event for every account regardless of need — that's contractual convention, not biology (a licensed applicator must still do the treating, but not every quarter needs a full treatment). The single highest-leverage unknown: **do customers value the reassurance of a scheduled visit itself, independent of outcome?** If yes, most of what follows shrinks. If no, it opens up substantially. You don't know the answer yet, and it's cheap to find out — see the experiments below.

## Top opportunities

**1. Risk-tiered, condition-triggered cadence.** Score accounts by risk (construction, tree cover, callback history). Low-risk accounts move to 2 full visits + 2 remote photo-report touches/year, escalating to a truck roll only if flagged; high-risk accounts keep or increase cadence. If even the bottom half of accounts drop from 4 to ~2.5 visits/year, that's ~19% fewer truck rolls without touching a route. Biggest risk: customers read fewer visits as less service regardless of outcome — testable before buying anything.

*Experiment:* Move ~75 low-risk accounts to 2 visits + 2 photo check-ins for a year, framed as "smarter monitoring." Track churn/complaints/reversion-requests against a matched 75-account control. **Succeeds** if churn/complaints stay within 1.5x of control and truck rolls drop ≥30%. **Fails** if churn/complaints exceed 2x control or >15% ask to revert. Cost: a CSR's time to set it up, no new tools.

**2. Stop selling into sparse geography, start batching what you have.** Every account sold outside your existing clusters permanently degrades every tech's route — and sales is paid for volume, not density, so acquisition works against the fix indefinitely. Gate new-account commission by proximity to existing clusters; pair with wider due-date windows (±3-4 weeks instead of a fixed day) so batching is actually possible. This is the one lever that *compounds* — it's the only fix that prevents the problem from re-accumulating after everything else works.

*Experiment:* 90-day trial — bonus commission for closes near existing density, wider promised-date windows on new contracts. **Succeeds** if median new-account distance-to-nearest-existing-account drops ≥25% with <10% drop in total closes. **Fails** if closes drop >20% or distance doesn't move. Cost: a commission-plan tweak and a spreadsheet tag.

**3. Give the tech a stake in their own route.** Right now the software optimizes; the person driving has zero financial reason to. Assign a tech (or pair) a standing zone, pay a quarterly bonus as a share of zone margin improvement (drive-time share tracked as a cost input), stay W-2 to avoid misclassification exposure. This converts drive time from a fixed cost into something a motivated employee works to shrink continuously, at zero software spend.

*Experiment:* Pilot with 1 zone, 2 quarters, 15% bonus on margin improvement vs. trailing baseline. **Succeeds** if that zone's drive-time share drops ≥5 points with no attrition/complaint spike. **Fails** if no measurable change after 2 quarters. Cost: a few hours/quarter of payroll math.

## Most contrarian hypothesis

The radical extension of #1: stop selling a fixed visit count at all. Sell an annual "stays pest-free" outcome and let cadence float per account (could be more *or* fewer than 4 visits) based on risk score and monitoring signal. This removes the contractual constraint that forces every other idea to work around a fixed number instead of through it. It's contrarian because every national chain still keeps a nominal visit schedule even while selling outcome guarantees — weak evidence this either doesn't work commercially or just hasn't been tried; you don't know which.

*Experiment:* Offer ~25 *new* prospects (not existing accounts, to dodge contract-migration mess) a real choice at point of sale: "4 scheduled visits, $X" vs. "we monitor and treat as needed, guaranteed pest-free, $Y." **Succeeds** if ≥25% pick the no-fixed-count plan with complaint rate within 1.5x of standard. **Fails** if <10% pick it or complaints exceed 2x. Cost: a revised pricing sheet and some sales training time.

## Cheapest first move — do this before any of the above

You already have the data to know which lever matters most, and haven't looked at it. Pull one quarter of GPS breadcrumb data from the route software you already own and bucket every drive minute into: intra-cluster, inter-cluster (same town), inter-town, and depot-to-first-stop/last-stop-to-depot, by town.

- **If inter-town + depot legs dominate** → structural fix (geographic batching, forward-staged town depots) is your priority.
- **If intra/inter-cluster minutes dominate** → density and cadence (opportunities 1 and 2) are the higher-leverage fix, not batching.
- **If no bucket dominates (all within ~20-30% of each other)** → no single lever wins; run small parallel pilots instead of betting big on one.

Cost: a few hours of a dispatcher's time, $0. This also answers a question nobody's checked: whether the software's "helped a bit and stalled" result reflects a real structural ceiling, or just poor configuration/adoption — which would make everything above premature.

## Rejected, and why (instructive misses)

- **Real-time gap-filling / day-of dynamic discounting** — this is just re-solving the same fixed-stop-list problem the software already handles. Doesn't leave the category that already plateaued.
- **E-bikes for dense blocks** — ignores that techs carry chemical/gear payload; doesn't survive a basic feasibility check.
- **Drone/robot perimeter checks** — FAA overflight complexity and cost for marginal gain over the much cheaper photo-self-report mechanism in Opportunity 1.
- **Firing the least-profitable accounts** — standard "prune the bottom 20%" advice; real, but caps upside since edge accounts are a small slice of 900, and doesn't fix the sales engine still selling more of them.
- **Pooling route/traffic data with other local service companies** — marginal value beyond what your existing software's traffic feed likely already has; not worth the coordination overhead.

## What's still genuinely open

- **No regulatory check has been done.** Applicator-licensing law and worker-classification rules are load-bearing for Opportunity 3 and any self-treatment variant — this needs an actual conversation with your state pesticide regulator or counsel, not an assumption, before committing budget there.
- **Contract migration for your existing 900 isn't solved.** The experiments above deliberately sidestep this by testing on subsets/new customers — a real rollout of cadence or contract changes to the existing base needs its own communication plan to avoid a churn spike.
- **Customer segmentation wasn't explored.** Anxious/new customers likely tolerate schedule flexibility very differently than long-tenured ones — any rollout probably needs to be segmented, not uniform.