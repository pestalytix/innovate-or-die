# ADR-002 regression — Stage 0 single-turn fix, measured

**Date:** 2026-08-19 (runs) / 2026-08-20 (written) · **Provider:** codex ·
**Model:** `gpt-5.6-terra` · **Case:** `eval-route-density`

The first **same-provider, same-model, same-prompt pair across two protocol
versions** in the eval history. It is both the ADR-002 regression test and the only
clean measurement of a protocol-version effect.

This is a **post-baseline measurement and does not revise iteration-1.** The
iteration-1 tier means stand as the v2.0.0 record; blending this run into them would
produce a 4-plus-1 version mixture, exactly what the version-span banner forbids.
Both arms of both versions are preserved under `evals-workspace/adr002-regression/`.

## The defect

v2.0.0 Stage 0 said to ask up to three clarifying questions "then proceed
regardless" — which presumes a conversational host. Under `codex exec` there is no
second turn, so the run returned **771 bytes of questions and nothing else**, skipping
the entire workflow. It was the only negative case in the whole baseline.

v2.0.1 relocates the questions: gaps become labelled assumptions surfaced in the
Stage 6 delivery, each noting what changes if wrong. A standalone question block has
nowhere to live in the canonical output structure, so ending in questions is
structurally impossible rather than merely discouraged.

## Result

| | v2.0.0 | v2.0.1 |
|---|---|---|
| `delivers_answer` | **FAIL** | **PASS** |
| question-final lines | 3 | **0** |
| response size | 761 chars | **5,123 chars** |
| recommendation markers | absent | **present** |
| `failure_mode` | `stage0-stall` | none |
| with_skill assertions | 1/7 | **5/7** |
| without_skill assertions | 4/7 | 2/7 |
| **case delta** | **−0.4285** | **+0.4285** |
| with_skill tokens | 8,058 | **28,366** |
| with_skill duration | 16s | **166s** |

**A 0.857 swing**, from worst case in the baseline to tied-best.

## Cost of the fix

**3.5x the tokens, 10.1x the duration.**

That is the fix working, not a regression: v2.0.0's cheapness *was* the defect. A run
that asks three questions and stops is fast because it does nothing. The v2.0.1 cost
is the cost of actually executing the protocol.

## Confidence

**The categorical result stands and is outside the noise band.**
`delivers_answer` is a **mechanical** check — pure Python over the response text,
deterministic by construction, identical across grading draws. The failure mode moved
from present to absent, which is not a matter of degree.

The 0.857 assertion swing is an order of magnitude larger than the largest observed
grader shift (0.286 on a single case; see `2026-08-19-grader-variance.md`), so the
direction survives grader noise comfortably.

**Magnitude figures carry single-draw uncertainty.** The 1/7 and 5/7 assertion counts
each come from one grading pass, before N=3 majority voting was introduced. The exact
delta should be read as approximate.

**n=1 per version.** One pair cannot separate the version effect from `gpt-5.6-terra`'s
known ~6-fold case-to-case cost variance. Strong evidence on the **stall** — a
categorical failure now absent, corroborated by two independent signals. Weaker
evidence on the **magnitude** of the improvement.

## Tier-level confirmation (iteration-2)

The full Codex workhorse tier was later re-run under v2.0.1 with N=3 majority grading.
Restricted to the **iteration-1 assertion set** (iteration-2 added three actionability
assertions, so the raw pass rates have different denominators and are not directly
comparable), the tier deployed delta was **+0.2857**, against iteration-1's two
observed draws of +0.1357 and +0.0750.

**+0.2857 is outside the observed 2-draw grader range.** Two caveats attach:
iteration-1 grades are **single draws** while iteration-2 uses **N=3 majority**, so the
grading *method* changed alongside the protocol version; and **n=2 draws is a weak
variance bound** — it establishes that grader noise is non-trivial, not its true spread.

`eval-route-density` itself moved **-0.4285 -> +0.4286** on the same assertion set, and
**5 of 5 with_skill arms activated with no Stage 0 stalls anywhere** in that tier.

## What this does not settle

Whether the fix changes tier-level results is measured separately by the iteration-2
Codex workhorse tier, run entirely under v2.0.1 with N=3 majority grading. Projecting
a tier delta from this single case would repeat the version-blending error this
document exists to avoid.
