# Efficacy roadmap — what would actually test whether this works

**Status:** accepted as future work, 2026-08-20. **Not scheduled.** Nothing here
is in progress, and none of it is a commitment to a date.

Recorded after an external adversarial review whose central finding was accepted:
the existing eval measures **protocol compliance and cost**, not independent idea
quality. This document says what a real efficacy test would require, so the gap
is written down rather than implied by silence.

## Why the current design cannot answer the question

Three structural limits, none of which more runs would fix:

1. **The assertions derive from the protocol's own output spec.** `kill_list_min_5`,
   `experiment_spec_complete` and `falsifier_with_number` ask whether the answer
   has the shape the skill mandates. The `with_skill` arm is graded against its own
   instructions, so a positive delta means the protocol executed.
2. **The judge shares a rubric with the protocol's evaluator**, and — measured — is
   biased toward reframing even where reframing is wrong. See
   [`evals/results/2026-08-20-judge-validity-dental.md`](../evals/results/2026-08-20-judge-validity-dental.md).
3. **Iteration-2 is in-sample.** Its extra assertions were written after reading
   iteration-1 outputs, over the same five cases. That is a consistency check.

## What a real test needs

Roughly in dependency order. Each item is a months-scale piece of work, and the
list is not a plan.

- **A clean host, and this one is a prerequisite rather than an item.** `claude -p`
  on a configured workstation **is not a clean context**. The harness's
  `assert_uncontaminated` checks one thing — that the *skill* is out of scope for
  the control arm — and nothing else; it does not and cannot check what the host
  account already knows. Measured 2026-08-20: on the iteration-1 flagship pair for
  `eval-route-density`, the `with_skill` run took the operator's account email
  domain into its Stage 0 assumptions, and the `without_skill` control offered to
  query a `BigQuery` dataset it knew about only because that MCP server was
  connected to the machine. Neither fact was in the prompt; the two arms were
  contaminated differently, so it does not cancel. **The same failure class was
  already recorded on another host** — Perplexity account memory leaking four
  facts about the user's other projects and location into a fresh session, see
  [`COMPATIBILITY.md`](COMPATIBILITY.md) — where the standing ruling is already
  "use an account with no history, or memory disabled". That ruling was never
  extended to the Claude lane, and it should have been. **On Codex: no leakage
  observed — but Codex exposes no event stream, so absence is unobservable, not
  established.** The scan there could only read delivered answers; the
  intermediate reasoning that carried the leak on the Claude side has no
  equivalent artifact to search. A clean Codex result and an unmeasurable one
  look identical from outside, and must not be reported as the same thing. Future Claude runs must
  come from a dedicated account, or from a session with account context
  demonstrably off, and the demonstration has to be recorded per run the way
  model resolution already is. Until that holds, no lane's numbers are clean
  enough for the items below to mean anything, which is why this is a
  prerequisite and not a nice-to-have.
- **Preregistered held-out cases.** A case set written before the protocol is run
  against it, with assertions authored from the *problem*, never from the
  protocol's output spec, and sealed before any run. Held-out means the author of
  the cases has not read the outputs.
- **Repeated generations per condition.** Every number in the current history is a
  single draw with no variance estimate. Run-to-run variance must be measured
  before any delta is called real; grader variance is already known to be
  nonzero.
- **Arm-order and position randomization.** Judge presentation order is
  randomized per ballot **from harness commit `d4c7269` onward**, recorded as
  `presentation_method` in `judge.json`. Runs judged before it used index
  alternation and carry no such field; their recorded `presented_first` values
  stand. Run arm order — which of `with_skill` / `without_skill` executes first —
  is likewise randomized per case from `d4c7269` onward and recorded as
  `arm_order_index` plus `arm_order_method` in `timing.json`. **Every existing
  run, iteration-3 runs included, predates `d4c7269` and carries no
  `arm_order_index`:** `with_skill` ran first in all of them, so anything
  drifting with wall time loaded onto that arm identically in every pair.
  Commits, not iteration numbers — an iteration is a label the operator chose. Both draws are seeded
  and reproducible, which is what makes them auditable rather than merely
  unpredictable. This does not close the item: randomization removes a
  systematic offset, it does not estimate the residual, and at these ballot and
  case counts an order can still come out lopsided by chance.
- **Compliance and quality scored separately**, by different instruments, and
  reported as two numbers that are never summed. A compliance score is a
  legitimate thing to report — it just is not a quality score.
- **Human raters**, blind to arm, ideally domain practitioners, on a rubric that
  includes *"was the unconventional answer appropriate here?"* — the term the
  current judge lacks.
- **Component ablation.** Quotas, role separation, the critic's checklist and the
  gate are all asserted to carry weight; none has been tested alone. The honest
  current statement is that the quotas force volume and that whether each earns
  its cost is unknown.
- **A decision-outcome measure**, if one can be constructed at all: whether a
  reader acting on the output does better than one acting on the control's. This
  is the question the skill's premise actually rests on and the hardest to
  operationalize.

## Reporting methodology — method prose derives from recorded fields

`evals/runners/report.py` is the only writer of results files, and a results file
is regenerated whenever anything about it changes. Each regeneration re-emits
every sentence from the generator as it stands that day. So **any sentence
describing a method — grading, judging, presentation or arm ordering, activation
detection — must be derived from a field the run itself recorded.**

Ungated prose is silently rewritten: a file recording a 2026-08-19 run comes to
assert a method introduced later, the numbers stay honest while the prose
describing how they were produced becomes false, and the completeness gate cannot
catch it because the section is present and the sentence is well-formed.

Gating on the iteration number does not fix this, it only hides it. `iteration
>= 3` encodes "iteration 3 is when the harness changed" — a fact about history,
not about the artifact in hand. Re-run iteration 1 under today's harness and the
rule describes it wrongly; replay iteration 3 from artifacts the old harness
produced and it describes those wrongly too. **The iteration number is a label
the operator chose, not a record of what the code did.**

The method therefore travels with the artifact: `judge.json` carries
`presentation_method` and `harness_commit`, and each `timing.json` carries
`arm_order_method` beside `arm_order_index`. A missing field produces an explicit
"predates this field" sentence naming the harness commit; an unrecognised value
is reported verbatim rather than mapped to the nearest known one.

The test for a new method sentence is not *"is this true?"* but *"which recorded
field is this read from?"*

## What may be claimed until then

That models running this protocol reliably produce its full output structure —
falsifiers, kill list, experiment spec — which they rarely produce unprompted, at
substantially higher token cost, with activation on Claude Code unreliable for
reasons not understood. Nothing about decision quality.
