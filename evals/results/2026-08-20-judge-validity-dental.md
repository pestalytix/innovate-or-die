# Judge validity — the judge rewarded novelty on the case built to punish it

**Recorded 2026-08-20**, from an external adversarial review of the public repo.
No new runs: this is a re-reading of judge and grading records already in the
workspace.

This document exists for the same reason as
[`2026-08-19-grader-variance.md`](2026-08-19-grader-variance.md) — it changes how
the blind-judge verdicts elsewhere in the eval history should be read. Grader
variance showed the *assertion* grader is nondeterministic; this shows the
*pairwise judge* carries a directional bias on exactly the case designed to
detect that bias.

## The case

`eval-dental-no-shows` is the control. From `evals/evals.json`:

> The well-established interventions (reminder sequences, deposits/late-cancel
> fees, strategic overbooking, waitlist backfill) are genuinely near-optimal
> here. A correct run says so and labels the winner conventional. A run that
> invents an exotic mechanism to appear innovative FAILS
> intellectual_independence — **this case tests the protocol against
> novelty-forcing.**

Two of its assertions encode that intent: the answer must state the conventional
approach is at or near optimal, and must **not** headline an exotic mechanism.

## What the judge did

The blind pairwise judge picked `with_skill` on this case in **every tier where
it ran** — and its stated reason each time is that the skill's answer *reframed*:

| Tier | Verdict | Judge's reason (verbatim) |
|---|---|---|
| iteration-1 codex/workhorse | `with_skill` | "B reframes the problem with a named psychological mechanism and a falsifiable A/B design with explicit thresholds; A is a solid but conventional confirm-and-escalate playbook." |
| iteration-1 codex/flagship | `with_skill` | "B reframes as perishable-capacity/early-info problem with sharper falsification thresholds and a kill list; A is a solid but conventional confirm-and-recover playbook." |
| iteration-2 codex/workhorse (3/3 ballots) | `with_skill` | "B reframes the causal problem (commitment/activation vs reminders) with named mechanisms and a falsifiable A/B test; A is a solid but conventional checklist." |

In all three the judge treats "conventional" as the demerit. On this case,
conventional is the **correct answer**.

## What the assertions said about the same answers

The assertion grader, scoring the same outputs against the case's own intent,
disagrees with the judge:

| Tier / arm | score | "conventional is near-optimal, labelled" | "does NOT headline an exotic mechanism" |
|---|---|---|---|
| it-1 codex/workhorse `with_skill` | 7/8 | **FAIL** | pass |
| it-1 codex/flagship `with_skill` | 7/8 | pass | **FAIL** |
| it-2 codex/workhorse `with_skill` | 5/11 | **FAIL** | **FAIL** |
| it-2 codex/workhorse `without_skill` | 5/11 | **FAIL** | pass |

The iteration-2 row is the sharpest. The `with_skill` arm scored **identically to
its own control (5/11, delta 0.000)**, failed *both* anti-novelty assertions where
the control failed only one — and the judge still picked it, 3 ballots to 0, for
reframing.

## The finding

**On this case the two instruments point in opposite directions, and the judge
points the wrong way.** The assertion set says the skill did the specific thing
the case was constructed to catch. The judge rewarded it for doing so.

That is a property of the judge, not of the answers. Its rubric —
non-obviousness, mechanism, testability, honesty, usefulness — has no term for
*"was novelty appropriate here?"*, so an answer that reframes scores well on
non-obviousness whether or not reframing was warranted. A rubric that cannot
express "the boring answer was right" cannot detect novelty-forcing, which is the
one failure mode this protocol most needs measured.

## Consequences

1. **Blind-judge verdicts on `eval-dental-no-shows` carry no weight** and should
   not be counted in any tally. The tally is already labelled noise at n=5; this
   case is worse than noise, it is biased.
2. **The bias plausibly extends to every case**, in the direction of favouring the
   `with_skill` arm — the protocol mandates reframing, and the judge rewards
   reframing. No case other than dental has a ground truth that would expose it.
3. **The judge is not independent of the protocol.** Its five dimensions are close
   to the gate criteria in `roles/evaluator.md`. This is stated in the scope
   section of every results file.
4. **Not fixed here.** A judge rubric with an appropriateness term, or a
   held-out case set with known-correct conventional answers, is future work —
   see [`docs/NOTE-efficacy-roadmap.md`](../../docs/NOTE-efficacy-roadmap.md).

No protocol change follows from this. The finding is about the measuring
instrument, and changing the protocol in response to a biased instrument is how a
harness bug becomes a protocol bug.
