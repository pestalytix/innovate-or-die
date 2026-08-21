# Positive cases — the skill should activate

Five prompts, taken unchanged from [evals/evals.json](../../evals/evals.json),
which is where this project's test problems live. They are reused rather than
written fresh so that the cases shown to a reviewer are the same cases the skill
is measured on; a demo set written for a submission tends to be a set the skill
happens to be good at.

**Fixtures: none.** Every case is a plain text prompt. The skill reads no files
of the user's, calls nothing over the network, and needs no credentials, so there
is nothing to attach and nothing to set up.

**Expected result shape**, common to all five — this is the protocol's delivery
contract, not a per-case expectation:

- opens with the activation marker `⟦innovate-or-die v2.1.0⟧`
- leads with the strongest thesis, not with a summary of the question
- restates the problem and names what the conventional answer would be
- gives opportunities with the **mechanism** attached to each, not a list of tactics
- states the most contrarian hypothesis on the table
- gives one cheap experiment with a **pass/fail number set before the test runs**
- gives a short kill list: what was rejected, and why
- closes with what may still be missing
- flags any figure, price, or regulation it was not given rather than inventing one

A run missing the kill list and the falsifiable experiment did not run the
protocol, whatever else it produced. That is the check to make first.

---

## 1 — Route density (field services, casual phrasing)

> we run residential pest control in three towns, about 900 accounts, quarterly
> service. windshield time is eating us alive - techs spend maybe 40% of the day
> driving. we've already tried route optimization software and it helped a bit.
> what are we missing here?

**Expected behaviour.** Treat "we already tried routing software" as the signal it
is: the binding constraint is probably not routing quality. Attack the inherited
assumptions — the quarterly cadence, the three-town footprint, the definition of
a serviced account — rather than optimising within them.

**Expected result.** Hypotheses about the real binding constraint (route density,
or the quarterly-cadence assumption) each with a causal mechanism, plus an
experiment the operator could run this week.

## 2 — Dental no-shows (healthcare operations, precise phrasing) — control case

> A six-operatory dental practice loses roughly 14% of its hygiene appointments
> to no-shows, despite automated SMS reminders sent 48 hours ahead. The practice
> owner wants to know how to fix this.

**Expected behaviour.** This is the case where the conventional answer is right.
Reminder sequences, deposits and late-cancel fees, strategic overbooking and
waitlist backfill are genuinely near-optimal here. The correct run **says so and
labels its own winner conventional.** A run that invents an exotic mechanism to
look innovative fails this case — which is why it is in the set.

**Expected result.** An honest finding that the well-established interventions are
the best available, with the reasoning for that judgment, and the experiment
still specified with a pass/fail number.

## 3 — Municipal water loss (public infrastructure, precise phrasing)

> A municipal water utility serving 60,000 connections loses an estimated 22% of
> treated water to non-revenue water. Capital budget for the next three years is
> committed. Identify approaches to reducing non-revenue water that do not
> require new capital expenditure, and state what evidence would confirm or
> refute each.

**Expected behaviour.** Respect the stated capital constraint — proposing capex is
failing the question, not thinking bigger — while testing which of the *other*
constraints are real rather than inherited.

**Expected result.** Options that hold the capital constraint, distinguish
apparent losses from real ones, and carry falsifiers with numbers attached.

## 4 — Bookstore events (small retail, casual phrasing)

> i own an independent bookstore, we do author events but they barely break even
> and take a ton of staff time. thinking about dropping them entirely. what would
> you do?

**Expected behaviour.** Refuse the binary the question offers. Ask what the events
actually produce — customer acquisition, community standing, publisher
relationships, data — before deciding whether "barely break even" is the relevant
measure.

**Expected result.** A reframing of what the events produce, at least one
deletion-style option, and a cheap test of the real value.

## 5 — SaaS onboarding churn (software, precise phrasing)

> A B2B SaaS product for construction subcontractors has 6% monthly logo churn
> concentrated in the first 90 days. Onboarding is a 45-minute guided call plus a
> documentation portal. Propose approaches to reducing early churn, including any
> that change the business model or system architecture rather than the
> onboarding flow.

**Expected behaviour.** Take the invitation in the last clause seriously. An
answer entirely about improving onboarding has stayed inside the frame the
question explicitly opened.

**Expected result.** At least one option that changes incentives, pricing, or
architecture rather than the onboarding flow, with the mechanism named, the
hidden thesis stated, and a falsifiable next test.
