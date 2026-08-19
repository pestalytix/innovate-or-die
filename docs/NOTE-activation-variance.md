# Note — cross-host skill activation variance

**Opened 2026-08-19** from iteration-1 evals. Not a protocol matter (ADR-002 scope
decision); tracked here as its own workstream.

## Observation

On **identical** prompts, whether the skill activates differs by host:

| Case (v1 prompt) | claude-sonnet-5 | gpt-5.6-terra |
|---|---|---|
| `eval-dental-no-shows` | **did not activate** | activated |
| `eval-route-density` | activated | activated, stalled at Stage 0 |

The Claude miss is stark: 40,923 tok / 36 s with zero protocol markers, versus
41,386 tok / 43 s for its own control — statistically indistinguishable, i.e. the
`with_skill` arm ran as a second baseline.

## Competing hypotheses — none settled

1. **Exclusion-clause match.** The v1 prompt opened "Evaluate what would most reduce…",
   which reads as decision analysis — precisely what the `description` field instructs
   agents to decline. On this reading the skill behaved *correctly*.
2. **Probabilistic activation miss.** Description matching is a model judgement, not a
   deterministic rule. Codex activated on the same wording, which hypothesis 1 alone
   does not explain.
3. **Differing dispatch implementations.** Claude Code surfaces an explicit `Skill`
   tool call; Codex has no equivalent observable. The hosts may apply different
   thresholds or matching strategies entirely.

Hypothesis 2 and 3 are not distinguishable from one run each. **Do not present the
exclusion clause as the settled mechanism.**

## Why this matters more than it looks

A non-activated `with_skill` run is invisible without instrumentation — it looks like
the skill performing poorly. In iteration-1 that distinction moved the reported
Codex workhorse delta by **2.7×** before other corrections. Any future eval must
record activation per run, and any activation claim must state its method:
`observed` (tool call seen), `heuristic` (output markers), or `inferred` (backfilled).

## Workstream: description-field optimization

The `description` in `core/skill-meta.yaml` is the sole activation lever and is
currently unoptimized — written once, never tested. Candidate work:

- Build an **activation-only eval**: many short prompts, measure activation rate
  alone, no full protocol run. Cheap, since activation is decided before the
  expensive work starts.
- Test whether the `Do NOT use…` exclusion clause suppresses legitimate activations
  as well as illegitimate ones — the dental case suggests it may be over-broad.
- Measure activation across hosts separately; a description tuned on one host's
  dispatcher may not transfer.
- Watch for the opposite failure: a description broad enough to fire on decision
  analysis or delivery work, which the exclusion clause exists to prevent.

Any change here is a `skill-meta` change regenerating every adapter, so it needs its
own ADR and a version bump.
