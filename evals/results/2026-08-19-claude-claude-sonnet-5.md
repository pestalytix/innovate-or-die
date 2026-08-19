# Eval baseline — claude / claude-sonnet-5

**Date:** 2026-08-19 · **Iteration:** 1 · **Provider:** claude

**Resolved model(s):** claude-sonnet-5 — this is the resolved id reported by the run, not a requested alias.

Paired design: every case ran twice, with and without the skill, same prompt, same model, clean context. The delta is the result.

> **Statistical modesty.** Five cases, **one run per case, per arm**. Every number here is **directional only** — no repeated trials, so no variance estimate and no significance. `stddev` across cases measures case-to-case spread, not run-to-run stability. Treat differences of a few points as indistinguishable from noise, and treat win/loss tallies as anecdote. The qualitative verdicts and the named findings carry more weight than any mean in this document.

## Headline

| Metric | with_skill | without_skill | delta |
|---|---|---|---|
| Assertion pass rate | 1.00 | 0.57 | 0.43 |
| Duration (s) | 713 | 30 | 683.68 |
| Tokens | 523,224 | 40,099 | 483125 |

### Two deltas

| Delta | Mean | n | Meaning |
|---|---|---|---|
| **deployed** | 0.4286 | 1 | every case, misses and stalls included -- what an installing user experiences |
| **per-activation** | 0.4286 | 1 | cases where the skill fired; activated-but-failed runs included |

No genuine non-activations in this tier, so the two deltas are **identical**. The gap between them is the activation/execution-reliability signal; here it is **0.000**.

Per case (deployed): `eval-route-density` +0.429

**Judge model:** requested `claude-sonnet-5`, resolved `claude-sonnet-5`.

> **Limitation.** A Claude-family judge scores both providers. Blind pairwise cancels arm bias WITHIN a provider; cross-provider comparisons carry possible same-family leniency toward Claude outputs.

### What the judge actually said

The verdict *text* is the finding here. Read the reasoning, not the tally.

- **eval-route-density** → *with_skill* — A names the same core reframe as B but adds quantified falsifiers, cost math, and an explicit fact/assumption split; B stops at a checklist.

(Tally, for completeness only: with_skill 1, without_skill 0, tie 0. **At n=5 with one run per case this count is noise and carries no claim.** The judge saw answers as 'A'/'B' with presentation order alternating per case, so position bias cannot align with arm.)

## Per case

### eval-route-density — field services, casual

- `with_skill`: 7/7 assertions · 523,224 tok · 713s
- `without_skill`: 4/7 assertions · 40,099 tok · 30s
- judge: **with_skill** — A names the same core reframe as B but adds quantified falsifiers, cost math, and an explicit fact/assumption split; B stops at a checklist.

### eval-dental-no-shows — healthcare operations, precise  ·  **control: conventional is near-optimal**

- `with_skill`: no run recorded

- `without_skill`: no run recorded


### eval-municipal-water-loss — public infrastructure, precise

- `with_skill`: no run recorded

- `without_skill`: no run recorded


### eval-bookstore-events — small retail, casual

- `with_skill`: no run recorded

- `without_skill`: no run recorded


### eval-saas-onboarding-churn — software, precise

- `with_skill`: no run recorded

- `without_skill`: no run recorded


## benchmark.json (verbatim)

```json
{
  "run_summary": {
    "with_skill": {
      "pass_rate": {
        "mean": 1.0,
        "stddev": null
      },
      "time_seconds": {
        "mean": 713.36,
        "stddev": null
      },
      "tokens": {
        "mean": 523224,
        "stddev": null
      },
      "n": 1
    },
    "without_skill": {
      "pass_rate": {
        "mean": 0.57,
        "stddev": null
      },
      "time_seconds": {
        "mean": 29.68,
        "stddev": null
      },
      "tokens": {
        "mean": 40099,
        "stddev": null
      },
      "n": 1
    },
    "delta": {
      "pass_rate": 0.43,
      "time_seconds": 683.68,
      "tokens": 483125
    }
  },
  "deltas": {
    "deployed": {
      "mean": 0.4286,
      "n": 1,
      "per_case": {
        "eval-route-density": 0.4286
      },
      "meaning": "every case, misses and stalls included -- what an installing user experiences"
    },
    "per_activation": {
      "mean": 0.4286,
      "n": 1,
      "per_case": {
        "eval-route-density": 0.4286
      },
      "meaning": "cases where the skill fired; activated-but-failed runs included"
    },
    "excluded_from_per_activation": [],
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
