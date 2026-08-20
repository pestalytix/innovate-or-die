# Eval baseline — claude / claude-sonnet-5

**Date:** 2026-08-19 · **Iteration:** 1 · **Provider:** claude

**Resolved model(s):** claude-sonnet-5 — the resolved id reported by the run, not a requested alias.

Paired design: 4 of 5 cases have a matched valid pair (see exclusions under Two deltas).

> **Version span.** Iteration-1 spans **two protocol versions**: runs before the ADR-002 Stage 0 fix are **v2.0.0**, runs after it are **v2.0.1**. Each arm below is labelled. Cross-version comparisons within this iteration are confounded and flagged where they occur.

> **Statistical modesty.** Five cases, **one run per case, per arm**. Every number here is **directional only** — no repeated trials of the runs themselves, so no variance estimate and no significance. `stddev` across cases measures case-to-case spread, not run-to-run stability. Treat differences of a few points as indistinguishable from noise, and win/loss tallies as anecdote. The qualitative verdicts and named findings carry more weight than any mean here.

> **Aggregation corrected in v2.0.2 per external review finding 5.** The figures in this file were previously computed over **unmatched** arms: `eval-dental-no-shows` contributed a `with_skill` run with no control, so a 5-case `with_skill` mean was subtracted from a 4-case control mean. The tier is now computed over **matched valid pairs only** and this file has been regenerated. What moved: `with_skill` pass rate 0.53 → 0.54, delta 0.14 → 0.15, `with_skill` tokens 299,802 → 364,742, token delta 259,511 → 324,451, n 5 → 4. The narrative below already described this tier as 4-case; the numbers now agree with it. No run was re-executed and no grade was re-drawn.

> **Uncontrolled context (found 2026-08-20).** Both arms of `eval-route-density` on the **flagship** tier drew on the host machine's context — information the prompt did not supply and the paired design does not hold constant. **`with_skill`** recorded the operator's account email domain among its Stage 0 assumptions and carried the inference through its subagent fan-out; it stayed in the intermediate turns and is **not** in the delivered answer. **`without_skill`** offered to query a `BigQuery` dataset connected to the host as an MCP server, and that offer **is** in its delivered answer. So `clean context` held for neither arm of this pair, and the two were contaminated **differently**, not equally — this does not cancel out. Assertion grades score output structure and are unaffected. The blind judge read the delivered answers, so the `eval-route-density` verdict should be read knowing the control's answer carries a host-derived offer the treatment's does not. No other Claude run in any tier shows this. No Codex run shows it either, but Codex exposes no event stream, so absence there is unobservable rather than established. Evidence: [`evals/transcripts/README.md`](../transcripts/README.md#known-confound-uncontrolled-host-context-in-the-flagship-pair).

> **Post-baseline annotation.** LLM-graded assertions were later measured nondeterministic (see `2026-08-19-grader-variance.md`); the grades in this file are **single draws**, not replicated measurements. This file is the v2.0.0 record: annotated, never re-graded.

> **Run order.** Arm order: `with_skill` ran first in every pair (predates the `arm_order_method` field, harness < `d4c7269`). Derived from what the runs recorded, not from the iteration number.

> **Reproducibility.** The redacted raw transcripts behind this file are published under `evals/transcripts/` — per-run `response.md`, `timing.json`, `grading.json` and, where one exists, the raw `trace/stream.jsonl`. `evals-workspace/` remains the **local-only (gitignored)** working tree; `evals/evals.json` plus `evals/runners/` regenerate it, and `evals/runners/redact_transcripts.py` derives the published copy from it.

## What this measures

**Protocol compliance and cost, not independent idea quality.** Three structural reasons, each of which caps what any number below can support:

1. **The assertions derive from the protocol's own output spec.** `falsifier_with_number`, `experiment_spec_complete`, `kill_list_min_5` and the rest test whether the answer has the shape this skill mandates. An arm running the skill is being scored against its own instructions, so a positive delta means *the protocol executed*, not *the reasoning improved*.
2. **The blind judge's dimensions mirror the protocol's evaluator.** non-obviousness, mechanism, testability, honesty and usefulness are close to the gate criteria in `roles/evaluator.md`. Two instruments sharing a rubric with the thing they measure are not independent of it.
3. **Iteration-2 is in-sample.** Its additional assertions were authored after reading iteration-1 outputs, and the cases are the same five. Measurement on observed cases is a consistency check, not a held-out test.

Nothing here establishes that the protocol produces better decisions, or that a reader acting on its output does better than one acting on the control's. That experiment has not been run — see `docs/NOTE-efficacy-roadmap.md` for what it would take.

## Headline

| Metric | with_skill | without_skill | delta |
|---|---|---|---|
| Assertion pass rate | 0.54 | 0.39 | 0.15 |
| Duration (s) | 460 | 36 | 423.83 |
| Tokens | 364,742 | 40,291 | 324450.75 |

### Two deltas

| Delta | Mean | n | Meaning |
|---|---|---|---|
| **deployed** | 0.1429 | 4 | every case, misses and stalls included -- what an installing user experiences |
| **per-activation** | 0.2142 | 2 | cases where the skill fired; activated-but-failed runs included |

Excluded from per-activation: `eval-municipal-water-loss, eval-bookstore-events` — the skill did not fire, so those arms are baseline runs.

Per case (deployed): `eval-route-density` +0.000, `eval-municipal-water-loss` +0.000, `eval-bookstore-events` +0.143, `eval-saas-onboarding-churn` +0.428

Computed over **matched valid pairs only** (4): `eval-route-density`, `eval-municipal-water-loss`, `eval-bookstore-events`, `eval-saas-onboarding-churn`.

Pairs excluded, with reasons:

- `eval-dental-no-shows` — without_skill: no timing.json

_a non-activated with_skill run is NOT invalid -- it is a real deployed outcome and is included in the deployed delta; see `deltas`_

### What the judge actually said

Judge model: requested `claude-sonnet-5`, resolved `claude-sonnet-5`.

> **Limitation.** A Claude-family judge scores both providers. Blind pairwise cancels arm bias WITHIN a provider; cross-provider comparisons carry possible same-family leniency toward Claude outputs.

The verdict *text* is the finding. Read the reasoning, not the tally.

- **eval-route-density** → *with_skill* — A names specific causal levers (density/cadence/incentives) with falsifiable pilot designs and numeric thresholds; B lists plausible diagnostic questions but no mechanism depth or testable claims.
- **eval-municipal-water-loss** → *tie* — Same M36 framework and levers; A is more quantified (N1 exponent, MNF %, accuracy thresholds), B is slightly broader and flags DMA as the one item bordering on capital.
- **eval-bookstore-events** → *without_skill* — A asks sharper diagnostic questions (repeat-customer assumption, which events lose money) that make the next step more concrete and falsifiable.
- **eval-saas-onboarding-churn** → *with_skill* — A names specific causal mechanisms, ranks ideas by evidence strength, and gives a falsifiable experiment with thresholds; B lists plausible levers without mechanisms or falsifiers.

(Tally for completeness only: with_skill 2, without_skill 1, other 1. **At n=5 with one run per case this count is noise and carries no claim.** Answers were shown as 'A'/'B'. Presentation order: index alternation (predates the `presentation_method` field, harness < `d4c7269`).)

## Per case

### eval-route-density — field services, casual

- `with_skill`: 3/7 assertions · 767,382 tok · 979s · v2.0.1
- `without_skill`: 3/7 assertions · 40,099 tok · 30s · v2.0.0
- judge: **with_skill** — A names specific causal levers (density/cadence/incentives) with falsifiable pilot designs and numeric thresholds; B lists plausible diagnostic questions but no mechanism depth or testable claims.

### eval-dental-no-shows — healthcare operations, precise  ·  **control: conventional is near-optimal**

- `with_skill`: 4/8 assertions · 40,042 tok · 24s · v2.0.1 · **skill did NOT activate**
- `without_skill`: no run recorded


### eval-municipal-water-loss — public infrastructure, precise

- `with_skill`: 3/7 assertions · 41,813 tok · 46s · v2.0.1 · **skill did NOT activate**
- `without_skill`: 3/7 assertions · 42,548 tok · 66s · v2.0.1
- judge: **tie** — Same M36 framework and levers; A is more quantified (N1 exponent, MNF %, accuracy thresholds), B is slightly broader and flags DMA as the one item bordering on capital.

### eval-bookstore-events — small retail, casual

- `with_skill`: 3/7 assertions · 38,894 tok · 12s · v2.0.1 · **skill did NOT activate**
- `without_skill`: 2/7 assertions · 38,323 tok · 11s · v2.0.1
- judge: **without_skill** — A asks sharper diagnostic questions (repeat-customer assumption, which events lose money) that make the next step more concrete and falsifiable.

### eval-saas-onboarding-churn — software, precise

- `with_skill`: 6/7 assertions · 610,878 tok · 802s · v2.0.1
- `without_skill`: 3/7 assertions · 40,194 tok · 37s · v2.0.1
- judge: **with_skill** — A names specific causal mechanisms, ranks ideas by evidence strength, and gives a falsifiable experiment with thresholds; B lists plausible levers without mechanisms or falsifiers.

## Opus envelope probe (flagship, n=1, not aggregated)

The 10-run flagship tier was replaced by a single envelope probe (MODEL_POLICY scope amendment). One case, `with_skill` only, `claude-opus-5`, **default effort — the deployed condition on a Max plan**, so the result carries the upward-compatibility claim. **It completed**, so the medium-effort mitigation arm was not run. A `without_skill` arm for this case **does exist on disk** — `claude-opus-5`, v2.0.0, 28,357 tok, non-activated, as a control should be — but it is **excluded from the probe by design**: the probe asks whether the flagship tier carries the protocol at all, which is a one-arm question, and its figures are not aggregated with any tier. It is the run named in the uncontrolled-context banner above.

| | value |
|---|---|
| resolved model | `claude-opus-5` |
| skill version | **v2.0.1** |
| effort | default (deployed condition) |
| tokens | 1,137,884 |
| duration | 1,472s (24.5 min) |
| turns | 15 |
| cost | $4.84 |
| activation | observed:Skill-tool-call |
| tools | `{"Skill": 1, "Read": 12, "Bash": 1, "Agent": 3, "ToolSearch": 2, "WebSearch": 4, "Write": 2}` |

`Agent`x3 is three isolated subagents — ADR-001 D1's isolation executing as designed. `WebSearch`x4 is the protocol gathering external evidence where load-bearing facts were missing, which `principles.md` requires and which no other run in the baseline did. This is the protocol at full fidelity: 24.5 minutes and $4.84 for one question.

### Cost variance caveat — the same prompt, three runs

| run | skill version | tokens | duration | turns |
|---|---|---|---|---|
| sonnet, before the pause (inferred activation) | v2.0.0 | 523,224 | 713s | — |
| sonnet, repeat (observed) | v2.0.1 | 767,382 | 978s | 13 |
| **opus, default effort (observed)** | **v2.0.1** | **1,137,884** | **1472s** | 15 |

**Version confound.** The two sonnet runs are *not* a clean repeat measurement: the first ran v2.0.0 and the second v2.0.1, so the token difference confounds run-to-run variance with the ADR-002 change. Only the sonnet-v2.0.1 vs opus-v2.0.1 pair is a clean same-version comparison. An earlier opus attempt on this prompt also timed out at 1800s where this one finished in 1,472s. **No single cost figure here should be read as representative**; the tier ordering is consistent, the magnitudes are not.

**Resolved post-baseline:** a `gpt-5.6-terra` re-run of `eval-route-density` under v2.0.1 supplied the first clean same-provider cross-version pair — see `2026-08-19-adr002-regression.md`.

## Activation ledger

Raw counts, deliberately not rates — n is far too small for a percentage to mean anything. **3 of 7 `with_skill` runs activated; 2 of 5 by observed method.**

| case | register | version | method | activated |
|---|---|---|---|---|
| `eval-route-density` | casual | v2.0.0 | inferred | **YES** |
| `eval-route-density (repeat)` | casual | v2.0.1 | **observed** | **YES** |
| `eval-dental-no-shows v1` | precise | v2.0.0 | inferred | no |
| `eval-dental-no-shows v2` | precise | v2.0.1 | **observed** | no |
| `eval-municipal-water-loss` | precise | v2.0.1 | **observed** | no |
| `eval-bookstore-events` | casual | v2.0.1 | **observed** | no |
| `eval-saas-onboarding-churn` | precise | v2.0.1 | **observed** | **YES** |

A non-activated `with_skill` run shows `turns: 1`, `tools: {}`, and costs within a few percent of its own control — it *is* a baseline run. Such runs are included in the **deployed** delta and excluded from **per-activation**.

**Mechanism unknown.** Three hypotheses were proposed and all three falsified: the **exclusion-clause** explanation (killed by the v2 dental rewrite, which made the prediction and failed it), **conversational register** (pre-registered, then falsified in *both* directions by bookstore and saas), and **near-literal trigger-phrase overlap** (killed by saas, which contains no trigger phrase and activated). Full record with falsifying observations: `docs/NOTE-activation-variance.md`. No surviving hypothesis.

`eval-dental-no-shows` has no `without_skill` arm on this tier: the restart predicate dropped it after its v2 `with_skill` run failed to activate, so this tier is **4-case**, not 5.

## The route-density result

`eval-route-density` scored **3/7 with_skill and 3/7 without_skill — delta 0.00** — despite activating, spawning subagents, and spending **767,382 tokens against the control's 40,099 (19x)**.

Graded twice: a mechanical-only pass showed 0.00 and the **full LLM pass reproduced 0.00 exactly**. So "did the mechanical set simply miss it?" is answered **no** — the complete assertion set, including mechanism quality, fact/assumption separation and the case-specific inherited-constraint check, finds no measurable difference.

**Interpretation (testable in iteration-2).** The control arm itself scored 3/7 — where the base model natively produces protocol-shaped output, the marginal delta collapses. The delta measures the **gap between base behaviour and the protocol, per problem**, not the protocol in isolation. A problem the model already handles in a protocol-like way leaves the skill nothing to add, at full cost.

The blind judge scored this case *for* `with_skill` on Claude, having scored it for the *control* on Codex flagship — the methods disagree on direction while agreeing there is no large assertion-level gap.

Whether the 0.00 generalises is unknown: `eval-saas-onboarding-churn`, same model and tier, scored **6/7 vs 3/7 (+0.428)** and its control also scored 3/7. Case-to-case variance dominates any tier mean here, which is why the per-case tables matter more than the headline numbers.

## Budget and metering

Eval runs were gated on a **token cap** (3,000,000 new Claude tokens). Two figures were tracked and they differ:

| Figure | Value | Counts |
|---|---|---|
| Driver-counted | 1,990,576 | the unattended driver's own runs |
| **True cumulative** | **2,846,382** | adds a standalone positive-control run (767,382) and a metering probe (88,424) launched outside the driver |

The discrepancy is not an error in either number — the driver could only see runs it started. The **true** figure was the enforced one.

### The token metric misprices small calls

One cold grading call measured **88,424 tokens, of which 85,071 was `cacheCreation`** — the harness caching its own system prompt and tool definitions, charged per invocation and near-independent of payload. Actual response text across all grading and judge calls was ~41,000 tokens, about 1.5% of the projected cost. Under that metric 31 short classification calls would 'cost' more than the entire opus envelope probe (2.65M vs 1.14M) — a run that took 15 turns, spawned 3 subagents and ran 4 web searches. Grading was therefore moved to a **cost basis**.

### Measured: batching changes the price by 6x

| | cold call | serial batch (27 calls) |
|---|---|---|
| cost per call | $0.5201 | **$0.0846** |
| tokens per call | 88,424 | **42,549** |

Run back-to-back, consecutive calls hit `cacheRead` instead of re-creating the cache. Cached share of the token sum stayed at **95.9%**: batching changes *which* cache field is charged, not the fact that ~96% of the token sum is scaffolding rather than work. Iteration-1 grading + judge totalled **$2.73** against a $25.00 ceiling.

> **Neither metric is a verified proxy for subscription weekly-quota weighting.** `cost_usd` is an assumption, labelled as such. How either figure maps to quota consumption is unknown and was not measured.

## benchmark.json (verbatim)

```json
{
  "run_summary": {
    "with_skill": {
      "pass_rate": {
        "mean": 0.54,
        "stddev": 0.21
      },
      "time_seconds": {
        "mean": 459.74,
        "stddev": 502.79
      },
      "tokens": {
        "mean": 364741.75,
        "stddev": 379983.31
      },
      "n": 4
    },
    "without_skill": {
      "pass_rate": {
        "mean": 0.39,
        "stddev": 0.07
      },
      "time_seconds": {
        "mean": 35.91,
        "stddev": 23.08
      },
      "tokens": {
        "mean": 40291,
        "stddev": 1733.33
      },
      "n": 4
    },
    "delta": {
      "pass_rate": 0.15,
      "time_seconds": 423.83,
      "tokens": 324450.75
    }
  },
  "deltas": {
    "deployed": {
      "mean": 0.1429,
      "n": 4,
      "per_case": {
        "eval-route-density": 0.0,
        "eval-municipal-water-loss": 0.0,
        "eval-bookstore-events": 0.1429,
        "eval-saas-onboarding-churn": 0.4285
      },
      "meaning": "every case, misses and stalls included -- what an installing user experiences"
    },
    "per_activation": {
      "mean": 0.2142,
      "n": 2,
      "per_case": {
        "eval-route-density": 0.0,
        "eval-saas-onboarding-churn": 0.4285
      },
      "meaning": "cases where the skill fired; activated-but-failed runs included"
    },
    "excluded_from_per_activation": [
      "eval-municipal-water-loss",
      "eval-bookstore-events"
    ],
    "gap_is": "activation/execution reliability"
  },
  "pairing": {
    "rule": "matched valid pairs only: both arms present, neither carrying model_mismatch, TIMEOUT/UNKNOWN resolution, a harness error, a parse failure, or a null grade",
    "note": "a non-activated with_skill run is NOT invalid -- it is a real deployed outcome and is included in the deployed delta; see `deltas`",
    "pairs_used": [
      "eval-route-density",
      "eval-municipal-water-loss",
      "eval-bookstore-events",
      "eval-saas-onboarding-churn"
    ],
    "excluded_pairs": [
      {
        "slug": "eval-dental-no-shows",
        "with_skill": [],
        "without_skill": [
          "no timing.json"
        ]
      }
    ]
  },
  "resolved_models": [
    "claude-sonnet-5"
  ],
  "provider": "claude",
  "iteration": 1
}
```

## Reproducing

```bash
python3 evals/runners/run_evals.py --provider claude --tier workhorse --model claude-sonnet-5 --iteration 1
python3 evals/runners/grade.py     --provider claude --tier workhorse --iteration 1
python3 evals/runners/judge.py     --provider claude --tier workhorse --iteration 1
python3 evals/runners/aggregate.py --provider claude --tier workhorse --iteration 1
python3 evals/runners/report.py    --provider claude --tier workhorse --iteration 1
```
