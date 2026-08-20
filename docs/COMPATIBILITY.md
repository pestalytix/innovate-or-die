# Compatibility notes

Every fact below was verified against a live source on the date shown, not
recalled — **except where the row itself says otherwise**. Three kinds of exception
exist and each is stated in place, never omitted: a check we did not run (the
`skills-ref` validator row below), a limit we accepted without a first-party
source (rows marked **WORKING BUDGET**), and a first-party source that only a
human could read because the host blocks automated fetches (the Perplexity
section). A row with none of those markings was seen with our own eyes on the
date given. Re-verify before trusting any row older than a frontier release or a
host UI change.

**Verification method matters.** Where a vendor doc and a shipped validator
disagree, the validator wins and the row says so.

---

## Agent Skills (`SKILL.md`) — agentskills.io

**Verified 2026-08-19** · source: <https://agentskills.io/specification>

| Fact | Value |
|---|---|
| Allowed frontmatter keys | `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` — **and nothing else** |
| Required | `name`, `description` |
| `name` | 1–64 chars; lowercase `a-z0-9` and `-`; no leading/trailing hyphen; no `--`; **must match parent directory name** |
| `description` | 1–1024 chars |
| `compatibility` | max 500 chars (omitted — this skill has no environment requirements) |
| `metadata` | map of string keys to **string** values |
| Frontmatter position | must start at byte 0 with `---` |
| Body budget | < 5000 tokens recommended; keep `SKILL.md` under 500 lines |
| File references | relative from skill root, one level deep |
| Reference validator | `skills-ref validate ./my-skill` (github.com/agentskills/agentskills) — not run here; conformance is asserted by `build/assemble.py` instead |

**`allowed-tools` is schema-legal but no targeted host documents enforcing it;
this skill does not declare it, because declaring an unenforced restriction would
be an untestable claim (external review #2, 2026-08-20).**

**Consequence for this repo:** `core/skill-meta.json` carries `version` and a
nested `author` map. Neither is a legal top-level `SKILL.md` key, so
`assemble.py` maps them into `metadata` as quoted strings. Our generated
values: name 15 chars, description 757 chars — both well inside the limits.

---

## claude.ai skill upload (zip)

**Verified 2026-08-20** against
<https://support.claude.com/en/articles/12512198-creating-custom-skills> and
<https://support.claude.com/en/articles/12512180-getting-started-with-skills>.

| Fact | Value |
|---|---|
| Package format | a `.zip` |
| Zip layout | **the skill folder is the zip root, not a subfolder** — quoted: *"The ZIP should contain the skill folder as its root (not a subfolder)"* |
| Illustrated structure | `my-skill.zip └── my-skill/ ├── skill.md └── resources/` |
| Folder name | must match the skill name (a mismatch is listed as a common upload error) |
| `SKILL.md` location | directly inside the skill folder, not in a subfolder |
| Upload path | **Customize → Skills → + → Create skill → Upload a skill** |
| Plan tiers | Free, Pro, Max, Team, Enterprise |
| Prerequisite | **code execution must be enabled** — Settings → Capabilities (individual), or Organization settings → Skills (Team/Enterprise owners) |

**Consequence for this repo:** the release asset
`innovate-or-die-skill-v<version>.zip` is built with `innovate-or-die/` as its
single top-level entry, so `innovate-or-die/SKILL.md` sits at depth 1 and the
folder name matches `name:` in the frontmatter. Built from the tagged tree with
`git archive`, never from the working tree. A **second** asset,
`innovate-or-die-skill-flat-v<version>.zip`, carries the identical files under
the opposite layout — see Perplexity, immediately below, for why one zip cannot
serve both hosts.

---

## Perplexity — Computer skills and Projects

Sources:
<https://www.perplexity.ai/help-center/en/articles/13914413-how-to-use-computer-skills>
(article updated 2026-08-14) and
<https://www.perplexity.ai/help-center/en/articles/10352961-what-are-spaces>
(article updated 2026-07-30).

**Read 2026-08-20 by the Claude.ai advisory session via live fetch (HTTP 200);
not machine-checked from this repo — the help center returns 403 to CI-style
fetches.** That split is the whole reason this section is marked: the figures
below were read off the live pages, but no build step, CI job, or agent working
in this repo can re-read them to confirm the pages still say so. Every value in
the two tables is therefore **quoted verbatim** rather than paraphrased, so a
future reader can diff the quote against the live article instead of trusting a
summary of it.

### Computer skill upload (zip)

Quoted verbatim from the article (updated 2026-08-14):

| Fact | Value (verbatim) |
|---|---|
| Package format and layout | *"a .zip file with a SKILL.md file at the root level, or upload a .md file directly"* |
| Max size | *"Maximum file size: 10 MB"* |
| Skill `name` — character set | *"lowercase with hyphens only"* |
| Skill `name` — length | *"between 1 and 64 characters"* |
| Upload path | **Computer → Skills → Create skill → Upload a skill** |

Note the alternative the quote offers: a bare `.md` file is also accepted. We do
not use it — it would ship `SKILL.md` with no role briefs at all — but it is the
documented fallback if the zip path ever breaks.

**This is the exact inverse of claude.ai's requirement.** claude.ai wants the
skill *folder* as the zip root; Perplexity wants `SKILL.md` itself there. No
single zip satisfies both, and a zip built for one is not degraded on the other
— it simply does not load. That is why `build/package.py` emits two assets from
the same tree rather than one, and why each is layout-asserted before it can
reach a release.

Size is not a live constraint: the skill package is ~14 KB against a 10 MB cap,
three orders of magnitude of headroom. The `name` rule is identical to
agentskills.io's, and `innovate-or-die` (15 chars) already satisfies both.

### Projects (formerly Spaces)

| Fact | Value |
|---|---|
| Instructions field | *"up to 8,000 characters"* (verbatim) |
| Renamed | Spaces → **Projects** |
| Knowledge attachment | files uploaded to the Project's **Files** |

**On the rename date.** 2026-07-30 is the date the *article* was updated, which
is what the source actually gives us. Treating it as the date of the rename is an
inference, and a reasonable one, but it is not a quoted fact — so it is written
here as the article's update date and nowhere as "renamed on". If the exact
rename date matters to something, it needs its own source.

The 8,000 figure matches the ChatGPT and M365 caps, so the existing web target
budget carries over unchanged — `perplexity-project-instructions.md` is built to
the same cap as `chatgpt-gpt-instructions.md` and currently sits **291 chars
under** it (10 more than the others: its preamble names the host).

**The cap is REPORTED, not paste-tested.** The ChatGPT 8,000 was settled by
pasting the real file into the live builder and reloading; this one has not been.
A published figure and a figure we have watched hold are different things, and
only the second one has ever caught a surprise. Until the paste test runs, this
sits in the same epistemic class as the Gemini row — a number we build to, not a
ceiling we have seen enforced.

### Subfolder survival — TESTED AND PASSED, 2026-08-20

**Method:** the verbatim quota-extraction probe, the same one that settled the
Gemini Gem on 2026-08-19 — upload the artifact, then ask the host to return the
Innovator brief's quotas *verbatim* and check them character by character. This
is the probe's second use, and reusing it is deliberate: two hosts measured the
same way are comparable, two hosts measured differently are not.

| | |
|---|---|
| Date | 2026-08-20 |
| Run by | Ken |
| Host | Perplexity **Enterprise** Computer |
| Artifact | `innovate-or-die-skill-flat-v2.1.0.zip` — the flat asset, `SKILL.md` at zip root |
| Result | **PASS.** All four Innovator top-level quotas and all four sub-quotas returned intact. `>=` symbols preserved. The relative reference path survived too |

**What this establishes:** the `roles/` and `references/` subfolders inside the
flat zip **survive the Computer import**. The failure this probe was written to
catch — a skill that loads with `SKILL.md` present and its four role briefs
silently missing — did not occur. The flat asset is a full-skill install on this
host, and the README says so without qualification.

**What it does not establish**, and neither should be read out of it:

- The host tested was **Enterprise** Computer. Whether other Perplexity tiers
  import identically is untested. One tier is not all tiers — the same caution
  the knowledge-file caveat carries for retrieval implementations.
- Content arriving intact says nothing about **how the host runs it** — and the
  execution runs below went on to demonstrate exactly that gap.

### Two full runs — 2026-08-20 — banner 2/2, and the demotion to Level 3

Both open questions from the import probe are now answered. One passed; the
other failed, and the failure is the one that decides the fidelity level.

**Setup.** Two complete end-to-end runs, same prompt — the windshield-time
example from the README — on Perplexity **Enterprise** Computer with the flat
zip v2.1.0 installed. Run by Ken. The variable was the orchestrator model,
which Perplexity lets the user select:

| | run 1 | run 2 |
|---|---|---|
| Orchestrator model | **pinned, GLM 5.2** | **default** (multi-model) |
| Activation banner | **PRESENT** | **PRESENT** |
| Stage 6 structure | full | full |
| Stage 0 assumptions declared up front | — | **yes** ([ADR-002](ADR-002-stage0-single-turn.md) behaviour) |
| Explicit regulatory deferrals | — | **two** |

"Full Stage 6 structure" means all of it, checked item by item: thesis,
reframing, three opportunities each with a mechanism and a failure mode, the
contrarian hypothesis, an experiment carrying **numeric** pass/fail thresholds,
a kill list, and residuals.

**Activation: 2 of 2. Method: `heuristic` (banner).** A count, not a rate — n=2.
Per this project's standing rule, the method is stated rather than implied:
Perplexity exposes no tool-call stream, so as on Codex the banner is an
output-side inference with **no independent ground truth to check it against**.
Only Claude's observed `Skill` call provides that. What 2/2 does establish is
that emission survives a **change of orchestrator model**, which is a
configuration axis no other host in this file exposes at all.

**Sub-agent dispatch: `observed-single`.** Ken watched both runs. Computer's
normal multi-agent activity display — the one it shows for ordinary Computer
tasks — **did not appear on either run**. Method: visual, against the observer's
own baseline of what this host looks like when it does dispatch sub-agents.

State the limit of that method plainly: **absence of a UI display is weaker
evidence than a positive observation.** It is consistent with a host that
dispatched sub-agents without rendering them. But the claim being tested is
Level 1 — *the roles run in genuinely separate contexts* — and that claim needs
positive evidence, which does not exist here. Two observed runs with no dispatch
indication is more than enough to withhold it.

**Isolation: none.** One context, the same as ChatGPT GPTs, Gems and M365
Agent Builder.

### Level: 3 — demoted from Level 1 candidate

Perplexity Computer is **Level 3**, and the CANDIDATE label is withdrawn from
the README, this file, the session state and the CHANGELOG.

The import probe passing was never evidence about execution, and this is the
measurement that made the distinction concrete: the files arrive perfectly, the
skill runs perfectly, and the roles still share one context. Level 1 would
require Perplexity to dispatch the skill's stages as separate sub-agents. **It
did not, on two observed runs.**

**What would reverse this**, stated so the bar cannot drift: dispatch observed
as `observed-separate` — positively, not by absence of a display — *and* the
critic's inputs readable, so that separation can be checked rather than assumed.
Anything less leaves it at Level 3.

### Perplexity-specific behaviours

Three things this host does that no other host in this file does. Each changes
how its output must be read, and (a) and (b) change how it must be *evaluated*.

**(a) Web search runs inside the skill.** Run 2 cited external sources for a
load-bearing industry figure, mid-protocol. No other supported host does this:
everywhere else the protocol runs on whatever the model already knows plus what
the user pasted.

> **Consequence for evals: Perplexity is its own tier and must never be blended
> with the others.** A with/without delta measured here is not like-for-like with
> the same delta on ChatGPT, a Gem or M365 — the arms differ by live retrieval as
> well as by the protocol, so the number would attribute to the skill an effect
> that partly belongs to web access. This is the same discipline as standing rule
> 5 on protocol versions, applied to a host capability instead of a version.

For users this is mostly upside — it is the one Level 3 host that can check a
figure instead of flagging it — but the "it doesn't know your prices or your
local rules" caveat still holds: retrieved is not verified.

**(b) Account memory leaks into fresh sessions.** Run 2 referenced **four facts**
about the user's other projects and location that appeared nowhere in the prompt.

> **Consequence for evals: use an account with no history, or memory disabled.**
> Otherwise runs are contaminated by whatever the account already knows, arms are
> not comparable, and the results are unreproducible by anyone else — the same
> failure class as the contamination assertion already guarded in the harness.

For users: the skill will draw on what Perplexity already knows about them. That
is often helpful and occasionally surprising, and it is worth knowing before
using it on anything sensitive.

**(c) The orchestrator model is user-selectable.** Activation held across two
configurations (pinned GLM 5.2, and the multi-model default). No other host in
this file exposes this axis. **Record the resolved model per run wherever the UI
exposes it** — the project's rule that a run records its *resolved* model, not
its requested one, applies here as much as to `claude -p`, and a multi-model
default is precisely the case where "which model actually answered" is not
knowable from the request.

---

## Claude Code plugin + marketplace

**Verified 2026-08-19** · sources: `claude plugin validate` from Claude Code
**2.1.218** (authoritative), the official marketplace manifest on disk at
`~/.claude/plugins/marketplaces/claude-plugins-official/`, and
<https://code.claude.com/docs/en/plugins-reference> (docs page — **partly wrong**, see below).

| Fact | Value |
|---|---|
| Plugin manifest path | `.claude-plugin/plugin.json` |
| Marketplace manifest path | `.claude-plugin/marketplace.json` |
| `plugin.json` required | `name` only |
| `skills` field | **adds to** the default `skills/` dir (does not replace it) |
| `author` | string, or `{name, email?, url?}` |
| Marketplace **`owner`** | **REQUIRED**, and must be an object |
| Marketplace `plugins[].source` | a **relative-path string** (e.g. `"."`) or an object whose own `source` field names the type (`url`, `git-subdir`, …) |
| `sourceDetails` | **does not exist** — the validator reports it as an unknown field |
| Validation status | `claude plugin validate .` and `--strict` both pass for plugin **and** marketplace |

> **The published docs page is wrong on two counts.** It omits the required
> `owner` field entirely and documents `source` as a type string paired with a
> `sourceDetails` object. Building to the docs produced two hard validation
> errors and two unknown-field warnings. The shipped validator plus the
> official marketplace manifest are the real schema. This is exactly the failure
> this project's rule — verify manifest schemas against current docs and the
> shipping validator, never from memory — guards against
> — and it turns out the vendor's own docs need the same distrust.

---

## Codex plugin

**Verified 2026-08-19** · source: OpenAI Codex plugin documentation and the
`plugin-creator` sample skill in `openai/codex`

| Fact | Value |
|---|---|
| Manifest path | `.codex-plugin/plugin.json` — required, and the **only** file that belongs inside `.codex-plugin/` |
| `name` | kebab-case: lowercase letters, numbers, hyphens |
| `skills` | points at a `skills/` directory; each skill is its own folder containing `SKILL.md` |
| Everything else | lives at the plugin root, not under `.codex-plugin/` |

No official JSON-schema validator was found for this manifest. The `interface`
block is carried forward from the v1 manifest unchanged.

---

## Repo-level skill discovery paths

**Verified 2026-08-19** · source: GitHub Docs, *Adding agent skills for GitHub
Copilot*

All three of `.github/skills/`, `.claude/skills/`, and `.agents/skills/` are
valid repository-level skill discovery directories, each skill in its own
subdirectory. This confirms the repo's target layout: the generated copies
under `.agents/skills/` and `.github/skills/` are discovered natively.

---

## VS Code / Visual Studio custom agents (`.agent.md`)

**Verified 2026-08-19** · source:
<https://code.visualstudio.com/docs/agent-customization/custom-agents>

| Fact | Value |
|---|---|
| Extension | `.agent.md` |
| Workspace locations | `.github/agents/` (default), `.claude/agents/`, or paths set via `chat.agentFilesLocations` |
| User profile location | `~/.copilot/agents` |
| Frontmatter keys | `description`, `name`, `argument-hint`, `tools`, `agents`, `model`, `user-invocable`, `disable-model-invocation`, `target`, `mcp-servers`, `handoffs`, `hooks` |
| Required keys | **none** — `name` defaults to the filename |
| `handoffs` entry | `{label, agent, prompt, send?, model?}` |
| Body | Markdown; `#tool:<name>` references tools |

We emit only `name` and `description`. `tools`, `model`, and `handoffs` are
deliberately omitted: the core protocol is model-agnostic (ADR-001 D8), and
pinning a model or tool set in a generated adapter would violate that.
`handoffs` is a candidate for a future revision — it could automate the
fresh-chat-per-role sequence the orchestrator currently instructs by hand.

---

## skills.sh (Vercel Labs registry)

**Verified 2026-08-20** against <https://skills.sh>, <https://skills.sh/docs>,
and <https://github.com/vercel-labs/skills>.

| Fact | Value |
|---|---|
| Submission mechanism | **none published.** No submit/publish/registry flow is documented on the site, in `/docs`, or in the repo README |
| How skills are listed | telemetry-based ranking; a skill enters the directory by being **installed**, not submitted |
| Install command | `npx skills add <owner/repo>` |
| Discovery in the target repo | root, `skills/`, or agent dirs (`.claude/skills/`, `.agents/skills/`); bounded depth-3 catalog walk covering `skills/<name>/SKILL.md` |
| Requirement | valid `SKILL.md` frontmatter with `name` and `description` |

**Consequence for this repo:** nothing to submit. `skills/innovate-or-die/SKILL.md`
already matches the depth-3 walk and carries both required frontmatter keys, so
`npx skills add pestalytix/innovate-or-die` resolves. Closed as an open item.

---

## Flattened web targets — instruction character budgets

> **Headroom (updated 2026-08-20, core v2.1.0).** Three of the four
> `*-instructions.md` files compose to **7,699 of the verified 8,000-char cap —
> 301 characters spare.** The fourth, `perplexity-project-instructions.md`, is
> **7,709 — 291 spare**: its preamble names its host outright rather than saying
> "this host", which costs 10 characters. Both are above the 200-char slack
> target `build/assemble.py` warns below, so the build is quiet again. It was 33
> characters before ADR-004: the activation banner cost 128 and was paid for by a
> 396-char dedup of the web preamble against the workflow it duplicated.
>
> **The rule has not relaxed.** Growth in `core/principles.md` or
> `core/workflow.md` still needs a compensating trim in the same commit once the
> slack is gone, or `--check` fails and nothing ships. Two worked examples now
> exist: ADR-003 (+202, paid from `principles.md` duplication) and ADR-004 (+128,
> paid from the web preamble). What remains in reserve is measured: the workflow's
> **Independence** section is a further 178 characters of duplication, deliberately
> not spent. This is a real constraint on protocol changes, not a formatting note.


**Verified 2026-08-19**

| Target | Limit | Confidence | Source |
|---|---|---|---|
| M365 Copilot Agent Builder — Instructions | **8,000** | **Verified** | Microsoft Learn, *Build agents with Agent Builder*, doc dated 2026-05-26. Same table: Name 30 chars, Description 1,000 chars |
| ChatGPT Custom GPT — Instructions | **8,000** | **Verified** | **Paste test by the author, 2026-08-19.** 8,000-char limit shown in the GPT builder UI; the 7,874-char instructions file was accepted |
| Gemini Gem — Instructions | **≥ ~7.9k, exact cap unknown** | **Working budget** | **Paste test by the author, 2026-08-19.** The Gem accepted the full instructions file (7,874 chars), so the cap is at least that. Google publishes no limit and the UI shows none; upper bound untested. Build keeps 8,000 as the working budget |
| Perplexity Projects — Project instructions | **8,000** | **Reported** | *"up to 8,000 characters"*, quoted from the Perplexity help center article (updated 2026-07-30). Read 2026-08-20 by the Claude.ai advisory session via live fetch; not machine-checkable from this repo, and not paste-tested — see the Perplexity section above |
| ChatGPT custom instructions (not GPTs) | 5,000 paid / 1,500 free | Verified, secondary | Raised from 1,500 on 2026-07-15. Not used by this project — recorded to prevent confusion with the Custom GPT field |

**Method note.** The two previously-unverified caps were settled by paste test
rather than documentation: paste the real generated file into the live builder,
save, reload, and confirm what survived. Both accepted the 7,874-char file. The
ChatGPT figure is a *hard cap* stated by the UI; the Gemini figure is a *lower
bound* only — we know our file fits, not where the ceiling is.

**Resolved 2026-08-19.** Both caps were open blockers for Phase E; both are now
settled by paste test (above). The only residual unknown is the Gemini *upper*
bound, which does not block anything while the file fits.

### Loader / knowledge split — fidelity caveat

Web targets emit three files per target: `-instructions.md` (preamble +
principles + workflow, sized to fit the cap), `-knowledge.md` (role briefs,
lens bank, experiment spec, uploaded as an attachment/knowledge source), and
`-fallback.md` (everything inlined, knowingly over budget, for hosts that take
no attachment).

**Retrieval verified on one host.** Knowledge-file retrieval was live-tested on a
**Gemini Gem, 2026-08-19**, method: verbatim quota-extraction probe — the model was
asked to return the Innovator section's quotas verbatim. **All four top-level quotas
and all four sub-quotas returned intact and exact, including `>=` symbols, with no
fragmentation of enumerated lines.** That is the specific failure this caveat was
written to anticipate, and it did not occur on that host.

**One host is not all hosts.** ChatGPT Custom GPTs and M365 Agent Builder remain
untested; each uses a different retrieval implementation. The caveat below stands for
untested hosts and is now evidence-backed rather than hypothetical for Gemini.

**Knowledge-file access is retrieval-mediated on some hosts.** A knowledge or
file-search attachment is not guaranteed to be loaded verbatim into context the
way an instructions field is: the host may chunk it, embed it, and return only
the passages its retriever judges relevant to the current turn. Consequences for
this protocol:

- A role brief may arrive **partially** — the quota lines (30 candidates, 10
  assumptions, 8 lenses) are exactly the kind of terse enumerated text that
  retrieval fragments.
- The instructions file therefore names each role and its stage explicitly, so
  the model asks for the right section rather than relying on the retriever to
  volunteer it.
- Where a host offers both, prefer pasting `-fallback.md` in full over relying
  on retrieval, accepting the over-budget truncation risk instead. Which failure
  is worse is host-specific and untested — this is a known open question, not a
  settled recommendation.

**Low-priority build item (logged, not scheduled):** the knowledge file carries
repo-relative reference paths (e.g. `../references/lenses.md`) inherited from `core/`.
These are meaningless on web hosts, where there is no filesystem — cosmetic only, since
the referenced content is inlined in the same file, but the build could strip or rewrite
them for web targets.

The three-rung fidelity ladder in the README should state this: agentic hosts
with real subagent isolation are rung one; Copilot `.agent.md` profiles with
manual fresh-chat-per-role are rung two; flattened web variants — retrieval
caveat and all — are rung three.

---

---

## `claude -p` metering — many-small-calls workloads

**Measured 2026-08-19.** A single cold `claude -p` invocation carries ~85,000 tokens
of `cacheCreation` — Claude Code caching its own system prompt and tool definitions,
charged per invocation and near-independent of payload size. For a grading call whose
actual payload was ~2,000 tokens, that was **85,071 of 88,424 total tokens (96%)**.

**Run small calls serially and back-to-back.** Consecutive calls land inside the
prompt-cache TTL and hit `cacheRead` instead of re-creating the cache:

| | cold call | serial batch (27 calls) |
|---|---|---|
| cost per call | $0.5201 | **$0.0846** (6.1x cheaper) |
| tokens per call | 88,424 | **42,549** (2.1x fewer) |
| cached share of tokens | 96.2% | 95.9% |

Batching changes *which* cache field is charged, not the ratio: ~96% of the token sum
is scaffolding either way. **Budget many-small-calls workloads on `total_cost_usd`,
not on summed token counts** — the token sum will overstate them by more than an order
of magnitude relative to real work. Observed judge batch: 90.3% cached over 4 calls.

Caveat: neither figure is a verified proxy for subscription (Max/Pro) weekly quota
weighting. That mapping is unmeasured.

## Distribution identity vs authorship

**Decided at Gate C, 2026-08-19.** Distribution identity (GitHub org, marketplace
id, install path) tracks PESTalytix, which hosts the repo; authorship (LICENSE,
all author fields) is Ken Pendergast personally. Deliberate split — do not
reconcile in either direction.

Practical consequence: `marketplace.json` keeps `"name": "pestalytix"`, so
`/plugin marketplace add pestalytix/innovate-or-die` is the stable install path
and must not be renamed once published.

---

## Consumer (non-M365) Microsoft Copilot

**Checked 2026-08-19 — result: inconclusive.** Handoff open item 3.

A consumer-facing Agent Builder rollout reportedly began in late April 2026, and
Microsoft has announced it is merging the consumer Copilot app with Microsoft 365
Copilot into a single app during 2026. But Microsoft's own Agent Builder
documentation still scopes the feature to users with a Microsoft 365 Copilot
license or a tenant with Copilot Studio pay-as-you-go enabled, and the consumer
Microsoft 365 Premium tier does not enumerate Agent Builder among its features.
There are also live reports of the builder not appearing for subscribers who
expect it.

**Disposition: the README continues to claim only the M365 Agent Builder path.**
Claiming consumer support on this evidence would be a guess presented as a fact,
and the merge in progress means any answer today has a short shelf life. Re-check
after the app unification completes; the fix if it works is a README row, not a
code change — the same generated files would be pasted either way.
