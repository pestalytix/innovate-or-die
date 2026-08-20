## Reframing the problem, before the ideas

The conventional read is "new customers churn because onboarding doesn't get them to habit fast enough — improve the call, the docs, the nudges." That's the neighborhood to leave. The 45-minute call + doc portal is already the industry-standard SaaS onboarding motion; if it were just an execution problem, incremental fixes there would likely have already dented the number.

**Strongest surviving thesis:** the framing itself may be wrong in three specific ways, and the fix isn't a better onboarding flow but (a) finding out which of the three is actually happening, cheaply, before building anything, and (b) architecturally deleting the assumptions that make the current model fragile — that a human call must gate setup, that the person who signed up must be the one who keeps the login working, and that the vendor carries zero risk in the first 90 days while the customer carries all of it.

**Most important reframing:** "90 days" is being treated as a fixed habit-formation clock, but it's superimposed on subcontractors' own lumpier project/bid cycles and thin, turnover-prone office staff. Real constraint vs. inherited: it's *inherited* that onboarding must be synchronous human labor; it's a genuine open question — not yet a real constraint — whether "concentrated in the first 90 days" means rejection, dormancy (no job occasion yet), or account-continuity failure (the person who signed up left and nobody else has the login). Those three have completely different fixes, and nothing in the current setup distinguishes them.

## Top opportunities

**1. Delete the call — AI-driven autonomous setup, human only on exceptions.** Instead of a scheduled 45-minute call, parse the customer's existing data (QuickBooks/accounting export, spreadsheets, even photos of a paper job list) at signup and pre-populate real jobs, crew, and pricing before first login — no calendar dependency. *Mechanism:* the call is a coordination problem (translate existing data into product state) wearing labor's clothes; at near-zero marginal cost, every signup gets what today only the CSM's calendar allows a fraction to get quickly. *Why non-obvious:* the industry treats "the call" as the onboarding, not as one expensive way of solving a data-migration problem. *Why disproportionate value:* removes the queue (accounts sitting idle waiting for a CSM slot) that is very likely the actual bottleneck, not call quality. *Biggest failure risk:* many one-truck subcontractors run on paper/memory, not digitized records — this only works for the segment with something machine-readable to import, and handing financial data to an automated importer requires trust that field-based, non-technical owners may not extend.

**2. Risk-shifted commercial terms.** Don't bill full price from day one regardless of usage; gate billing (or offer a credit/refund) on a real usage milestone (e.g., three real invoices or bids sent) within the first 30 days. *Mechanism:* currently the vendor bears 100% of CAC loss on cancellation and the customer bears 0% of the risk of paying for something they never used — inverting who holds that risk removes "I paid for nothing" as the single most obvious cancel-trigger. *Why non-obvious:* SaaS pricing orthodoxy says bill on a calendar, not an outcome; construction subcontractors are unusually cash-flow-sensitive, which is exactly the population where "paid for nothing this month" is most likely to trigger a cancel. *Why disproportionate value:* changes the *default* at the exact decision moment (a cash-tight month) rather than trying to out-educate it. *Biggest failure risk:* revenue recognition gets messier, and it invites gaming (customers doing the bare minimum to avoid the bill, then still churning at day 45).

**3. Offline-first field-reliability architecture.** This is the one true system-architecture candidate, and it wasn't in the original onboarding-flow frame at all: if the product is slow, flaky, or unusable on a jobsite with poor signal, every field interaction reads as "this doesn't work" regardless of how good the onboarding was. *Mechanism:* local-first data capture with background sync turns "no signal on-site" from a failure event into a non-event. *Why non-obvious:* the entire churn conversation defaults to onboarding/engagement framing; connectivity is an infrastructure problem hiding inside what gets reported as "didn't adopt it." *Why disproportionate value:* if true, it explains churn that no amount of CSM cadence or docs could ever fix, because the failure is happening in the field, invisibly, after the call already went well. *Biggest failure risk:* this is a real engineering project, not a quick test, and it's currently unconfirmed as the actual driver — it needs to earn its investment with evidence first (see experiment below).

## Most contrarian hypothesis

**The mandatory onboarding call is net-negative for a meaningful share of this customer base, not protective.** For a time-poor, field-based, call-averse owner-operator, a scheduled 45-minute synchronous obligation between signup and first real use may itself be the largest single piece of friction in the funnel — worse than no onboarding at all. This directly inverts the premise that more human touch = more retention. It should be tested, not assumed either way.

## Cheapest high-information experiment

This one is cheaper than any product change and should gate the others — it turns three of the ideas above from speculation into evidence:

```
Hypothesis: A material share of "first-90-day churn" is not product rejection — it splits into (a) dormancy (no project occasion yet), (b) account-continuity failure (signer left / login lost), and (c) field-reliability failure (product didn't work on-site), each requiring a different fix than "better onboarding."
Critical assumption tested: churn reason and destination (competitor vs. reversion to paper/Excel vs. still-dormant-but-alive) are knowable from data you already have.
Experiment: pull the last 12 months of cancelled logos. For each: exit-survey/support-ticket text (if any), usage pattern in the 14 days pre-cancel, whether a different person logged in after the original signer's last session, connectivity-error/crash logs in the final week, and whether the account reactivated organically within 12 months.
Resources: 1 analyst, 2–3 days, no new tooling — existing support/product/billing data only.
Measured outcome: % of churned logos in each of the four buckets (rejection / dormancy / continuity-failure / reliability-failure).
Success threshold: any single non-rejection bucket ≥20% of churned logos — strong enough to justify building the matching fix (e.g., role-based account architecture, offline-first work, or a dormancy/pause state).
Failure threshold: >70% cleanly bucket as straightforward rejection with no secondary pattern — in which case the onboarding-flow-improvement instinct was closer to correct than this analysis assumes, and effort should go back to onboarding quality, not architecture.
Learned either way: which of the ideas above deserve real investment vs. which were solving a problem that doesn't actually exist at scale.
If validated: fund the matching architecture/business-model fix for the largest confirmed bucket first.
If falsified: run the "kill the call" A/B test (self-serve/AI-import path vs. mandatory call, both cohorts otherwise identical) as the next-cheapest test of the onboarding-flow hypothesis itself.
```

## Compact kill list

- **Route sales through GCs/bonding agents as the paying customer** — already the standard construction-SaaS B2B2B distribution model (Procore/Textura-style); not novel, just unnamed by the team.
- **"Pause" instead of hard cancel** — universal subscription-retention pattern already in wide use across SaaS; no construction-specific mechanism.
- **Marketplace/invoice-factoring loss-leader model** — real precedent (Toast, ServiceTitan) but requires underwriting-grade data and scale this company almost certainly doesn't have yet; no falsifier fits inside a 90-day-churn brief — it's a later-stage bet, not an early-churn fix.
- **Auto-parse the crew's group-text thread** — no clean consent/API path to personal SMS content; a legal and technical dead end as stated, not just "execution risk."
- **Free-forever core + metered power features (freemium)** — one of the oldest SaaS business models in existence; doesn't survive an industry-swap test and isn't specific to this problem.

## What may still be missing

- **Real churn-reason and churn-destination data** — everything above is generative until the experiment runs; treat the top three opportunities as hypotheses ranked by mechanism strength, not settled priorities.
- **Whether the 6% figure is uniform** across acquisition channel, company size, and trade — if it concentrates in one lead-gen source, this may be a funnel/ICP-qualification problem wearing an onboarding costume, not addressed by any idea above.
- **The regulatory compliance surface** (lien waivers, COI/W-9 management, prevailing wage) beyond certified payroll was only lightly sampled — a compliance-lock-in play could be much larger or much smaller than estimated depending on what fraction of the customer base does regulated work.
- **Pricing/packaging fit** — whether the product is simply oversold to a segment (very small, near-zero-admin-bandwidth shops) that no onboarding design can retain, independent of everything else here.

Happy to go deeper on any one of these — especially designing the data pull, or sketching what the offline-first or role-based-account architecture would actually require to build.