# Quality gates (Phases 4, 6, 8)

## Phase 4 — Fake-novelty detector

Run every candidate through these. Anything caught gets named in the kill list with the reason — the kill list is part of the deliverable, because knowing what was rejected and why is itself information.

1. **The rename test.** Restate the idea in the plainest possible words. If the plain version is something the industry already does, it was terminology, not novelty. ("AI-powered dynamic route optimization" → "plan the day's stops in a sensible order" → already standard.)
2. **The AI-bolt-on test.** Does the structure of who does what, who pays whom, and what gets delivered change? If not, and the only change is that a model now produces an output a human used to produce, it's an efficiency gain — real, but not an innovation candidate. Efficiency gains belong in an ops backlog, not here.
3. **The noun-swap test.** Swap the industry noun for an unrelated one. If the idea survives intact, it's generic filler that could have been generated without knowing the problem.
4. **The already-dominant test.** Would a well-informed practitioner say "yes, we all do that"? Being unfamiliar to *you* is not the same as being novel in the field. When you're unsure whether something is already standard practice, say so and flag it for a five-minute check rather than presenting it as new.
5. **The importance test.** Grant that the idea works perfectly. Does the top-line outcome move materially? A technically elegant fix to something that costs 0.4% of revenue is a distraction, however satisfying.
6. **The complexity test.** Count the moving parts and the number of other parties who must cooperate. If a simpler version captures 80% of the value, the complex version is complexity masquerading as innovation — keep the simple one.
7. **The feature-extension test.** Is this "the current thing, but more/faster/with an app"? Extensions are fine work but they are not what this protocol is for; they crowd out the ideas it exists to find.

**Calibration:** killing 8–15 of 30 is normal. Killing zero means the detector didn't run. Killing 28 usually means Phase 3 was timid rather than that the detector is strict.

## Phase 6 — Adversarial checklist

For each finalist, argue against it as someone whose reputation depends on proving it wrong. Work through:

- **Hidden assumptions** — what has to be true that nobody stated? Especially about customer willingness, data availability, and cost of acquisition.
- **Failure mechanism** — name the specific way it breaks, not "execution risk."
- **Customer rejection** — what's the honest reason someone hears this and says no? Habit, distrust, switching cost, embarrassment, and "it's fine already" are the common ones.
- **Economics** — unit economics at 1 customer, at 10, at 100. What's the fixed cost that must be amortized, and how many units does that need?
- **Technical bottleneck** — the one component that has to work and might not.
- **Regulatory or licensing barrier** — say plainly when you don't know the rule and it's load-bearing. Naming the specific statute, license class, or agency to check is more useful than a guess about what it says.
- **Second-order consequences** — what does this do to the rest of the business, to existing customers, to staff, to liability exposure?
- **Incumbent response** — if it works, who copies it, how fast, and does anything stop them? If the answer is "nothing," the idea may still be worth doing, but its value is a time-limited lead, not a moat. Say which.
- **Falsifier** — a specific observation, with a number attached where possible, that would end the thesis. If you can't write one, the idea isn't testable and doesn't belong in the finalists.

Then repair the idea if the critique suggests a fix. If it can't be repaired, drop it and promote the next candidate from Phase 5 — the deliverable needs live finalists, not defended corpses.

## Phase 8 — Experiment spec

Design the smallest thing that would substantially move confidence. Two properties matter more than rigor: **speed** and **the ability to be wrong.**

Use this shape for each of the top 3:

```
Hypothesis: [specific, falsifiable claim]
Critical assumption tested: [the single one that, if false, kills it]
Experiment: [what you literally do, this week]
Resources: [hours, dollars, people, data, tools — actual figures]
Measured outcome: [the number or observation you record]
Success threshold: [value at which you invest further]
Failure threshold: [value at which you stop]
Learned either way: [what becomes known regardless of outcome]
If validated: [next action]
If falsified: [next action]
```

Rules:

- **Test the assumption, not the product.** Willingness-to-pay is usually testable before anything is built — an offer, a price, a landing page, ten phone calls.
- **Design for a clean no.** If every outcome can be read as encouraging, the experiment measures nothing. Set the failure threshold before running it, in writing.
- **Scale to the operator that exists.** For a solo operator or small team, an experiment requiring hiring, new software builds, or 6 months of data collection is not an experiment — it's a project. Redesign it smaller or say honestly that this idea can't be cheaply tested and that this is a reason to rank it lower.
- **Prefer information you don't already have.** An experiment whose result you can predict with 90% confidence is not worth running; the one whose result you genuinely cannot call is where the value is.
