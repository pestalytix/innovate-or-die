A few likely root causes before jumping to fixes: sales selling to bad-fit accounts, a activation gap (the call happens but nobody reaches real first value), or setup friction specific to this segment (subcontractors are often migrating from spreadsheets/paper, not a prior SaaS tool). Worth pulling churn-by-cohort data (referral source, company size, trade type) and doing 5-10 exit interviews before betting on any single fix — but here's a spread of approaches across the levers you mentioned.

**Business model changes**
- **Paid onboarding / setup fee.** Counterintuitively, charging for onboarding (even a modest fee) filters out low-commitment signups and raises psychological investment — sunk-cost effect measurably improves retention in usage-heavy B2B tools.
- **Delay monetization to first value.** Don't start the billing clock until a usage milestone hits (first job scheduled, first invoice sent). Shifts risk from customer to vendor, which forces the org to actually prioritize activation.
- **Annual-only or annual-discounted contracts at signup**, paired with a right-sized trial — reduces the "try it for a month, bail" pattern that shows up as logo churn in the data.
- **Reconsider ICP/qualification.** If churn concentrates in a segment (e.g., sole proprietors vs. 20-person crews), the fix may be sales/pricing tiering that steers unqualified leads elsewhere rather than any onboarding change.

**System/architecture changes**
- **Data import tooling as a first-class feature**, not a manual step in the call — auto-import from QuickBooks, Procore, or common spreadsheet formats. For subcontractors, migrating existing job/customer data is probably the single biggest hidden switching cost, and it's currently sitting inside a human-run call instead of being solved with software.
- **Trade-specific templates/presets** (electrical vs. plumbing vs. framing) so the product ships pre-configured instead of requiring blank-slate setup — reduces both call length and time-to-first-value.
- **In-app activation instrumentation**: define concrete activation events, build a health/risk score per account, and trigger automated or CS interventions at day 3/7/14/30 instead of relying on the single 45-minute call plus static docs to carry the whole first 90 days.
- **Sandbox/demo data mode** so users can experience value before committing their real (messy) business data — decouples "seeing the product work" from "doing the tedious migration."

**Process/org changes**
- **Replace the single call with a milestone-based CS motion** — proactive touchpoints tied to usage data rather than a calendar event, so drop-off after the call doesn't go unnoticed until renewal/cancellation.
- **Cohort or group onboarding** for smaller accounts — cheaper to run than 1:1 calls and creates peer accountability, which tends to help habit formation more than documentation does.

My starting recommendation: before building anything, segment the churned cohort to see whether this is a sales-qualification problem, a data-migration problem, or a habit-formation problem — the fix differs a lot depending on which one dominates, and construction subs churning at 90 days smells most like unmigrated data/no habit formed rather than the call itself being bad.