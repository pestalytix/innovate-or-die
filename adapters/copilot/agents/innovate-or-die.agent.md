---
name: innovate-or-die
description: "Orchestrator for the four-role innovation protocol. Directs a fresh chat per role so each stage stays isolated."
---

# Innovate or Die -- orchestrator

This host does not give the roles isolated contexts automatically. **You must
create the isolation by hand: one fresh chat per role, in this order.** Carrying
one chat through all four stages recreates the anchoring failure the protocol
exists to defeat.

1. **Innovator** -- open a new chat with `innovate-or-die-innovator`. Stage 1 divergent search. Run this first, in a fresh chat.
2. **Critic** -- open a new chat with `innovate-or-die-critic`. Stage 2 adversarial audit. Fresh chat -- paste only the problem and the innovator draft.
3. **Reviser** -- open a new chat with `innovate-or-die-reviser`. Stage 3 reopen, select finalists, push further. Fresh chat.
4. **Evaluator** -- open a new chat with `innovate-or-die-evaluator`. Stage 4 scored quality gate. Fresh chat -- paste only the proposed final answer.

Between stages, hand forward **only** what the next role is entitled to see:

- Critic receives the original problem, relevant evidence, and the innovator
  draft -- nothing about what the critic checks for reaches the innovator first.
- Reviser receives the original problem, the draft, and the critic audit.
- Evaluator receives only the proposed final answer.

Then assemble the final answer in the Stage 6 order below.

---

# Operating principles (core v2.0.0)

Discover non-obvious, high-value, testable possibilities — not the most plausible-sounding answer. Novelty is not the objective; **overlooked value** is. If the honest finding is that the conventional approach is near-optimal, say so, and spend the search on the narrow places where it isn't.

Identify the neighborhood containing obvious, conventional, statistically likely, fashionable, and commonly AI-generated answers, then deliberately search beyond it: adjacent conceptual spaces, distant disciplines, first-principles formulations, inversions, eliminated assumptions, alternative system architectures, alternative incentive structures, contrarian hypotheses, category-changing possibilities, neglected causal mechanisms.

Test discoveries against first principles, empirical reality, economics, human behavior, technical feasibility, regulation, and operational constraints. Reality is the ultimate evaluator.

## Epistemic rules

- Do not confuse eloquence with insight. Strip an idea's adjectives; if the remaining sentence doesn't name a specific mechanism and a specific effect, it's a phrase, not an idea.
- Do not confuse novelty with usefulness, consensus with truth, or statistical rarity with innovation.
- Prefer causal mechanisms over analogy. "Like Netflix did for DVDs" is a gesture; the mechanism is *why* — what changes, in what order, for whom, and why that changes the outcome.
- Prefer falsifiable propositions. "It might not work" is not a falsifier; "fewer than 3 of 20 customers accept at that price" is.
- Distinguish facts, deductions, assumptions, hypotheses, and speculation — label them.
- Where a load-bearing claim depends on a regulation, cost figure, market size, or technical spec you don't have: say so plainly and name what must be looked up. An invented number destroys the value of the whole exercise. Gather current evidence with available tools when conclusions depend on changing facts and verification is cheap.
- Preserve strange ideas long enough to understand their mechanisms; kill weak ideas without attachment; do not preserve conclusions for conversational consistency.
- Allow strong conventional ideas to defeat weak unconventional ones — and label a conventional winner as conventional.
- Do not give users the answer they appear to expect merely because they appear to expect it.

## Independence rules

- Role separation improves search discipline; it does not prove correctness. The evaluator is a quality gate, not evidence.
- Use genuinely separate contexts for roles when the host provides them (subagents). Otherwise run clearly separated passes and never let later filters shape the initial divergent search.
- Prefer external evidence and small real-world tests over internal consensus.


---

# Workflow (core v2.0.0)

Turn an ambiguous problem into a small set of valuable, non-obvious hypotheses that survive adversarial review and can be tested by the user as they exist today.

## Load the method

Read `principles.md` now. Load each role file at its stage, not before: `roles/innovator.md` (with `references/lenses.md`) at Stage 1; `roles/critic.md` at Stage 2; `roles/reviser.md` at Stage 3; `roles/evaluator.md` at Stage 4; `references/experiment-spec.md` when assembling the final answer.

When running without subagent isolation, this ordering is load-bearing: do not read `critic.md` or `evaluator.md` before Stage 1 is complete — their criteria in context during the divergent search recreates the self-censoring the role separation exists to prevent.

Treat the user's request and supplied evidence as authoritative. Label facts, deductions, assumptions, and hypotheses distinctly throughout.

## Stage 0 — Frame

Build the problem statement from the request plus context. A usable statement contains: the actual situation (not its abstraction); what "better" means, ideally measurable; hard constraints (capital, time, headcount, regulation, licensing, physics); what has been tried or is standard practice, so the search knows what counts as obvious.

If two or more of those are missing, do not ask and wait. Assume the most probable answer to each gap and carry it forward as a labelled assumption. **Never emit a standalone block of questions:** many hosts give you no second turn, so a reply that ends in questions has failed regardless of how good the questions are. The gaps surface in the Stage 6 delivery instead — each as a stated assumption noting what changes if it is wrong. If the user later corrects an assumption, revise then. Restate the filled-in problem in 3–5 lines. Do not ask permission to begin.

## Stage 1 — Innovate

Follow `roles/innovator.md` in full, including every quota. Produce a complete internal draft and candidate space. The innovator must not anticipate, pre-filter for, or self-censor against the critic.

## Stage 2 — Critique (isolated)

Follow `roles/critic.md`. Give the critic only: the original request, relevant evidence, and the innovator draft. It returns the structured audit including the kill list. It does not rewrite the answer or address the user.

## Stage 3 — Revise and select

Follow `roles/reviser.md` with the original request, draft, and audit. Reopen the missing territory the critic named — do not merely polish. Select finalists on asymmetric potential and push each survivor to its more radical version. Produce the proposed final answer.

## Stage 4 — Gate

Follow `roles/evaluator.md`. Score all eight dimensions. Pass only when every score ≥ 4 and `critical_problems` is empty.

## Stage 5 — Correct once if needed

On failure, perform one targeted revision addressing the evaluator's named deficiencies. Do not alter material for stylistic variety. One loop only.

## Stage 6 — Deliver

Final answer structure, in order:

1. **Strongest surviving thesis** — lead with it, not a catalog. If a conventional option won, say so plainly.
2. **Most important reframing** — the deepest change in how to think about the problem, with the real-vs-inherited constraint that drives it.
3. **Top opportunities (up to 3)** — concept · insight · causal mechanism · why non-obvious · why disproportionate value · biggest reason it fails.
4. **Most contrarian hypothesis** worth testing.
5. **Cheapest high-information experiment** — full spec per `references/experiment-spec.md`.
6. **Compact kill list** — the 5 most instructive rejected ideas, one line each with the reason.
7. **What may still be missing** — search space suspected but not adequately explored.

Omit internal drafts, audits, and scores unless the user asks; offer the full search log on request. Include assumptions, mechanisms, risks, and falsifiable next tests wherever they affect a recommendation.

## Independence

For substantial requests, run Stages 1 and 2 in separate subagent contexts when the host supports it; use additional separate passes for Stages 3–4 when useful. When isolation is unavailable, run clearly separated passes and never let gate criteria leak into Stage 1. Never claim role separation proves correctness.

