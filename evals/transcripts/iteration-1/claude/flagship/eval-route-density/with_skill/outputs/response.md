Gate returned REVISE (mechanism 3, testability 3). I've applied one correction pass — the routing-prize arithmetic was scaling with headcount when it shouldn't, and two of the recommendations shipped without falsifiers. Here's the corrected answer.

---

# What you're missing

*No web access this session, so nothing external was verified. Every figure I don't have is named rather than invented.*

## 1. The thesis

**Your optimizer is solving the easy half.** It decides the *order* of a day's stops. It does not decide **which accounts share a day** — and that's where nearly all the cost is set. That assignment is currently made by each customer's sign-up anniversary, which means each day's route is a near-random geographic sample drawn from your historical sales sequence. Sequencing a random sample well still leaves you with a random sample.

**Labeled conventional:** this isn't exotic. Due-date *windows* instead of fixed dates, with street-assigned service days, is standard practice at scaled residential operators and a first-class feature in mainstream pest field software. So the most likely answer to "what are we missing" is unglamorous: **you may be running software you already own in single-day sequencing mode when it supports a multi-week horizon with flexible windows.** Two questions to your vendor, ten minutes, before anything else.

**But size the prize first, because nobody has.** Let **H** = your total company field hours per year (all techs combined).

- Drive time = 0.4H.
- Routing changes that don't change the *account set* typically recover 20–30% of drive time — the geography doesn't move. [ESTIMATE, not a measured figure for your business.]
- So perfect routing recovers roughly **10% of your total field hours.**

Now the part that explains your own report. **A freed hour is not cash.** It converts only two ways: you cut payroll hours, or you fill it with revenue work. At 1–3 techs, 10% of field hours is nowhere near a headcount, and your book supplies no extra demand to absorb it. So what you actually banked was fuel and vehicle wear.

Worked illustration — plug in your own numbers: at two techs, H ≈ 4,000 hours, recoverable ≈ 400 hours ≈ 12,000 miles ≈ **$3,000–4,000/year** at marginal vehicle cost. Against that: a 5% price increase on 900 accounts yields 45 × (annual revenue per account), which at $450/account is **~$20,000/year at near-100% margin.** Break-even on churn is clean and worth writing down: **the increase pays as long as incremental cancellations stay under 5%.**

That's an order-of-magnitude framing, not a decision rule. But the ordering is robust: **a single-digit price move is probably worth several times everything routing can ever return, and it takes an afternoon.** That's the strong conventional option and it should be labeled as such.

## 2. The reframing

**Windshield time isn't waste. It's a fixed cost of having a truck in the field, and it's fixed per *day*, not per *stop*.** You don't cure a fixed cost by shrinking it. You amortize it.

- **Inherited constraint:** minimize drive-time percentage.
- **Real constraint:** maximize gross margin per truck-day.

Drive % is a ratio. You've been attacking the numerator, which is bounded by geography you can't move. The denominator — revenue per truck-day — has no ceiling. Across three towns your numerator may already be near its floor.

This is also why "it helped a bit." Routing produced hours; hours aren't money until something absorbs them.

## 3. Three opportunities

### 3.1 Free the due date — and redirect reschedule requests as a zero-risk migration channel

**Concept.** Convert accounts from "due 14 Aug" to "due in the Aug–Oct window." Assign the service day by street, not by customer. Apply to all new sales immediately.

**Insight.** The binding constraint is your billing system's anniversary anchor, not customer preference. Utilities solved this decades ago by slaving the billing cycle to the meter-reading book. You have it backwards — the route is slaved to the billing anniversary.

**Mechanism.** Optimizing a fixed 14-address set drawn at random is nearly trivial and nearly worthless. The same software over a ~300-address monthly pool, free to choose which fifteen share a Tuesday, is a different problem with real slack in it.

**Why non-obvious.** The clustering advice is obvious. The *migration path* isn't. Migrating 900 existing relationships to chase a few thousand dollars is a bad trade, so most operators try it, generate cancellations, and stop. The non-obvious move: **your inbound reschedule requests are a free, consent-based migration channel that you are currently spending to make density worse.** Every time a customer asks to move and you answer "sure, what day works?", you push them further off route. Replace it with: *"I can do Tuesday the 12th or Thursday the 21st"* — both already on that street. Same felt autonomy, opposite geometric effect. Add new sales, renewals, and price-increase touchpoints, and the book densifies over 12–24 months at zero churn risk.

**Disproportionate because** it compounds — every migrated account permanently improves the geometry for its neighbors.

**Biggest reason it fails, with a number.** If customers must be home, the date has real value to them and assigning it causes churn. **Threshold: if more than ~40% of your quarterly services require interior access or the customer present, don't assign the day — price it instead. Under ~20%, just take it.** This is one query against your work orders and it's the highest-value fact you don't have.

### 3.2 Attack the denominator: add-ons that create *extra visits to addresses you already visit*

**Concept.** Seasonal mosquito (monthly Apr–Sep), rodent, termite monitoring — sold specifically into accounts inside existing clusters, and scheduled onto that street's existing service day.

**Insight.** The marginal drive cost of an incremental visit to an address already on a serviced street is approximately zero. This is the only growth vector that *increases* total visits while *improving* your drive ratio — and it's the mechanism that converts 3.1's freed hours into actual cash.

**Why non-obvious.** It reads backwards. "More visits" is the intuitive opposite of "less driving," so it's never generated by anyone framing this as drive reduction.

**The discriminating test — this also resolves the tempting "one visit, two services" idea.** Cross-training a tech to deliver lawn care or gutter work on the same stop sounds like free revenue on a paid drive. It isn't: it *substitutes* stop time for drive time, and stop time is the productive part. Doubling on-site minutes halves your stops per day. So the real question for any add-on isn't revenue per stop, it's **revenue per on-site minute.** Low-ticket bolt-ons fail that test. High-ticket ones pass. (Separately, lawn/ornamental application is usually a different license category from structural pest control in most US states — verify before assuming cross-training is available to you.)

**Biggest reason it fails.** Attach headroom may already be gone — a quarterly customer has declined the upsell three times a year already. And it turns your tech into a salesperson, which is a different hire, a different comp plan, and a known driver of turnover. At 1–3 techs, losing one is a catastrophe. **Falsifier: if fewer than 3 of the next 20 doorstep offers convert, the headroom thesis is dead.**

### 3.3 Price by cost-to-serve — tested on one decile, not the book

**Concept.** Join revenue-per-account to drive-minutes-per-account (you have both — one in billing, one in your phones' GPS). Then apply a zoned trip component, sized to actual drive cost, to your worst decile only.

**Insight.** You sell one product at one price to 900 accounts whose cost to serve differs by roughly an order of magnitude. Your dense-street customers are silently subsidizing your outliers, and neither group knows it.

**Why non-obvious.** Cost-to-serve accounting is routine in freight and distribution and essentially absent from small residential service, where price is set by service level and competitor comparison. The join itself is one afternoon.

**Bounded test with a real no.** Apply the surcharge to ~90 accounts, not 900. **Success: under 8% of them cancel within two quarters. Failure: over 15% cancel — the surcharge exceeds their willingness to pay; revert and eat the geography.**

**Two cautions I'd take seriously.** Size the surcharge at cost, not punitively — those outliers still carry contribution above their marginal drive, and you'd be destroying real margin to improve a ratio. And **keep the service-area polygon internal.** In a three-town word-of-mouth market, publishing a boundary reads as announcing withdrawal; quote the surcharge case by case instead.

## 4. Most contrarian hypothesis worth testing

**Your CAC ceiling is not a number — it's a function of geography. You should be willing to pay several times your normal acquisition cost for a customer next door to an existing one.**

Concretely: a referral bounty **3–5× your standard rate for a same-street neighbor**, sized against the drive you avoid rather than against your usual bounty.

Conventional wisdom says never pay above your CAC ceiling. But an in-cluster account carries near-zero marginal drive for its entire lifetime; an out-of-cluster account can carry 20–40 dedicated minutes, four times a year, forever. **These are not the same product and should never have shared an acquisition budget — or a price.** Your customers are also the only people with door-to-door social access on precisely the streets where your marginal cost is zero.

The logic runs in reverse too, but with a condition: it can be rational to *discount* an in-cluster account below list. **Declining** an out-of-cluster account at full price only makes sense once you're actually capacity-constrained — which, given the argument in §2, you probably aren't. Until then, surcharge them; don't refuse them.

**Falsifier:** if fewer than 3 of your next 40 customers produce a same-street referral at the elevated bounty, the social channel doesn't exist at that geography. Cost of finding out: only the bounties you actually pay, which occur only on success.

## 5. Cheapest high-information experiment

```
Hypothesis: A material share of the 40% is addressable — the drive between
  consecutive same-day stops is inflated because those stops were never
  chosen for geography in the first place.

Critical assumption tested: That your daily stop sets are geographically
  near-random rather than already about as tight as your towns permit.

Experiment (this week):
  1. Pull the last 20 working days of phone GPS / timestamp logs.
  2. Tag every drive leg into exactly four buckets:
       (a) shop/home -> first stop, last stop -> shop/home   [depot tails]
       (b) legs to a supply or restock stop
       (c) legs between two service stops                    [inter-stop]
       (d) legs returning to an address already attempted today
                                                    [no-access re-drives]
  3. Re-run each of those same days' stop sets through your existing
     optimizer; record its best achievable total drive time.
  4. One query against work orders: what % of the last 12 months of
     quarterly services required interior access or the customer present?
  5. Ten minutes with your vendor. Two questions only:
       - Does it support due-date windows/ranges rather than fixed dates?
       - Can it optimize across a multi-week horizon, not one day at a time?

Resources: ~3 hours, $0, data you already own, plus one vendor call.

Measured outcomes:
  (a) the four-way split of the 40%
  (b) median inter-stop leg, in minutes
  (c) gap between your actual daily route time and the optimizer's best
      for the identical stop set
  (d) share of services requiring customer presence
  (e) vendor yes/no on windows and multi-day horizon

Success threshold: median inter-stop leg > 8 min AND each day's stops span
  most of your service area rather than one town — AND (d) is under ~40%.
  The set-selection problem is real and actionable -> execute 3.1 now.

Failure threshold: your actual route time is within 10% of the optimizer's
  best for the same stop set AND median inter-stop leg is under ~6 min.
  Routing is already at its floor for your geography. Stop spending on
  routing entirely; go straight to 3.2 and 3.3.

Learned either way: the four-way decomposition. Depot tails, no-access
  re-drives, restock trips and genuine inter-stop distance are four
  different problems with four different cures, and you've been treating
  them as one number nobody has measured. Note that depot tails and
  restock legs sit OUTSIDE what any route optimizer models — if those
  are large, that alone explains "helped a bit."

If validated: convert all new sales to service windows + street-assigned
  days this month; redirect every inbound reschedule request to an
  on-route date.

If falsified: the 40% is structural. Reprice for it (3.3), fill the
  truck (3.2), and stop buying routing software.
```

## 6. Kill list — the instructive failures

- **Four 10-hour days.** Only depot tails shrink, and those are maybe 8–15% of the day [ESTIMATE]. So this cuts ~2–3% of field time, not 20%. Several states also pay daily overtime past 8 hours, which can make it net-negative.
- **Longer-residual chemistry to delete visits.** The EPA label is federal law and caps application frequency and rate — you can't buy past it. And the interval is set by reinfestation pressure, not residual half-life.
- **"Two scheduled visits + unlimited free callbacks."** Superficially deletes ~1,800 truck rolls. Actually converts 1,800 *plannable, batchable* stops into unscheduled, time-pressured, geographically random ones — the worst possible input to the exact problem you're solving.
- **HOA block contracts as a density play.** An HOA generally can't bind individual owners to pest service on their own dwellings; that authority usually stops at common areas. The realistic version is an endorsement plus an opt-in group rate — a marketing channel with a partial take rate, not a 40-account block.
- **Paying a competitor to service your stranded far-town accounts.** Hands your most likely predator the addresses, service history, and an ongoing relationship for exactly the accounts they most want. A clean no-cash *trade* of accounts survives this objection; wholesale servicing does not.

## 7. What may still be missing

- **Seasonality — the largest unexplored space.** I couldn't examine the monthly distribution of your scheduled work. If your book is seasonally peaked rather than anniversary-flat, the diagnosis could shift entirely to a low-density-winter problem with a different cure.
- **Dual-purposing drive time rather than eliminating it.** Hands-free renewal and collection calls, voice-dictated notes that kill end-of-day admin, audio recertification credit. Converts part of those hours from pure cost into productive time for the price of a headset. Unsearched.
- **Remote triage before rolling a truck.** A photo or 3-minute video on a callback deflects some share of unnecessary drives. Borrowed from telehealth; not explored.
- **Channel partners that deliver pre-clustered accounts:** property managers, single-family-rental portfolio owners, builders, home-warranty companies. Probably better than HOAs and barely examined.
- **No-access re-drives.** The experiment measures them; I proposed no cure. The standard ones — gate codes and lockbox authorization on file, dog-on-property flags, standing service-regardless-of-presence consent — went unsearched.
- **No external verification.** Software capabilities, regulatory specifics, and industry benchmarks here are unverified.

## 8. Assumptions this rests on

1. **~1–3 field techs**, deduced from 900 × 4 ÷ ~250 days ≈ 14 stops/day. *If you run 4–6*, your real workload far exceeds 3,600 scheduled services — meaning callbacks, initials and one-offs dominate, and *those* are your drive problem, not the quarterly book.
2. **You are not one of the drivers.** *If you are*, every incentive-and-pay argument evaporates — there's no principal-agent problem to fix.
3. **Most quarterly service is exterior, customer not required.** *If not*, 3.1 causes churn and you should price the date rather than assign it. Measured in §5.
4. **Your agreement names a frequency, not a date.** *If it names a date*, freeing due dates needs a contract change and migration rides renewals only.
5. **The three towns are near-contiguous.** *If they form a line or are widely separated*, inter-town drive is structural, the routing prize goes to near zero, and 3.3 becomes the whole answer.
6. **Quarterly service runs year-round.** In a northern market the winter quarter is often deferred or bundled, which would make the real stop distribution nothing like 14/day.

---

**If I'm right about one thing only:** stop measuring drive percentage and start measuring gross margin per truck-day. The first number can only get less bad. The second has no ceiling.

Correct any of those six assumptions and I'll revise. The full search log — 40 candidates, the adversarial audit, and the 15 that were killed — is available if you want it.