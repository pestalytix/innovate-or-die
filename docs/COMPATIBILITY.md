# Compatibility notes

Every fact below was verified against a live source on the date shown, not
recalled. Re-verify before trusting any row older than a frontier release or a
host UI change (see the maintenance policy in the handoff).

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

**Consequence for this repo:** `core/skill-meta.yaml` carries `version` and a
nested `author` map. Neither is a legal top-level `SKILL.md` key, so
`assemble.py` maps them into `metadata` as quoted strings. Our generated
values: name 15 chars, description 757 chars — both well inside the limits.

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
> the handoff's "do not trust manifest schemas from memory" rule guards against
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
subdirectory. This confirms the handoff's target layout: the generated copies
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

## Flattened web targets — instruction character budgets

**Verified 2026-08-19**

| Target | Limit | Confidence | Source |
|---|---|---|---|
| M365 Copilot Agent Builder — Instructions | **8,000** | **Verified** | Microsoft Learn, *Build agents with Agent Builder*, doc dated 2026-05-26. Same table: Name 30 chars, Description 1,000 chars |
| ChatGPT Custom GPT — Instructions | **8,000** | **Verified** | **Paste test, Ken, 2026-08-19.** 8,000-char limit shown in the GPT builder UI; the 7,874-char instructions file was accepted |
| Gemini Gem — Instructions | **≥ ~7.9k, exact cap unknown** | **Working budget** | **Paste test, Ken, 2026-08-19.** The Gem accepted the full instructions file (7,874 chars), so the cap is at least that. Google publishes no limit and the UI shows none; upper bound untested. Build keeps 8,000 as the working budget |
| ChatGPT custom instructions (not GPTs) | 5,000 paid / 1,500 free | Verified, secondary | Raised from 1,500 on 2026-07-15. Not used by this project — recorded to prevent confusion with the Custom GPT field |

**Method note.** The two previously-unverified caps were settled by paste test
rather than documentation: paste the real generated file into the live builder,
save, reload, and confirm what survived. Both accepted the 7,874-char file. The
ChatGPT figure is a *hard cap* stated by the UI; the Gemini figure is a *lower
bound* only — we know our file fits, not where the ceiling is.

**Headroom warning.** At 7,874 chars the instructions file sits **126 chars** under
the 8,000 budget. The v2.0.1 patch alone consumed 305 chars of the previous 431.
Any further addition to `core/principles.md` or `core/workflow.md` will breach the
ChatGPT hard cap and hard-fail `build/assemble.py --check`.

**Resolved 2026-08-19.** Both caps were open blockers for Phase E; both are now
settled by paste test (above). The only residual unknown is the Gemini *upper*
bound, which does not block anything while the file fits.

### Loader / knowledge split — fidelity caveat

Web targets emit three files per target: `-instructions.md` (preamble +
principles + workflow, sized to fit the cap), `-knowledge.md` (role briefs,
lens bank, experiment spec, uploaded as an attachment/knowledge source), and
`-fallback.md` (everything inlined, knowingly over budget, for hosts that take
no attachment).

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
