# ADR-004 — Self-identifying activation banner

**Date:** 2026-08-20 · **Status:** **ACCEPTED 2026-08-20, applied in v2.1.0** ·
**Affects:** core protocol v2.0.2 → **v2.1.0**

Raised by the GitHub Copilot review of the public repo at `fc3325e`
(`docs/notes/copilot-github-review.md`, §3.1 and §6 item 1), where it is the top
recommendation. Wave 2 of that review's disposition; wave 1 shipped in `d3d27d5`.

---

## Context

### The problem this addresses

A run where the skill did not activate is **indistinguishable from an ordinary
answer**. There is no error, no warning, and no marker. The user believes they
ran an adversarial four-role search; they received whatever the base model
produces. `docs/NOTE-activation-variance.md` records the measurement: **3 of 7
`with_skill` runs activated on Claude Code** (a count, not a rate — n is far too
small for a percentage), against every run on Codex. Three hypotheses for the
mechanism have been proposed and all three are falsified.

That note's own conclusion is the reason this ADR exists: *"No protocol
improvement matters if the skill does not fire."* Nothing here makes it fire
more often. It makes **not firing visible**, which is a different and smaller
claim — see Scope.

### How "did it run?" is answered today

Three detectors, all indirect:

| Who | Method | Where |
|---|---|---|
| The eval harness, Claude | An observed `Skill` tool call in the `stream-json` event stream | `run_evals.py` — `activation_method: "observed:Skill-tool-call"` |
| The eval harness, Codex | `markers >= 2` over seven fuzzy regexes (`kill list`, `falsifi`, `contrarian`, `reframing`, `most instructive`, `still missing`, `critical assumption`) | `run_evals.py` — `activation_method: "heuristic:markers"` |
| The user | Prose in the README: if there is no list of rejected ideas and no experiment with a pass/fail number, it did not run | `README.md`, *Good to know* |

The first is ground truth, and it exists only on hosts that emit a tool-call
stream. The second is a heuristic in both directions: a strong unassisted answer
can hit two of those seven patterns without any protocol, and a run that
activated but stalled hits none.

**The user-facing heuristic is not broken, and this ADR should not claim it is.**
Measured over the committed eval workspace, **0 of 19 `without_skill` runs**
passed the kill-list, experiment-spec, or numeric-falsifier mechanical checks. As
a *negative* signal — structure absent, therefore no protocol — it has so far
been clean. What it is not: an exact anchor. It requires the reader to have read
the whole answer, to know what the protocol's output is supposed to contain, and
to make a judgement call. It carries no version. And a host, a script, or a
support request cannot evaluate it at all.

---

## Decision

Four parts. Parts 1 and 2 must land in the same commit — part 1 alone fails the
build.

### 1. The banner becomes delivery item 0

In `core/workflow.md`, Stage 6, above the existing item 1:

> Final answer structure, in order:
>
> 0. **Activation line** — open with `⟦innovate-or-die v{{CORE_VERSION}}⟧` alone
>    on the first line, so the reader can see the protocol ran.
>
> 1. **Strongest surviving thesis** — …

Four properties, each deliberate:

- **Numbered 0, not inserted as a new 1.** Items 1–7 keep their numbers, so
  every other document that refers to "Stage 6 item 3" stays correct.
- **The version is substituted at build time.** `core/` already carries
  `{{CORE_VERSION}}` and `load_core()` already replaces it from
  `skill-meta.json`, so the banner cannot drift from the version that produced
  it, and the existing "no unsubstituted placeholder ships" guard covers it.
- **One line, first position, no content to generate.** It is the cheapest
  instruction in the protocol to comply with, which matters — see the compliance
  data in Consequences.
- **`⟦ ⟧` (U+27E6/U+27E7), not `[ ]`.** The string has to be one no unassisted
  model would produce by chance and no markdown renderer will eat. Square
  brackets read as a link fragment; these do not. The ASCII alternative
  `[[innovate-or-die v2.0.2]]` costs 2 more characters, not fewer — see Open
  questions.

**Every surface that assembles a final answer carries it**, because it lives in
`core/workflow.md`, which is what those surfaces are built from:

| Surface | Carries the banner | Via |
|---|---|---|
| `skills/`, `.agents/skills/`, `.github/skills/` — `SKILL.md` | yes | workflow is the SKILL.md body |
| `adapters/web/*-instructions.md` (ChatGPT, Gemini, M365) | yes | preamble + principles + workflow |
| `adapters/web/*-fallback.md` | yes | everything inlined |
| `adapters/copilot/agents/innovate-or-die.agent.md` | yes | the orchestrator assembles Stage 6 |
| `adapters/web/*-knowledge.md` | no, correctly | role briefs only; it assembles nothing |
| `adapters/copilot/agents/innovate-or-die-<role>.agent.md` | no, correctly | single roles, no delivery |

### 2. The compensating trim

**No banner wording fits in the headroom that exists.** Measured, not estimated —
each row is a real build of `chatgpt-gpt-instructions.md` against the verified
8,000-character ChatGPT cap:

| Composition | Instructions | Headroom | Fallback |
|---|---|---|---|
| v2.0.2 as shipped | 7,967 | 33 | 24,860 |
| **+ banner, recommended wording** | 8,095 | **−95 — build fails** | 24,988 |
| + banner, shortest wording that still specifies it (`0. First line, exactly: …`) | 8,019 | **−19 — build fails** | 24,912 |
| + banner + preamble dedup (T1+T2) | **7,699** | **301** | 24,988 |
| + banner + T1+T2 + workflow Independence trim (T3) | 7,521 | 479 | 24,810 |
| + banner long in `core/`, short on web only, + T1+T2 | 7,623 | 377 | 24,988 |

Even a 52-character banner is 19 characters more than the budget has. This is the
pre-decision recorded in `docs/COMPATIBILITY.md` — *"any future growth in
`core/principles.md` or `core/workflow.md` needs a compensating trim in the same
commit"* — coming due exactly as written.

**Recommended: banner + T1+T2 → 7,699 chars, 301 of headroom.** That clears the
200-character slack target added in wave 1, so the build stops warning. T3 is
held in reserve rather than spent.

**T1 and T2 are in `build/assemble.py`'s `PREAMBLE_SPLIT`, not in `core/`.** The
web preamble opens by saying what the workflow says again a few hundred
characters later, because the preamble was written before the per-surface
substitution tables existed:

| The web preamble says | The substituted workflow already says |
|---|---|
| "The four role briefs, the lens bank, and the experiment spec live in the **attached knowledge file**. Read each role's section at its stage, not before." | "The role briefs, lens bank, and experiment spec are in the **attached knowledge file** — read each at its stage, not before: **Innovator** (with the **Lens bank**) at Stage 1; **Critic** at Stage 2; **Reviser** at Stage 3; **Evaluator** at Stage 4; the **Experiment spec** when assembling the final answer." |
| "**This ordering is load-bearing.** Do not read the Critic or Evaluator sections until your Innovator pass is complete. Their criteria in context during the divergent search recreates the self-censoring that role separation exists to prevent." | "When running without subagent isolation, this ordering is load-bearing: do not read the **Critic** or **Evaluator** briefs before Stage 1 is complete — their criteria in context during the divergent search recreates the self-censoring the role separation exists to prevent." |

In both rows the workflow's version is the more specific one — it names each
role and its stage. The one sentence the preamble carries alone, *"Announce each
pass as you begin it,"* is kept.

**Two consequences worth stating plainly.** First, because the trim is
generator-side, **the canonical skill package does not shrink at all**: Level-1
installs get the banner and lose nothing. Second, **this is still a prompt
change with an unmeasured behavioural effect.** The duplication sits in the
primacy position at the top of the instructions field, and repetition may be
doing compliance work that character-counting cannot see. Removing it is
defensible because the surviving copy is in the same document and is strictly
more informative — but "defensible" is not "measured", and the paste smoke test
below is the check.

### 3. Version bump — v2.0.2 → v2.1.0, MINOR

The first non-patch bump since v2.0.0, and the semver case is specific:

- **It is a change to the output contract, so it is not a PATCH.** ADR-002 and
  ADR-003 were patches because each corrected a defect in wording that was
  already meant to work one way. This adds a required output element that did
  not exist. A consumer reading a v2.1.0 answer sees something a v2.0.2 answer
  never contained.
- **It is additive and backward compatible, so it is not a MAJOR.** Nothing is
  removed, renumbered, or redefined; items 1–7 are untouched. Anything that
  parsed a v2.0.2 delivery still parses a v2.1.0 one, with one extra line above
  it. That is semver's definition of MINOR.
- **The version now appears inside the protocol's own output**, which is the
  point — an answer states which protocol produced it — and has one downstream
  rule: **any check for the banner must match the prefix plus a semver, never a
  literal string.** A test pinned to `v2.1.0` breaks on the next bump and would
  be read as an activation failure.

### 4. The detection upgrade

- **`grade.py` gains a `banner_present` mechanical check** matching
  `⟦innovate-or-die v<semver>⟧` as the first non-empty line, and `evals.json`
  gains the corresponding assertion.

  **Refined while applying.** The draft did not say which arm the assertion is
  graded in, and both obvious answers are wrong. Graded in **both** arms, it
  manufactures a delta: the control has no protocol and can never emit the
  banner, so the protocol's own signature would be scored as a quality
  difference. Graded in the **with_skill** arm only, it changes that arm's
  denominator and breaks comparability with iterations 1 and 2. So assertions may
  now carry an `arm` field; arm-restricted results are reported under
  `arm_specific_results` and are excluded from `summary`, from `pass_rate`, and
  therefore from every paired delta. The banner is an activation signal, not a
  quality assertion, and the harness now says so structurally.
- **`run_evals.py`'s Codex leg replaces `markers >= 2` with the exact-string
  test**, and records `activation_method: "observed:banner"`. This is the
  near-deterministic part: a seven-regex fuzzy vote becomes a string comparison
  on hosts that expose no tool-call stream at all.
- **The Claude leg keeps the `Skill` tool call as ground truth** and records the
  banner alongside it. That is what makes the validity check below possible: the
  new detector is measured against the old one rather than replacing it on faith.
- **It makes the cheap activation survey work everywhere.**
  `NOTE-activation-variance.md` proposes an OBSERVE-AND-ABORT instrument that
  kills a run as soon as activation is decided, at ~1% of a full run's cost —
  currently limited to hosts with a `stream-json` event stream. With a banner on
  the first line, any host that streams tokens can be aborted on the first line.
  That is the prerequisite instrument for the description-field workstream, which
  needs a real sample rather than a fourth anecdote.

---

## Scope — what is deliberately NOT in this ADR

- **This does not make activation more reliable.** It makes non-activation
  visible. The activation rate is a `description`-field problem and stays open
  in `NOTE-activation-variance.md`; that note's fourth hypothesis must still be
  pre-registered before it is tested.
- **The banner does not prove the protocol was followed.** It proves the
  instructions were in context. A model can emit the line and still skip the
  kill list — most plainly on the Level-4 fallback rung, where the whole
  document is pasted into the chat and the model can copy the first line without
  running anything. The README wording must say what it attests to and no more.
- **No role, quota, gate, or delivery-content change.** Items 1–7 are untouched.
- **No telemetry.** The banner is text in an answer. Nothing is transmitted,
  logged, or phoned home, and nothing here should ever imply otherwise.
- **No change to the activation *denominator* problem.** Copilot §6 item 4 asks
  for activation to be tracked as a rate with an N. The banner is the instrument
  that makes that survey affordable; running the survey is separate work.
- **T3 (the workflow Independence trim) is not adopted.** It is measured here so
  the reserve is known, not proposed.

---

## Consequences

### The expected failure mode is a false negative, and it may be common

The banner's guarantee is **asymmetric**:

- **Banner present ⇒ the protocol ran.** Near-certain: no unassisted model emits
  that string.
- **Banner absent ⇏ the protocol did not run.** A model that activated may still
  omit a required output element.

That second line is not hypothetical. Measured over activated `with_skill` runs
in the committed workspace, mandatory Stage 6 elements appear at these rates by
mechanical check:

| Required element | Emitted |
|---|---|
| Experiment spec, all five fields | 12/17 (71%) |
| Kill list, ≥ 5 items | 10/17 (59%) |
| A falsifier carrying a number | 4/17 (24%) |

Compliance with a mandatory delivery item is **not** near 1.0 today.

**Position is the reason to expect the banner to do better, and it is a
mechanism rather than a hope.** The three elements measured above all fall *late*
in the delivery — the experiment spec is item 5, the kill list item 6 — and each
requires the model to generate substantive content under accumulating
output-length pressure, after the thesis and opportunities have already been
written. Compliance decays down that list: 71% at item 5, 59% at item 6, and the
falsifier standard, which is a property every claim must carry throughout rather
than a section, at 24%. The banner is item 0. It is emitted before any of that
pressure exists, it is a fixed string, and it requires no thinking. The
prediction is therefore that it lands well above 71%, not between 59% and 71%.

That is a prediction with a stated mechanism, not a measurement, and this ADR
must not assume it.
**The first thing to measure after applying this is the banner's emission rate on
runs known to have activated.** If it lands near 60%, the banner is a weak
instrument and needs reinforcement (repeating the requirement in the preamble, or
in the "Load the method" section) before the README leans on it.

Note also that these mechanical checks can undercount — a four-item kill list, or
a differently-worded heading, fails the check while the protocol did run. They
bound compliance from below.

### Files that change when this is applied

1. `core/workflow.md` — Stage 6 item 0.
2. `core/skill-meta.json` — version 2.0.2 → 2.1.0.
3. `build/assemble.py` — `PREAMBLE_SPLIT` trim (T1+T2).
4. All 42 generated files — regenerated; the `(core v…)` headings move to 2.1.0
   automatically.
5. `evals/runners/grade.py` + `evals/evals.json` — the `banner_present` check.
6. `evals/runners/run_evals.py` — Codex activation by banner; Claude records both.
7. `README.md` — *"To check whether it actually ran"* names the banner, with the
   asymmetry stated: a banner means it ran; no banner is a strong hint, not proof.
8. `docs/COMPATIBILITY.md` — the headroom section. **It currently contains a
   stale paragraph** claiming 7,874 chars and 126 of headroom, superseded by the
   2026-08-20 warning block above it that says 7,967 and 33. Applying this ADR is
   the moment to delete the stale one rather than add a third figure.
9. `docs/NOTE-activation-variance.md` — cross-link, and note that the ledger's
   detection method changes from this version on, so activation counts before and
   after are measured differently.
10. `CHANGELOG.md` — a `[2.1.0]` section.

### Comparability

Every eval result to date was produced under a protocol with no banner.
Activation counts recorded before v2.1.0 come from the tool-call stream (Claude)
or the marker heuristic (Codex); counts after come from the banner. **The ledger
in `NOTE-activation-variance.md` must say which method produced each row**, as it
already does for `inferred` vs `observed`, or the 3-of-7 becomes uncomparable to
whatever the survey finds.

### Cost

24,988-char fallback, 5,012 under the 30,000 ceiling added in wave 1. No new cap
is approached. The banner costs the user one line of output.

---

## Regression test

1. `python3 build/assemble.py --check` — must pass, with **no SLACK warning**
   (i.e. ≥ 200 chars of headroom on all three web targets). The build is the gate:
   if the composition does not fit, nothing ships.
2. `python3 -m pytest` — must pass, including the placeholder guard, which is
   what proves the banner's version was substituted rather than shipped as
   `{{CORE_VERSION}}`.
3. **Banner-emission measurement, pre-registered before the runs.**
   *Codex half done 2026-08-20: 5 of 5 on `gpt-5.6-terra`, recorded in
   `NOTE-activation-variance.md`. It carries no ground truth — the Claude half
   below is what tests the detector against independent evidence, and it is
   quota-blocked.* On Claude,
   where the `Skill` tool call is independent ground truth, record for every
   `with_skill` run: activated (tool call) × banner present. The prediction to
   record in advance is that **banner presence equals observed activation** —
   and the interesting cell is activated-but-no-banner, which is the false
   negative rate. This is a validity check of a new instrument against an old
   one, in the same spirit as `2026-08-20-judge-validity-dental.md`.
4. **One paste smoke test per web target**, because the compensating trim removes
   text from the top of the instructions field: paste the regenerated
   instructions file, attach the knowledge file, run one case prompt, and confirm
   the run still announces its passes in order and still reads the role briefs at
   their stages. One run per host is a smoke test, not evidence.
5. **One fallback paste test**, specifically to see whether the model emits the
   banner *without* doing the work — the failure mode named in Scope.

---

## Open questions

- **`⟦ ⟧` vs `[[ ]]`.** Measured at +128 vs +130 characters, so cost does not
  decide it. The question is rendering: whether every target host displays
  U+27E6/U+27E7 rather than a replacement glyph. Settle it by paste test on all
  three web targets before applying, the same method that settled the caps.
- **Should the banner name the stage or mode** (e.g. `· stage 6 delivery`, as the
  review's example did)? It would distinguish a full delivery from a partial one,
  at roughly 20 more characters. Deferred: there is no measurement yet showing
  partial deliveries are being mistaken for full ones.
- **Should the requirement be repeated** in "Load the method" as well as Stage 6?
  That is the obvious reinforcement if the emission rate comes back low. Cost is
  ~90 characters against 301 of headroom, so the reserve exists. Do not spend it
  pre-emptively — measure first.
- **Is the ChatGPT 8,000 cap still 8,000?** Re-verification is cheap (a paste
  test) and could change the whole budget picture, but the plan above deliberately
  does not depend on it: it fits under the cap as verified on 2026-08-19. Gemini's
  true cap remains an unknown *lower* bound and must not be assumed larger.

---

## Evidence

- `docs/notes/copilot-github-review.md` §3.1, §4, §6 — the recommendation, at repo
  state `fc3325e`.
- `docs/NOTE-activation-variance.md` — the 3-of-7 ledger, the three falsified
  hypotheses, and the OBSERVE-AND-ABORT instrument this banner would extend to
  hosts without a tool-call stream.
- Build measurements in the table above — produced by building the real
  artifacts from a modified copy of `core/`, 2026-08-20, not estimated.
- Compliance and control-arm rates — computed over the committed
  `evals-workspace/` grading records, 2026-08-20: 0/19 control-arm structural
  passes; 12/17, 10/17, 4/17 on activated treatment runs.
- `evals/runners/run_evals.py` — the `heuristic:markers` Codex path this replaces.
