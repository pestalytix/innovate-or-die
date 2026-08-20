# Note — cross-host skill activation variance

**Opened 2026-08-19** from iteration-1 evals. Not a protocol matter (ADR-002 scope
decision); tracked here as its own workstream.

**Status: mechanism UNKNOWN.** Three hypotheses have been proposed and all three are
falsified. They are kept below with their falsifying observations, because knowing
what the mechanism is *not* is the only durable result so far.

> **Detection changed at core v2.1.0 ([ADR-004](ADR-004-activation-banner.md)).**
> Every row below was recorded before the activation banner existed, by one of two
> methods: an observed `Skill` tool call in the Claude event stream, or — on Codex,
> which exposes no tool-call stream — a seven-regex marker vote. From v2.1.0 the
> delivery opens with `⟦innovate-or-die v<version>⟧`, so activation is an exact
> string match, and the Codex leg records a banner label instead of
> `heuristic:markers`. **Label changed after external review #2:** the Codex leg
> emits `inferred:banner`, not `observed:banner` — a banner is output-side
> evidence, the same kind the Perplexity rows below already refuse to call
> `observed`. Codex `timing.json` files written before this change retain the old
> `observed:banner` string and have **not** been rewritten; they are the record of
> what the harness emitted at the time. **Counts before and after that line were produced by
> different instruments and must be labelled as such rather than pooled.** The
> banner also makes the OBSERVE-AND-ABORT survey below workable on any host that
> streams tokens, not only on hosts that emit tool-call events — which is what
> makes a real denominator affordable.
>
> The banner does not make activation more likely. It makes a miss visible. This
> workstream — why the description does not fire — remains open and unexplained.

## Observations (claude-sonnet-5 unless noted)

| case | register | activation method | activated | tokens |
|---|---|---|---|---|
| `eval-route-density` | casual | inferred (pre-stream-json) | **YES** | 523,224 |
| `eval-dental-no-shows` v1 | precise | inferred | no | 40,923 |
| `eval-dental-no-shows` v2 | precise | **observed** | no | 40,042 |
| `eval-municipal-water-loss` | precise | **observed** | no | 41,813 |
| `eval-bookstore-events` | casual | **observed** | no | 38,894 |
| `eval-saas-onboarding-churn` | precise | **observed** | **YES** | 610,878 |
| `eval-route-density` (repeat) | casual | **observed** | **YES** | 767,382 |

Counts, deliberately not rates: **3 of 7 `with_skill` runs activated; 2 of 5 by
observed method.** n is far too small for a percentage to carry meaning.

**Repeatability.** `eval-route-density` was re-run under the current harness as a
repeatability test: it had activated before the mid-baseline pause (a
quota-management stop; see the results files), and it activated again (observed).
Same prompt, activation reproduced — so activation is not per-prompt nondeterministic
in this case, and the earlier inferred data point is corroborated by an observed
one. Cost varied substantially between the two runs on the identical prompt
(523,224 -> 767,382 tokens, +47%), so run-to-run *cost* is far less stable than
run-to-run *activation*.

Codex (`gpt-5.6-terra`) activated on both dental versions and on every other case,
stalling only at Stage 0 on route-density — a different failure entirely (ADR-002).

Every non-activated run shows `turns: 1` and `tools: {}` — no tool call attempted at
all — and costs within a few percent of its own control arm. A non-activated
`with_skill` run *is* a baseline run.

## Banner emission — Codex workhorse, v2.1.0 (iteration-3)

**Measured 2026-08-20**, the first runs under [ADR-004](ADR-004-activation-banner.md).
Five `with_skill` runs, `codex exec` / `gpt-5.6-terra`, one per eval case, at commit
`bc818f3` with a clean tree. `with_skill` only — the control arm has no protocol and
cannot emit a banner, so it would measure nothing here.

| case | banner on line 1 | version | activation method | tokens |
|---|---|---|---|---|
| `eval-route-density` | **yes** | 2.1.0 | `observed:banner` | 29,184 |
| `eval-dental-no-shows` | **yes** | 2.1.0 | `observed:banner` | 21,161 |
| `eval-municipal-water-loss` | **yes** | 2.1.0 | `observed:banner` | 68,605 |
| `eval-bookstore-events` | **yes** | 2.1.0 | `observed:banner` | 50,873 |
| `eval-saas-onboarding-churn` | **yes** | 2.1.0 | `observed:banner` | 17,052 |

**5 of 5**, in every case the exact string `⟦innovate-or-die v2.1.0⟧` as the first
line — no code-span wrapping, no preamble in front of it, no version drift. No model
mismatches; all five resolved `gpt-5.6-terra`.

**What this does and does not support.**

- It is a **count, not a rate**, and n=5 on one host and one model. The ADR predicts
  emission well above the 71% seen on Stage 6 item 5 because the banner is item 0 and
  carries no generation load. 5 of 5 is consistent with that prediction and does not
  establish it.
- **There is no ground truth on Codex.** `codex exec` exposes no tool-call stream, so
  both the banner and the old marker heuristic are output-side inferences. This
  measures that the banner *is emitted*, not that emission tracks activation. The
  check that can establish the latter is the pre-registered Claude run, where an
  observed `Skill` tool call is independent evidence — it is **quota-blocked** and
  sits in the session-state backlog.
- **The sample contains no negatives.** All five activated, so nothing here tests what
  the banner does when the skill does not fire. On this host it never has.
- **The old and new instruments agreed 5 of 5.** `marker_count` ranged 3–5, so the
  seven-regex vote would have called every one of these activated too. Concordance
  with no disagreement and no negatives is weak evidence — it shows the banner did not
  make detection *worse* on the cases where the old signal was already unambiguous.
- **Cost is not a version comparison.** Iteration-2 (v2.0.1) ran the same five cases
  on the same model at 15,007–27,696 tokens; iteration-3 ranges 17,052–68,605. One run
  per case, per version, with a different protocol and no repeated trials — run-to-run
  cost on an identical prompt has already been observed to vary 47% on this project.
  Nothing here supports a claim that v2.1.0 costs more.

Raw runs are in `evals-workspace/iteration-3/` (gitignored). Recorded here rather
than as an `evals/results/` file because it is an activation measurement, not a
paired eval — there is no delta to report, and `report.py` generates paired
documents only.

## Banner emission — Perplexity Enterprise Computer, v2.1.0

**Measured 2026-08-20** by Ken. Two complete runs, same prompt (the README's
windshield-time example), flat zip `v2.1.0` installed as a Computer skill. The
variable was the **orchestrator model**, which Perplexity lets the user select —
an axis no other host here exposes.

| run | orchestrator model | banner on line 1 | Stage 6 structure | activation method |
|---|---|---|---|---|
| 1 | pinned, GLM 5.2 | **yes** | full | `heuristic:banner` |
| 2 | default (multi-model) | **yes** | full | `heuristic:banner` |

**2 of 2**, across two model configurations. Run 2 additionally declared its
Stage 0 assumptions up front ([ADR-002](ADR-002-stage0-single-turn.md) behaviour)
and issued two explicit regulatory deferrals.

**Method is `heuristic`, not `observed`.** Perplexity exposes no tool-call
stream, so the banner is an output-side inference exactly as it is on Codex.
Recording it as `observed:banner` — as the Codex leg does — would overstate it;
the distinction this project draws is between a *seen tool call* and an *output
marker*, and this is the second kind. The Codex rows above carry the same
limitation and the same caveat applies: this measures that the banner is
emitted, not that emission tracks activation.

**No cross-host rate.** Three hosts now have counts — Claude 3 of 7 activations
(mixed inferred/observed), Codex 5 of 5 banners, Perplexity 2 of 2 banners — and
they must not be pooled. They were produced by **three different instruments** on
three different denominators: an observed `Skill` tool call, an exact-string
banner match on a CLI, and a human reading two chat transcripts. Standing rule:
counts before and after the v2.1.0 instrument change are not pooled either.
Summing any of these into "10 of 14" would be arithmetic performed on
incommensurable measurements.

**What 2/2 does add** that the Codex run cannot: emission survived a change of
orchestrator model. Every other banner measurement on this project holds the
model fixed. It remains n=2, on one host, one tier, one prompt.

**Note the sample contains no negatives here either.** Both runs activated, so
nothing in this row tests what the banner does when the skill does not fire —
the same gap flagged for Codex above. Across all three hosts the only negatives
on record are Claude's, where ground truth exists.

## Dead hypotheses

**H1 — Exclusion-clause match. FALSIFIED.** The v1 dental prompt opened "Evaluate what
would most reduce…", which reads as decision analysis, the use the `description`
field tells agents to decline. Prediction: rewording to remove that framing would
restore activation. The v2 rewrite did exactly that. **It still did not activate**
(40,042 tok, observed, vs 40,923 for v1). Near-identical cost across two different
prompts also argues against randomness — the behaviour looks systematic.

**H2 — Conversational register. PRE-REGISTERED AND FALSIFIED, in both directions.**
Hypothesis: dispatch keys on casual, frustrated-user phrasing matching the
description's trigger phrases, and misses precise, formally-specified prompts.
Predictions recorded in `evals-workspace/iteration-1/PREREGISTERED-PREDICTION.md`
*before* the runs:

| case | register | predicted | actual |
|---|---|---|---|
| `eval-bookstore-events` | casual | activate | **missed** |
| `eval-saas-onboarding-churn` | precise | miss | **ACTIVATED** |

Wrong on both, in opposite directions. Not merely unsupported — inverted.

**H3 — Near-literal trigger-phrase overlap. FALSIFIED before testing.** Proposed
post-hoc when H2 died: route-density ends "what are we missing here?", a near-match
for the description's "what everyone is missing". `eval-saas-onboarding-churn`
contains no trigger phrase and activated anyway.

## Harness validation

The negatives were checked for a harness cause before being treated as findings:

- **In-band positive:** `eval-saas-onboarding-churn` activated under the *same*
  stream-json code path that produced the negatives, so the harness is not broken.
- **Skill-present assertion added:** a `with_skill` arm whose workspace lacks
  `.claude/skills/innovate-or-die/SKILL.md` now hard-fails rather than recording a
  run that would masquerade as a non-activation. Inverse of the contamination assert.
- **Raw stream traces are now persisted** per run (`trace/stream.jsonl`). They were
  not, for the first three negatives — a gap that made those specific runs
  unauditable after the fact.

## Why this outranks everything else open

A non-activated run is invisible without instrumentation: it looks like the skill
performing badly rather than not running. Correcting for it moved the reported Codex
workhorse delta by **2.7x**. On Claude it is worse than a measurement problem — a
majority of realistic prompts got no skill and no indication of it. **Users cannot
tell.** No protocol improvement matters if the skill does not fire.

## Workstream: description-field optimization

The `description` in `core/skill-meta.json` is the sole activation lever and is
currently unoptimized — written once, never tested. Any change regenerates every
adapter, so it needs its own ADR and a version bump.

### Instrument: activation-only eval with OBSERVE-AND-ABORT

A full `with_skill` run costs ~520k tokens, but **activation is decided in the first
few hundred**. `--output-format stream-json` emits events as they happen, so the run
can be killed the instant a `Skill` tool call is observed — or after a short
no-activation window (first assistant turn completing with no tool call).

That measures activation at roughly **1% of a full run's cost**, which turns a
20+ prompt activation survey from unaffordable into routine. It is the prerequisite
instrument for any further work here: with three hypotheses dead on six data points,
the next one needs a real sample, not another anecdote.

**Discipline:** any fourth hypothesis must be **pre-registered before its test runs**,
as H2 was. H2 was wrong, but recording it in advance is what made its failure
informative instead of forgettable.

### Other candidate work

- Test whether the `Do NOT use…` exclusion clause suppresses legitimate activations
  as well as illegitimate ones — H1 is dead as *the* mechanism but the clause is
  untested in isolation.
- Measure activation per host separately; a description tuned on one dispatcher may
  not transfer.
- Watch the opposite failure: a description broad enough to fire on decision analysis
  or delivery work, which the exclusion clause exists to prevent.
