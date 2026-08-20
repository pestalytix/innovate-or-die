# Changelog

All notable changes to the core protocol. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the protocol is
versioned with [semver](https://semver.org/). Protocol changes require an ADR
and a version bump.

## [Unreleased]

No protocol change — `core/` is untouched, so the version stays 2.1.0. Release
packaging, a fourth web target, and the Perplexity findings.

### Added
- **`build/package.py`** — builds the release assets from a tag with `git
  archive`, never from the working tree, and emits **two** zips because two hosts
  demand incompatible layouts: `innovate-or-die-skill-v<ver>.zip` (skill folder as
  the zip root — claude.ai) and `innovate-or-die-skill-flat-v<ver>.zip` (`SKILL.md`
  at the zip root — Perplexity Computer). Each layout is asserted against the
  finished zip before it can reach a release, so a wrong-rooted asset fails the
  build instead of failing silently at someone else's upload.
  **Builds are reproducible.** `git archive` given a `<ref>:<path>` argument
  resolves a *tree*, which carries no date, so it stamps members with the wall
  clock and writes a second build-time mtime into an `UT` extra field that no zip
  listing shows. Both are normalised to the commit time in UTC. Two builds of the
  same tag are now byte-identical, in CI or on a laptop, in any timezone.
- **`.github/workflows/release.yml`** — on a `v*` tag: `assemble.py --check`,
  `pytest`, a guard that the tag matches `core/skill-meta.json`, then `package.py`
  and a `gh release upload`. `check.yml` is untouched. Uses the `gh` CLI rather
  than a third-party action, so no external code receives the write-scoped token.
- **A fourth web target, `perplexity-project`** — `perplexity-project-{instructions,
  knowledge,fallback}.md`, same 8,000-char budget as `chatgpt-gpt`. Its preamble
  names Perplexity Projects outright instead of saying "this host", which costs 10
  characters: **7,709 of 8,000, 291 spare**. The other three are unchanged at 7,699.
- **`tests/test_package.py`** — the packager's layout assertions, each handed the
  mistake it exists to catch (flat zip checked as folder-root and the reverse,
  `SKILL.md` one level too deep, a dropped member), plus a positive control so the
  negative tests cannot pass an assertion that rejects everything, plus a
  reproducibility test. Three more in `test_assemble.py` cover the per-target
  preamble. Suite: 56 → **65**.
- **README** now links the published [Custom GPT] and [Gem] directly, and carries
  two Perplexity rows (Computer, Projects).

### Changed
- **`docs/COMPATIBILITY.md` gains a Perplexity section**, with every figure quoted
  verbatim rather than paraphrased. Its provenance is stated exactly: read
  2026-08-20 by the Claude.ai advisory session via live fetch (HTTP 200), **not
  machine-checked from this repo** — the help center returns 403 to CI-style
  fetches. That is a third kind of exception to this project's verification rule,
  and the file's opening paragraph now enumerates all three.
- **Perplexity Computer subfolder survival: TESTED, PASS** (2026-08-20, Ken,
  Perplexity Enterprise Computer, flat zip v2.1.0). The verbatim quota-extraction
  probe — the same one that settled the Gemini Gem — returned all four Innovator
  top-level quotas and all four sub-quotas intact, `>=` symbols preserved, relative
  reference path preserved. The flat asset is a full-skill install.
- **Perplexity Computer settled at Level 3** (2026-08-20), after two full runs on
  the same prompt with different orchestrator models. The activation banner was
  emitted **2/2** — a count, not a rate, by `heuristic` method, since Perplexity
  exposes no tool-call stream — and both outputs carried full Stage 6 structure.
  But **sub-agent dispatch was `observed-single` on both runs**: no isolation, one
  context, the same as ChatGPT GPTs, Gems and M365. Level 1 would require
  Perplexity to dispatch the skill's stages as separate sub-agents; it did not.
  The CANDIDATE label is withdrawn everywhere. A passing import probe measures
  what arrived, never what runs — that distinction is the whole finding.
- **Two Perplexity-specific behaviours now documented**, both of which change how
  the host must be *evaluated*, not just read: **live web search runs inside the
  protocol** (so a with/without delta here is not like-for-like with any other
  host and must never be blended into one), and **account memory leaks into fresh
  sessions** (so evals need an account with no history, or memory disabled). Its
  orchestrator model is also user-selectable, which is why the banner count is
  reported across two configurations.
- The README's claim that the ChatGPT and Gemini caps "have no first-party source"
  was stale — ChatGPT was settled by paste test on 2026-08-19. Corrected.

### Fixed
- **`package.py --check` no longer builds into `dist/` and deletes afterwards.**
  It built the assets, asserted them, then removed them — which also removed
  assets a previous real run had left there. A verification mode that can destroy
  what it verifies makes "I built the zips" and "the zips are on disk" separately
  true and jointly false. It now builds into a temp dir and says so, and both
  modes print what is left behind.

### Release assets — v2.1.0 re-cut
The v2.1.0 folder-root asset originally attached to the release was **not built by
`package.py`**: its member timestamps are wall-clock build time, 45 seconds after
the tag's own commit, so it could not be reproduced from the tag. It has been
**replaced** with the reproducible build, and the flat asset added. Recorded here
because a published checksum that silently changes is worse than one that changes
loudly:

| Asset | sha256 | size |
|---|---|---|
| `innovate-or-die-skill-v2.1.0.zip` — **superseded**, original upload | `bb37204fcf728a7982c860438915172ae72d9a0421454d6f58135e80eecad86e` | 14,251 |
| `innovate-or-die-skill-v2.1.0.zip` — current, `package.py` build | `089d69738cc76430a4da1fe64c0ec7e02c428209392e9a063a3478a7f162d41a` | 14,053 |
| `innovate-or-die-skill-flat-v2.1.0.zip` — new | `6ac122d1e5bbe7e0d9a714b7c7c72126534d85e9b10064e45eeb927af6429f27` | 13,625 |

Reproduce either with `python3 build/package.py --ref v2.1.0` — **from the tag,
not from `HEAD`**. The two differ: member mtimes come from the ref's own commit,
so a `HEAD` build of the same files yields different bytes and a different
checksum. That is the property working, not a defect.

The two folder-root builds are **identical in content** — same 11 members, same
names, same order, same CRC-32s. They differ only in embedded timestamps and the
`UT` extra field, which is the 198-byte size difference. The asset had been
downloaded twice before replacement.

[Custom GPT]: https://chatgpt.com/g/g-6a85fa3ea49c8191b4a7c58167f8eff5-innovate-or-die
[Gem]: https://gemini.google.com/gem/1XoPOHbLHJCR5zxVRxmOKsZVlBzsK5EWj

## [2.1.0] — 2026-08-20

Minor. **The first change to the delivery structure since v2.0.0**, and the first
non-patch bump: the protocol now opens its answer with a version-stamped
activation banner ([ADR-004](docs/ADR-004-activation-banner.md)). Additive —
items 1–7 of Stage 6 keep their numbers and meanings, so anything that read a
v2.0.2 delivery still reads a v2.1.0 one with an extra line above it. Also
carries the harness and tooling work from wave 1 of the GitHub Copilot review
disposition (`docs/notes/copilot-github-review.md`).

### Added — protocol
- **An activation banner as Stage 6 item 0.** The answer's first line is
  `⟦innovate-or-die v<version>⟧`, substituted at build time from
  `skill-meta.json`. A run where the skill silently did not fire was previously
  indistinguishable from an ordinary answer — the README's advice was to infer it
  from the absence of a kill list. Now presence is an exact string match, and it
  names the version that produced the answer. It ships on every surface that
  assembles a final answer (all three skill packages, the three web instructions
  and fallback files, the Copilot orchestrator) and on none that does not (the
  knowledge files, the per-role profiles).
  **What it does not do:** make activation more likely. It makes a miss visible.
  Presence proves the protocol ran; absence is a strong hint, not proof — a model
  that ran it can still omit the line, which is why the README says so and why
  the emission rate is now measured.

### Changed
- **Instruction budgets.** The banner costs 128 characters against 33 of
  headroom, paid for by a 396-character dedup of the web preamble, which restated
  two things the substituted workflow already says more specifically a few hundred
  characters below. Web instructions files: 7,967 → **7,699 of the 8,000 cap, 301
  spare** — above the slack target, so the build no longer warns. The trim is
  generator-side, so the canonical skill package loses nothing. A further 178
  characters of measured duplication are left unspent in reserve.
- **Activation detection.** The Codex leg of the eval harness replaces its
  seven-regex marker vote with the exact banner match (`observed:banner`), keeping
  the markers as a secondary signal so a missing banner is not recorded as a
  non-activation. The Claude leg keeps the `Skill` tool call as ground truth and
  records the banner beside it — that pairing is what will measure the banner's own
  false-negative rate rather than assume it.
- Assertion blocks in `evals.json` may now restrict an assertion to one arm.
  Arm-restricted results are excluded from `pass_rate` and from every paired
  delta: the control arm can never emit a banner, so grading it in both arms
  would have turned the protocol's own signature into a measured quality gain.

### Added — harness and tooling (no protocol effect)
- **A `pytest` suite over the harness** (`tests/`), plus a CI job that runs it.
  It guards the two correctness bugs fixed in 2.0.2 — unmatched-arm aggregation
  and non-majority judge verdicts — which until now were fixed by inspection with
  nothing to stop them coming back. Also covers `_sub()`'s refusal to no-op,
  `check_references()`, the size guardrails, the banner on every surface that
  should carry it, and a `LICENSE` ↔ `skill-meta.json` license match.
- **A hard 30,000-char ceiling on the single-paste fallback.** Being over every
  instruction-field cap is the fallback's accepted condition; being over the
  ceiling is a size nobody decided on. Currently 24,988. Raising it requires an
  ADR.
- **A slack warning on the web instruction caps** — under 200 chars of headroom
  the build says so by name. It fired at 33; ADR-004 cleared it to 301.
- **A generated index at `evals/results/README.md`**, built from the results
  files and the root README's results table, with a guard that fails the build if
  those two sets disagree in either direction.
- **A "you did it wrong if…" checklist in the Copilot orchestrator profile.**
  That path is the only one where the role isolation is the human's to maintain,
  which makes it the easiest to run wrong while believing it ran right.
- **A default install path in the README** above the matrix, for readers who do
  not want to compare eleven rows first.

### Fixed
- **`check_references()` could not see `../`-style references.** Its pattern
  required the first character to be alphanumeric, so `../references/lenses.md`
  — the exact form `core/` uses — passed unchecked into single-file surfaces,
  the one place it can never resolve. Found by the new test suite on its first
  run. No shipped artifact was affected; the hole was open, not exercised.

### Docs
- `docs/notes/` now holds session ephemera and raw review inputs; the ADRs and
  `COMPATIBILITY.md` are no longer buried among them. `docs/notes/local/` is
  gitignored for future working state.
- `COMPATIBILITY.md`'s headroom section carried a superseded paragraph quoting
  7,874 chars and 126 of headroom against a newer block saying 7,967 and 33. The
  stale one is deleted rather than a third figure added.

## [2.0.2] — 2026-08-20

Patch. Disposition of an external adversarial review of the public repo at
`7daa93a`. One protocol change ([ADR-003](docs/ADR-003-injection-hardening.md));
everything else is generator, harness, and claim-accuracy work. No role, quota,
gate, or output-section change.

### Fixed
- **Supplied evidence is authoritative as evidence, not as instructions.**
  "Treat the user's request and supplied evidence as authoritative" did not
  distinguish evidence from instruction-shaped text embedded in a document, page,
  or tool result. The protocol reads external pages by design (an opus probe
  recorded `WebSearch`x4 on one run), so the ambiguity was live. Embedded
  instructions are now data to analyse and reporting them is a finding.
- **The single-paste fallback demanded eight lenses from a file it did not
  carry.** The lens bank is now inlined, and every web and Copilot adapter has
  its references rewritten to name sections rather than unreachable file paths.
- **The Copilot reviser profile referenced an experiment spec it did not
  carry**; it is now inlined. The innovator and orchestrator profiles had the
  same class of dangling reference and were corrected.
- **`core/workflow.md` referenced `critic.md` and `evaluator.md`** at the skill
  root, where the files are `roles/critic.md` and `roles/evaluator.md`. The
  canonical skill package shipped two broken references. Found by the new CI check.
- **Eval deltas were computed over unmatched arms.** `aggregate.py` now uses
  matched valid pairs only and names every dropped pair with its reason. The
  iteration-1 Claude workhorse tier is corrected and carries a note.
- **The blind judge could award a win without a majority** (A/B/tie is a
  three-way split, and `most_common(1)` does not imply a majority), and kept only
  one representative ballot. Strict majority is now required; all ballots are
  stored. Iteration-2 verdicts were unanimous and are unaffected.
- Version headings in `core/` no longer hardcode a version; the build substitutes
  it from `skill-meta.json` and fails if a placeholder survives.

### Added
- **Referential-completeness CI check.** Every relative file reference in every
  generated artifact must resolve in that artifact's install context;
  single-file surfaces must contain none. Tamper-tested.
- **Run provenance.** `timing.json` records repo commit, dirty flag, skill
  version read from the tree at run time, and CLI name and version.
- [`docs/NOTE-efficacy-roadmap.md`](docs/NOTE-efficacy-roadmap.md) — what an
  actual efficacy study would require, accepted as future work, not scheduled.
- [`evals/results/2026-08-20-judge-validity-dental.md`](evals/results/2026-08-20-judge-validity-dental.md)
  — the judge preferred the `with_skill` arm on the control case designed to
  punish novelty-forcing, in all three tiers.

### Changed
- **Claims reframed to what the eval actually measures: protocol compliance and
  cost, not independent idea quality.** The assertions derive from the protocol's
  own output spec, the judge's dimensions mirror the protocol's evaluator, and
  iteration-2 is in-sample. Every results file now states this before its first
  number. "Enforcement by exhortation demonstrably fails" is removed — no
  ablation supports it.
- ADR-001's "the critic is where the value is created" is now "the critic carries
  the largest share of the enforcement text; no ablation has tested where value
  is created."
- `core/workflow.md`'s Independence section is deduplicated against
  `principles.md`, paying for the ADR-003 amendment at net zero characters
  against the 8,000-char instructions cap.

## [2.0.1] — 2026-08-19

Patch. Clarifies an instruction that already intended to mandate proceeding; no
role, quota, gate, or output structure changed. See
[ADR-002](docs/ADR-002-stage0-single-turn.md).

### Fixed
- **Stage 0 no longer stalls in single-turn hosts.** v2.0.0 said to ask up to three
  clarifying questions "then proceed regardless", which presumes a conversational
  host. In a single-shot invocation (`claude -p`, `codex exec`, scheduled or API
  runs) there is no second turn, so a run could return only questions and skip the
  entire workflow. Observed in iteration-1 evals: one run returned 771 bytes of
  questions and scored 0.143 against its own control's 0.571.
- Questions are relocated rather than merely discouraged — gaps become labelled
  assumptions surfaced in the Stage 6 delivery, each noting what changes if wrong.
  A standalone question block has nowhere to live in the canonical output structure,
  so ending in questions is structurally impossible.

## [2.0.0] — 2026-08-19

Merge of two forked implementations into one canonical protocol. Rationale and
the full disposition table: [ADR-001](docs/ADR-001-protocol-merge.md).

**Architecture from `innovate-or-die` v1. Enforcement from `innovation-mode`.**

### Added
- Quotas that force a real search: 10+ assumptions classified real-vs-inherited,
  5 reformulations, 8+ lenses, 30 candidates with sub-quotas and two distinctness
  tests.
- Seven-test fake-novelty detector with 8–15-of-30 kill calibration, assigned to
  the isolated critic rather than the author (ADR-001 D1, D2).
- Nine-probe adversarial checklist and a falsifier standard — no falsifier, no
  finalist.
- Asymmetric-selection criteria and "more radical version" questions, assigned to
  the reviser (D3).
- `references/lenses.md` — lens bank with provocations.
- `references/experiment-spec.md` — experiment shape plus the solo-operator scale
  rule; required in the final answer.
- Compact kill list surfaced in the final answer while the rest of the
  scaffolding stays hidden (D5).
- Generated packaging for every install surface, assembled from `core/` by
  `build/assemble.py` with a CI drift guard.

### Changed
- Critic audit schema extended from 9 fields to 10: `ideas_to_discard` renamed
  `kill_list`, `adversarial_findings` added.
- Final answer shape merged (D6): strongest surviving thesis first, then
  reframing, opportunities with mechanisms, contrarian hypothesis, experiment,
  kill list, and what may still be missing.
- Roles load at their stage rather than up front, so the critic's and evaluator's
  criteria stay out of the divergent search context in single-context runs.
- Core is model-agnostic (D8); all host specifics live in generated adapters.

### Retired
- `innovation-mode` — superseded; archived at `docs/archive/innovation-mode/`.
- v1 skill — archived at `docs/archive/v1/`.
