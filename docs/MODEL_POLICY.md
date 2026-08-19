# MODEL_POLICY

Which models the evals pin, and why. Referenced by Phase D of the handoff.

**Status:** established 2026-08-19. Supersedes nothing — the handoff referenced a
`MODEL_POLICY` that had never been written; this is it.

## Two tiers, workhorse primary

| Tier | Purpose | Claude leg | Codex leg |
|---|---|---|---|
| **1 — Workhorse** | **Primary. The headline numbers.** | `claude-sonnet-5` | `gpt-5.6-terra` |
| **2 — Flagship** | Frontier tracking, maintenance loop | `claude-opus-5` | `gpt-5.6-sol` |

**Rationale.** Free and default-tier users never see frontier models. The
with/without delta *on the tier the skill's actual audience runs* is the
decision-relevant claim; the flagship number is frontier tracking, rerun on
frontier releases per the maintenance policy.

### Codex tier note — the default IS the flagship

OpenAI's Codex lineup is Sol ("detail and polish"), **Terra ("the everyday
workhorse")**, and Luna ("clear, repeatable work"). Verified 2026-08-19:
`codex exec` with no `-m` resolves to **`gpt-5.6-sol`** — i.e. the Codex default
is the flagship tier, unlike Claude Code, where an unpinned `claude -p` was
observed resolving to `claude-haiku-4-5-20251001`.

Consequence: Codex users get the flagship by default and Claude users may not.
Both tiers are still run on both providers, but the asymmetry belongs in any
cross-provider comparison. Both strings were smoke-tested against the live CLIs
before adoption.

## Rules

1. **Full model strings only.** No bare aliases in commands or results.
2. **Record the RESOLVED id per run**, never the requested alias. It goes in
   every `timing.json` (`requested_model` and `resolved_model` as separate
   fields) and in the results filename.
3. **A requested-vs-resolved mismatch is a run failure**, not a footnote. The
   runner flags `model_mismatch` and the run is excluded from headline numbers.
4. Claude Code reports several models per run in `modelUsage` — the pinned model
   plus utility calls (observed: `claude-haiku-4-5-20251001` alongside the pinned
   model on a trivial prompt). The runner resolves by matching the requested
   family first and only falls back to highest-output-token model, recording
   `all_models` either way.

## Baseline scope

5 cases x 2 arms x 2 tiers x 2 providers = **40 runs** per full baseline.
`benchmark.json` and results files report per tier; the results narrative leads
with the workhorse delta and reports flagship alongside.

## Quota-compliance finding rule

If a workhorse-tier model fails the protocol's quotas in the `with_skill` arm
(fewer than 30 candidates, missing sub-quotas, no falsifiers), **that is a
finding, not a harness bug.** Record it verbatim and document a
minimum-capable-model statement. Do not tune the protocol mid-baseline —
protocol changes are a new ADR and a semver bump.

## Gemini

Not yet runnable: the Gemini CLI is not installed on the build machine
(handoff open item 2, still open as of 2026-08-19). Tiers to be added here when
it is available.
