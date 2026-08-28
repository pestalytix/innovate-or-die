# ADR-005 — Binding output contract and literal output template

**Date:** 2026-08-28 · **Status:** **ACCEPTED 2026-08-28, applied in v2.2.0** ·
**Affects:** core protocol v2.1.0 → **v2.2.0**

Raised by a five-cell model/effort test of the v2.1.0 protocol on a single real
prompt (2026-08-28, internal notes), run across two vendors and five
model/effort configurations.

---

## Context

### The problem this addresses

ADR-004 made *activation* visible. It did not make *delivery* uniform. The
five-cell test shows the protocol reliably fires and then produces five
materially different documents, two of which leak the internal search into the
user's answer.

Every cell ran the same prompt against the same v2.1.0 protocol:

| Cell | Banner | Sections present | Numbered | Stage work leaked | Words |
|---|---|---|---|---|---|
| Fable — Low | yes | 7/7 | 7/7 | **yes** | 1,521 |
| Opus — Medium | yes | 7/7 | 7/7 | no | 2,155 |
| Sonnet — High | yes | 7/7 | **0/7** | no | 1,853 |
| Haiku — Extended | yes | 7/7 | **0/7** | **yes** | **7,723** |
| GPT-5.6 Sol — High | **no** | **1/7** | **0/7** | no | 2,028 |

**How these columns are counted.** *Sections present* matches each of the seven
delivery sections by title against any markdown heading in the cell, case- and
numbering-insensitive, accepting the wording variants the protocol itself uses
(`Cheapest`/`Best low-cost … experiment`, `Compact kill list`/`Kill list`,
`Top opportunities`/`Top 3 opportunities`). *Numbered* is the stricter check:
headings matching `^#+ [1-7]\. `. *Banner* is the exact `⟦innovate-or-die
v<semver>⟧` string. *Stage work leaked* matches stage narration — a literal
`STAGE n` heading or a "let me read / I'll run the protocol" preamble. *Words*
is a whitespace split over the whole cell.

Two failures matter, and they are different failures.

**Stage leakage.** Haiku — Extended opens with `Let me read the skill first`,
then emits a literal `## STAGE 0 — FRAME` heading, a numbered ledger of eight
constraints tagged `✓ Real` / `✗ Inherited`, and continues through the internal
passes — 7,723 words, roughly five times every other cell, most of it the search
rather than its result. Fable — Low leaks less but leaks the same way, opening
with narration about loading the skill before the banner. Stage 6 said *"Omit
internal drafts, audits, and scores unless the user asks"*, which is a
disclosure rule about artifacts. It does not forbid narrating the process, and
two of five models read it accordingly.

**Structure noncompliance, which is smaller than it first appears and must be
stated precisely.** Four of five cells emitted all seven delivery sections. Only
**one — GPT-5.6 Sol — actually lost the structure**, keeping the thesis and
dropping the other six: no reframing heading, no opportunities, no contrarian
hypothesis, no experiment spec, no kill list, no what-may-still-be-missing,
restructured instead into free-form headings (`# The product: Commercial Rodent
Entry Control`). It also dropped the banner. That is the one hard failure in the
set, and one of five is the honest count.

What three of five cells dropped is the **numbering**. Sonnet and Haiku produced
all seven sections under the outline's own wording (`Compact kill list`,
`Cheapest high-information experiment`) with no `1.`–`7.` prefixes. Those are
good answers, and under a v2.1.0 outline that never showed a literal heading they
are arguably conformant. The cost is positional: anything reading "section 5"
cannot find it, the mechanical compliance checks in ADR-004 undercount, and the
reader loses the ordering the protocol relies on to lead with the thesis.

Stage 6 described the delivery as a seven-item outline. A description invites
paraphrase; three of five models paraphrased the form while keeping the content,
and one paraphrased the content away.

**Length is unbounded.** No cell came in under 1,500 words; the spread is 1,521
to 7,723. Nothing in v2.1.0 bounds the deliverable, and the evaluator is
explicitly told not to reward length — which restrains the grader, not the
generator.

### Why the existing gate did not catch this

`roles/evaluator.md` scores eight quality dimensions. None of them is
"conforms to the delivery structure." A leaked Stage 0 dump can score well on
every dimension the gate measures, because the gate reads the ideas, not the
envelope.

---

## Decision

Three parts. Parts 1 and 3 must land in the same commit — part 1 alone fails the
build, for the reason measured in part 3.

### 1. A binding output contract, replacing the Stage 6 disclosure rule

`core/workflow.md` gains an **Output contract** section stating that the
response contains only the final deliverable; that all stage work — framing,
lenses, candidate generation, adversarial passes, scoring — is internal and
never emitted **in any form, at any effort level**; and that no stage names,
lens names, candidate lists, evaluator scores, drafts, or process narration
appear anywhere in the response.

Three properties are deliberate:

- **"At any effort level" is load-bearing.** The two leaking cells are the
  lowest and the highest reasoning configurations in the set (Fable — Low,
  Haiku — Extended). Leakage is not a property of thinking harder or less; the
  rule cannot be scoped to one end.
- **The on-request search log survives.** v2.1.0's *"offer the full search log
  on request"* is carried into the contract's first paragraph rather than
  dropped. The contract governs the unsolicited answer, not what the user may
  ask for afterward.
- **It bounds length.** 900–1,500 words total, with per-section ceilings that
  are explicitly ceilings and not targets, and with the total taking precedence.
  1,500 is above four of the five observed cells and cuts the fifth by 80%.

The contract also requires receipts for any section reporting no surviving idea,
and refuses a search that rejected fewer than two serious alternatives. Its
closing line states the intent in one sentence: *a response that shows 30
candidates has failed; a response that shows the 3 survivors of 30 has
succeeded.*

### 2. A literal template, replacing the seven-item outline

The outline becomes a template the model copies rather than a description it
paraphrases, carrying the ADR-004 banner as its first line and adding a
`Problem as framed` preamble that labels assumptions.

Items 1–7 keep their numbers, order, and meanings. Two counts change, both
because the fixed numbers were arbitrary:

- **Opportunities: "up to 3" → 2–4**, with C and D only when they materially
  improve the answer.
- **Kill list: a fixed 5 → 2–6**, with an explicit ban on inventing trivial
  rejects to reach the minimum. ADR-004 measured kill-list compliance at 10/17;
  a fixed count that a model cannot honestly fill invites padding, which is the
  failure the ban names.

Section 5's field list is duplicated from `references/experiment-spec.md` so the
template stands alone. Both files carry a comment saying they must match, since
from this version they ship in the same web knowledge file.

**The four superseded Stage 6 clauses are deleted, not left alongside.** The
banner instruction (item 0), the opportunity count, the kill-list count, and the
disclosure line were each restated — differently — by the contract. Leaving both
would create four places where the delivery is specified and no rule for which
wins.

### 3. The web adapters split the contract to the knowledge file

The contract and template are **3,715 characters** against **301** of headroom —
the reserve ADR-004 banked. Inlining them everywhere was measured, not
estimated:

| Composition | Instructions | Headroom | Fallback |
|---|---|---|---|
| v2.1.0 as shipped | 7,699 | 301 | 24,988 |
| **+ contract and template inline** | **11,371** | **−3,371 — build fails** | 28,849 |
| + contract and template, split to knowledge file | **7,842** | **158** | 28,964 |

The four capped instruction fields therefore carry a **micro-contract** — the
response is only the deliverable, copy the template from the knowledge file,
never emit stage work — and the full text ships in the attached knowledge file,
beside the experiment spec that template section 5 mirrors and that is read at
the same moment: when the final answer is assembled.

This is the split already used for role briefs, the lens bank, and the
experiment spec; it is applied to one more section. **Both variants are authored
in `core/workflow.md` between `SPLIT` markers**, so the wording lives in the
source file and `build/assemble.py` only routes between them. A missing marker
raises rather than silently emitting neither block, matching `_sub()`'s refusal
to no-op.

Claude, Codex, GitHub, the Copilot orchestrator, and the single-paste fallback
are unaffected and keep the full text inline.

**The banner consequently has exactly one home per target.** It rides with the
template, so on web targets it moves from the instructions file to the knowledge
file. ADR-004's table said knowledge files carry no banner *because they
assemble nothing*; that premise no longer holds, and the two guards in
`tests/test_banner.py` are inverted to match. A banner in a web instructions
file is now a defect — it means the template leaked back inline, which is what
breaches the cap.

### Version bump — v2.1.0 → v2.2.0, MINOR

- **Not a PATCH:** this changes the output contract. A consumer reading a v2.2.0
  answer sees a `Problem as framed` block, per-section word ceilings, and a
  bounded total that no v2.1.0 answer contained.
- **Not a MAJOR:** sections 1–7 keep their numbers, order, and meanings.
  Anything that parsed a v2.1.0 delivery still parses a v2.2.0 one. The two
  count changes widen ranges rather than removing anything — a 3-opportunity,
  5-item-kill-list answer remains valid.

---

## Alternatives rejected

**Per-model conditional guidance.** The obvious reading of the table is that
different models need different instructions — tell Haiku not to narrate, tell
GPT-5.6 to keep the numbers. Rejected on two grounds. It is **unmaintainable**:
the protocol ships to at least eight surfaces across two vendors, model
identifiers change without notice, and the matrix would need re-measuring every
release against models we cannot enumerate. More decisively, it is
**undetectable at runtime**: `core/` is static text with no branch point, the
skill cannot reliably know which model or effort level is executing it, and a
model that misidentifies itself would select the wrong branch. A single rule
every model must satisfy is the only kind this system can express.

**Raising the instruction-field cap.** The 8,000-character limit is verified on
ChatGPT and M365 Copilot and reported on Perplexity. It is a platform limit, not
a repo constant — `WEB_TARGETS` records it, it does not set it. Nothing in this
repo can raise it, and treating the Gemini working budget as larger would be
assuming an unknown lower bound is generous.

**Trimming `core/` to fit the contract inline.** The overflow is 3,371
characters against a 3,715-character addition: fitting it inline means removing
essentially the whole contract, or gutting `principles.md`. Rejected as
self-defeating.

---

## Scope — what is deliberately NOT in this ADR

- **No change to the search.** Roles, quotas, lenses, gate thresholds, and the
  one-loop correction rule are untouched. This ADR governs what reaches the
  user, not how the answer is found.
- **No new evaluator dimension for structural conformance.** The gate still
  scores eight quality dimensions and does not read the envelope. Adding a ninth
  is a candidate if compliance stays low — see Open questions.
- **This is not measured.** The five-cell test is the *motivation*; nothing here
  has been re-run against it. n=1 prompt, n=1 run per cell, two vendors. It
  identifies failure modes; it does not establish rates, and this ADR must not
  be cited as though it did.
- **The word budget is a judgement, not a finding.** 900–1,500 was chosen to sit
  above four observed cells and well below the fifth. No evidence says 1,500 is
  the right ceiling.

---

## Consequences

### The slack target is now breached, deliberately

Web instructions land at **7,842 of 8,000 — 158 spare**, under the 200-character
slack target ADR-004 established, so the build warns on every run. Accepted
rather than trimming the micro-contract, whose whole function is to be
unambiguous on a surface that cannot hold the real rules. **The practical
consequence: the next inline addition to the web adapters requires trimming
existing text or moving content to the knowledge file.** The reserve ADR-004
banked is spent.

The single-paste fallback moves 24,988 → **28,964, leaving 1,036 under the
30,000 ceiling.** No new cap is approached, but the fallback is now the closest
it has been to its ceiling, and the README's figure is pinned to that constant
rather than quoting a size that goes stale each release.

### The expected failure mode is a partially-copied template

A model that ignores a described outline will ignore a literal template too. The
template is a stronger instrument — it removes the paraphrase step, and the
cells that dropped the numbering kept every section, which suggests paraphrase
rather than refusal and is the failure a literal template most directly fixes.
GPT-5.6 Sol is the harder case: it did not paraphrase the form, it replaced it,
and nothing here guarantees a template survives that. "Stronger" is not
"reliable," and the compliance rates in ADR-004 (12/17, 10/17, 4/17 on
late-position elements) are the base rate to beat.

Note the new risk this introduces: **a template invites structural compliance
without substance.** A model can emit seven correctly-numbered headings filled
with hedges. The contract's "exceptions require receipts" clause and the ban on
promoting weak ideas exist for exactly that, and they are the harder thing to
verify mechanically.

### Files that change when this is applied

1. `core/workflow.md` — Stage 6 clauses deleted; contract, template, and
   micro-contract added between `SPLIT` markers.
2. `core/references/experiment-spec.md` — field list aligned to template
   section 5; thresholds rule added.
3. `core/skill-meta.json` — version 2.1.0 → 2.2.0.
4. `build/assemble.py` — `contract_full` / `contract_micro` / `contract_block`
   routing; the knowledge file gains the contract block.
5. All 45 generated files — regenerated; `(core v…)` headings move automatically.
6. `tests/test_banner.py` — the two banner-location guards, inverted.
7. `README.md` — the fallback size figure, pinned to `FALLBACK_CEILING`.
8. `CHANGELOG.md` — a `[2.2.0]` section.

---

## Regression test

1. `python3 build/assemble.py --check` — must pass. A SLACK warning on the four
   web instruction files is **expected** and accepted; a cap breach is not.
2. `python3 -m pytest` — must pass, including the inverted banner guards and the
   unresolved-placeholder check, which must still fail on a `{{CORE_VERSION}}`
   that did not substitute, wherever the banner lives.
3. **Re-run the five-cell test on v2.2.0**, same prompt, same five
   model/effort configurations, counted by the same definitions given above.
   The pre-registered prediction is that leakage goes to 0/5, sections present
   to 5/5, and numbering to 5/5. Two cells are the ones to watch: **Haiku —
   Extended**, the worst leak and the longest answer, and **GPT-5.6 Sol**, the
   only cell that lost the structure and the only one that missed the banner.
4. **One paste smoke test per web target**, because the split moves text the
   model needs across a file boundary: paste the instructions, attach the
   knowledge file, and confirm the answer follows the template that now lives
   only in the attachment. This is the split's specific risk — an instructions
   file that points at a template the host failed to attach produces an answer
   with no structure at all.

---

## Open questions

- **Does the template hold without the contract?** The split means web
  instruction fields carry the micro-contract only. If a host silently drops the
  knowledge file, the model has a binding rule and no template. Worth measuring
  whether the micro-contract alone produces acceptable structure.
- **Should structural conformance become an evaluator dimension?** It would move
  the check inside the loop rather than relying on the model to comply on the
  way out. Deferred until item 3 above says whether compliance is actually the
  problem.
- **Is 1,500 words right?** Chosen, not measured. If re-running the five-cell
  test shows answers truncating mid-argument to obey it, the ceiling is wrong
  and the fix is a higher ceiling, not a weaker rule.
- **Does the `Problem as framed` preamble reintroduce leakage?** It asks the
  model to restate the framing — adjacent to the Stage 0 dump the contract
  forbids. The distinction is a ≤100-word labelled restatement versus a narrated
  pass, and it is the clause most likely to be over-read.

---

## Evidence

- The five-cell model/effort test, 2026-08-28 (internal notes, not committed).
  One prompt (commercial rodent-exclusion marketing, Worcester County), five
  model/effort configurations across two vendors, run under v2.1.0. The table
  above reproduces every measurement taken from it.
- The compliance table above — computed mechanically over those notes, by the
  definitions stated beside the table. The *sections present* column is
  title-matched rather than numbering-matched: an earlier count conflated the
  two and scored Sonnet and Haiku at 0/7 when both emitted all seven sections
  under the outline's own wording.
- Build measurements in the split table — real builds of
  `chatgpt-gpt-instructions.md` against the verified 8,000-char cap, 2026-08-28.
- `docs/ADR-004-activation-banner.md` — the banner, the 301-char reserve this
  spends, the 200-char slack target, the 30,000-char fallback ceiling, and the
  late-position compliance rates (12/17, 10/17, 4/17) that are the base rate.
- `docs/COMPATIBILITY.md` — the cap sources and the distribution-identity split.
