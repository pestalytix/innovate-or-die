# Eval baseline — claude / claude-sonnet-5

**Date:** 2026-08-19 · **Iteration:** 1 · **Provider:** claude

**Resolved model(s):** claude-sonnet-5 — this is the resolved id reported by the run, not a requested alias.

Paired design: every case ran twice, with and without the skill, same prompt, same model, clean context. The delta is the result.

> **Version span.** Iteration-1 spans **two protocol versions**: runs before the ADR-002 Stage 0 fix are **v2.0.0**, runs after it are **v2.0.1**. Each arm below is labelled. Cross-version comparisons within this iteration are confounded and are flagged where they occur.

> **Statistical modesty.** Five cases, **one run per case, per arm**. Every number here is **directional only** — no repeated trials, so no variance estimate and no significance. `stddev` across cases measures case-to-case spread, not run-to-run stability. Treat differences of a few points as indistinguishable from noise, and treat win/loss tallies as anecdote. The qualitative verdicts and the named findings carry more weight than any mean in this document.

## Headline

| Metric | with_skill | without_skill | delta |
|---|---|---|---|
| Assertion pass rate | 0.53 | 0.39 | 0.14 |
| Duration (s) | 373 | 36 | 336.76 |
| Tokens | 299,802 | 40,291 | 259510.8 |

### Two deltas

| Delta | Mean | n | Meaning |
|---|---|---|---|
| **deployed** | 0.1429 | 4 | every case, misses and stalls included -- what an installing user experiences |
| **per-activation** | 0.2142 | 2 | cases where the skill fired; activated-but-failed runs included |

Excluded from per-activation: `eval-municipal-water-loss, eval-bookstore-events`.

Per case (deployed): `eval-route-density` +0.000, `eval-municipal-water-loss` +0.000, `eval-bookstore-events` +0.143, `eval-saas-onboarding-churn` +0.428

**Judge model:** requested `claude-sonnet-5`, resolved `claude-sonnet-5`.

> **Limitation.** A Claude-family judge scores both providers. Blind pairwise cancels arm bias WITHIN a provider; cross-provider comparisons carry possible same-family leniency toward Claude outputs.

### What the judge actually said

The verdict *text* is the finding here. Read the reasoning, not the tally.

- **eval-route-density** → *with_skill* — A names specific causal levers (density/cadence/incentives) with falsifiable pilot designs and numeric thresholds; B lists plausible diagnostic questions but no mechanism depth or testable claims.
- **eval-municipal-water-loss** → *tie* — Same M36 framework and levers; A is more quantified (N1 exponent, MNF %, accuracy thresholds), B is slightly broader and flags DMA as the one item bordering on capital.
- **eval-bookstore-events** → *without_skill* — A asks sharper diagnostic questions (repeat-customer assumption, which events lose money) that make the next step more concrete and falsifiable.
- **eval-saas-onboarding-churn** → *with_skill* — A names specific causal mechanisms, ranks ideas by evidence strength, and gives a falsifiable experiment with thresholds; B lists plausible levers without mechanisms or falsifiers.

(Tally, for completeness only: with_skill 2, without_skill 1, tie 1. **At n=5 with one run per case this count is noise and carries no claim.** The judge saw answers as 'A'/'B' with presentation order alternating per case, so position bias cannot align with arm.)

## Per case

### eval-route-density — field services, casual

- `with_skill`: 3/7 assertions · 767,382 tok · 979s · v2.0.1
- `without_skill`: 3/7 assertions · 40,099 tok · 30s · v2.0.0
- judge: **with_skill** — A names specific causal levers (density/cadence/incentives) with falsifiable pilot designs and numeric thresholds; B lists plausible diagnostic questions but no mechanism depth or testable claims.

### eval-dental-no-shows — healthcare operations, precise  ·  **control: conventional is near-optimal**

- `with_skill`: 4/8 assertions · 40,042 tok · 24s · v2.0.1 · **SKILL DID NOT ACTIVATE -- with_skill arm ran as a baseline; exclude from headline delta**
- `without_skill`: no run recorded


### eval-municipal-water-loss — public infrastructure, precise

- `with_skill`: 3/7 assertions · 41,813 tok · 46s · v2.0.1 · **SKILL DID NOT ACTIVATE -- with_skill arm ran as a baseline; exclude from headline delta**
- `without_skill`: 3/7 assertions · 42,548 tok · 66s · v2.0.1
- judge: **tie** — Same M36 framework and levers; A is more quantified (N1 exponent, MNF %, accuracy thresholds), B is slightly broader and flags DMA as the one item bordering on capital.

### eval-bookstore-events — small retail, casual

- `with_skill`: 3/7 assertions · 38,894 tok · 12s · v2.0.1 · **SKILL DID NOT ACTIVATE -- with_skill arm ran as a baseline; exclude from headline delta**
- `without_skill`: 2/7 assertions · 38,323 tok · 11s · v2.0.1
- judge: **without_skill** — A asks sharper diagnostic questions (repeat-customer assumption, which events lose money) that make the next step more concrete and falsifiable.

### eval-saas-onboarding-churn — software, precise

- `with_skill`: 6/7 assertions · 610,878 tok · 802s · v2.0.1
- `without_skill`: 3/7 assertions · 40,194 tok · 37s · v2.0.1
- judge: **with_skill** — A names specific causal mechanisms, ranks ideas by evidence strength, and gives a falsifiable experiment with thresholds; B lists plausible levers without mechanisms or falsifiers.

## benchmark.json (verbatim)

```json
{
  "run_summary": {
    "with_skill": {
      "pass_rate": {
        "mean": 0.53,
        "stddev": 0.19
      },
      "time_seconds": {
        "mean": 372.67,
        "stddev": 476.97
      },
      "tokens": {
        "mean": 299801.8,
        "stddev": 359689.41
      },
      "n": 5
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
      "pass_rate": 0.14,
      "time_seconds": 336.76,
      "tokens": 259510.8
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
  "resolved_models": [
    "claude-sonnet-5"
  ],
  "provider": "claude",
  "iteration": 1
}
```

## Reproducing

```bash
python3 evals/runners/run_evals.py --provider claude --model <alias> --iteration 1
python3 evals/runners/grade.py     --provider claude --iteration 1
python3 evals/runners/judge.py     --provider claude --iteration 1
python3 evals/runners/aggregate.py --provider claude --iteration 1
python3 evals/runners/report.py    --provider claude --iteration 1
```

Raw transcripts live in `evals-workspace/`, which is gitignored; `evals/evals.json` plus these runners regenerate them.
