# MODEL_POLICY

Which models the evals pin, and why.

**Status:** established 2026-08-19.

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
4. **Harness validity and product outcome are different exclusions.** A run is
   *harness-invalid* when the number does not measure what it claims to —
   `model_mismatch`, a `TIMEOUT`/`UNKNOWN` resolution, a parse failure, or a null
   grade. Those are dropped from every figure, and `aggregate.py` names each
   dropped pair with its reason. A **non-activation is not harness-invalid**: it
   is a real, correctly measured deployed outcome, and dropping it would delete
   the activation-reliability finding instead of reporting it. It is included in
   the `deployed` delta and excluded only from `per_activation`. Rule of thumb:
   *did the instrument fail, or did the product?* Only the first is an exclusion.
5. **Deltas are computed over matched valid pairs only.** Both arms of a case
   must be present and harness-valid, or the case is dropped from both arms.
   Per-arm means over different case sets are not comparable and must never be
   subtracted. (Introduced 2026-08-20 after external review finding 5, which
   caught exactly that on the iteration-1 Claude workhorse tier.)
6. Claude Code reports several models per run in `modelUsage` — the pinned model
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

**CLI installed 2026-08-19** (`gemini` 0.56.0). Headless mode is `-p/--prompt`;
`-o/--output-format` accepts `text`, `json`, `stream-json`; model is `-m/--model`.

**BLOCKED ON AUTH.** The CLI is present but unauthenticated — no
`~/.gemini/settings.json`, and none of `GEMINI_API_KEY`,
`GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_GENAI_USE_GCA` are set. A run returns:

> Please set an Auth method in your `~/.gemini/settings.json` or specify one of
> the following environment variables before running: `GEMINI_API_KEY`,
> `GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_GENAI_USE_GCA`

There is no non-interactive login subcommand. Auth requires either an interactive
`gemini` session completing OAuth (the Google Code Assist path, which is how a
Gemini subscription authenticates) or an API key in the environment. Both are the
author's to perform.

### Tier pins — PROVISIONAL, not yet confirmed against the live CLI

Google's lineup as of 2026-08 runs Pro (most capable) / Flash (fast, balanced) /
Flash-Lite (cheapest), with Gemini 3 current and 2.5 as the proven fallback.
Published docs did **not** give a complete list of CLI-accepted model strings, and
the CLI's own `/model` command is the authoritative source — which needs auth.

| Tier | Provisional pin | Status |
|---|---|---|
| Workhorse | Flash-tier string | **unconfirmed — must be read from `/model`** |
| Flagship | Pro-tier string (e.g. `gemini-3.1-pro-preview`) | **unconfirmed** |

Per rule 1 these are not usable pins yet: full model strings only, and a string we
have not seen the CLI accept is a guess. **Confirm both against `/model` after auth,
then record them here before any Gemini baseline run.**

---

## Reasoning effort as recorded configuration

**Verified 2026-08-19:** `claude -p` exposes `--effort <level>` with levels
**`low, medium, high, xhigh, max`**. It is a session-level control, so it applies to
a `-p` run and to the subagents that run spawns.

Effort is part of a run's configuration and is recorded in `timing.json` alongside
the resolved model. An unrecorded effort level makes two runs incomparable in
exactly the way an unrecorded model alias does.

Codex exposes a comparable notion — its banner prints `reasoning effort:` (observed
`none` on default `codex exec`). Gemini's equivalent, if any, is unknown pending auth.

---

## Claude flagship: envelope probe replaces the full tier

**Scope amendment, 2026-08-19.** The 10-run Claude flagship tier (5 cases x 2 arms
at `claude-opus-5`) is **replaced** by a single envelope probe. Rationale: the one
opus `with_skill` run attempted exceeded the 1800s timeout and produced zero bytes,
so a full tier is a large, unbounded quota commitment for a result we cannot
currently bound. The probe answers the question the tier was meant to answer — *does
the protocol complete on the flagship model, and at what cost* — for one run instead
of ten.

**Probe design:**

1. **One case, `with_skill`, `claude-opus-5`, DEFAULT effort**, `--output-format
   stream-json`, `TIMEOUT_S=5400`.
   Default effort is deliberate: it is the **Max-plan deployed condition**, so a
   result there carries the upward-compatibility claim. A probe run at a
   hand-tuned effort would not.
2. **If it completes:** record duration, tokens, turns, subagent count, and
   activation. That is the flagship envelope.
3. **If it times out:** one re-run at `--effort medium` as the documented
   mitigation. **The pair is the finding** — "the flagship model does not complete
   this protocol at default effort within 90 minutes, and requires reduced effort"
   is a materially different claim from a simple timeout, and it is directly
   actionable for users.
4. **Either way**, the effort level is recorded in `timing.json` as configuration,
   not inferred afterwards.

Gate: this probe runs only on explicit operator go-ahead alongside the Claude lane
restart. It does not run automatically.
