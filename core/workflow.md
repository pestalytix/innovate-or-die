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
