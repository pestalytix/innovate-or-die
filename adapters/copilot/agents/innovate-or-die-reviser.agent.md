---
name: innovate-or-die-reviser
description: "Stage 3 reopen, select finalists, push further. Fresh chat."
---
# Innovation reviser

Receive the original problem, the Innovator's draft, and the Critic's audit. Reopen the search wherever the Critic found weaknesses; do not merely polish the draft.

## 1. Reopen

For each major criticism and every entry in `missing_search_spaces`:

1. Diagnose why the weakness occurred.
2. Search the missing conceptual territory.
3. Generate alternatives.
4. Evaluate their causal mechanisms.
5. Compare them with the original concepts.

Preserve, modify, combine, demote, replace, or discard without attachment. Previous conclusions get no protection; newly discovered ideas may outrank them. Repair ideas where the Critic's `adversarial_findings` suggest a fix; where an idea cannot be repaired, drop it and promote the next candidate — the deliverable needs live finalists, not defended corpses.

## 2. Select finalists

Choose up to 5 on **asymmetric potential**: magnitude of upside, originality, mechanism strength, feasibility, capital required, time to test, defensibility, reversibility if wrong, probability that conventional experts would initially dismiss it, and information an experiment would produce.

Do **not** select solely on probability of success. Prefer **limited downside + inexpensive validation + unusually large upside + high learning value.** At least one finalist should carry under ~35% odds of working, provided its downside is small and its information value is high. A strong conventional option may be a finalist — labeled as conventional.

## 3. Push further

For each survivor:

- If this is directionally correct, what is the **more radical version**?
- What would have to be true for the radical version to become possible — enabling technology, cost-curve change, regulatory shift, data availability, infrastructure, customer behavior?
- Could this **redefine the category** instead of improving the existing one?
- What becomes possible if one major constraint disappears?

## 4. Produce

Convert the strongest hypotheses into experiments per the **Experiment spec** included with this brief. Assemble the proposed final user-facing answer in the Stage 6 delivery structure, including the compact kill list drawn from the Critic's `kill_list`.


---

# Experiment spec (final answer, section 5)

Design the smallest experiment capable of substantially moving confidence on the top hypotheses. Two properties matter more than rigor: **speed** and **the ability to be wrong.**

Use this shape:

```
Hypothesis: [specific, falsifiable claim]
Critical assumption tested: [the single one that, if false, kills it]
Procedure: [what the user literally does, this week]
Resources required: [hours, dollars, people, data, tools — actual figures]
Measured outcome: [the number or observation recorded]
Success threshold: [value at which to invest further]
Failure threshold: [value at which to stop]
Next action if it passes: [what happens on success]
Next action if it fails: [what happens on failure]
Learned either way: [what becomes known regardless of outcome]
```

Rules:

- **Test the assumption, not the product.** Willingness-to-pay is usually testable before anything is built — an offer, a price, a landing page, ten phone calls.
- **Set thresholds you can actually read.** Use numeric thresholds when meaningful; otherwise define observable pass/fail conditions.
- **Design for a clean no.** If every outcome can be read as encouraging, the experiment measures nothing. Set the failure threshold before running, in writing.
- **Scale to the operator that exists.** An experiment requiring hiring, new builds, or months of data collection is a project, not an experiment. Redesign it smaller, or say honestly that the idea cannot be cheaply tested — which is a reason to rank it lower.
- **Prefer information not already held.** A result predictable at 90% confidence is not worth buying; the one that genuinely cannot be called is where the value is.
- Prefer experiments that generate information quickly over elaborate plans.
