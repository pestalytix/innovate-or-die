Iod

# Project Review — innovate-or-die
 
**Reviewer:** GitHub Copilot · **Date:** 2026-08-20 · **Reviewed at:** working tree, core v2.0.2
 
This is a review of the whole repository: the protocol content, the build system,
the adapters, the evaluation harness, and the documentation. It is deliberately
critical — the strengths are summarized quickly so the bulk of the space can go to
things worth changing.
 
---
 
## 1. Overall assessment
 
This is an unusually disciplined project for what it is (a prompt/skill package).
The engineering around the content is the standout: a single source of truth in
`core/`, a deterministic generator that fans out to nine install surfaces, and CI
that fails on drift or on any reference that cannot resolve in its install context.
The documentation is honest to a fault — it repeatedly states what is *not* proven,
which is rare and valuable.
 
The two real risks are both already named by the authors and neither is solved:
**(a)** the skill does not reliably activate (3 of 7 runs on Claude Code), and
**(b)** efficacy is unproven — the evals measure protocol compliance and cost, not
whether the output is actually better. Everything below is secondary to those two.
 
**Verified during review:** `python build/assemble.py --check` passes — 41
generated files match `core/`, with only expected budget warnings.
 
---
 
## 2. What is done well
 
- **Single-source build with a refusing substitution.** `_sub()` raises rather
  than silently no-op'ing when an anchor drifts. This is the correct instinct:
  `str.replace` returning the input unchanged is exactly how a broken reference
  survives a green build. Good defensive design.
- **Referential-completeness check.** `check_references()` proves every quoted
  `*.md` path resolves in the artifact's real install layout, and that single-file
  surfaces contain none. This closes the most common failure mode for this class of
  project (instructions pointing at files the host can't reach).
- **Honest evaluation framing.** `evals.json` includes a *control* case
  (`eval-dental-no-shows`) explicitly designed to punish novelty-forcing, and the
  README states plainly that the judge preferred the skill arm on that control —
  i.e. it reports a result that undercuts the product. The N=3 majority-vote grading
  and blind A/B position-flipping in `judge.py` show real awareness of LLM-grader
  bias.
- **ADR + CHANGELOG discipline.** Protocol changes require an ADR and a semver
  bump; the changelog is specific and traceable (e.g. the Stage 0 single-turn fix
  with the actual failing byte count and score). This is better than most
  production codebases.
- **Injection hardening (ADR-003).** The workflow now treats supplied evidence as
  data-not-directive, which matters because the protocol reads external pages by
  design.
- **Prose quality.** The role briefs are tight and mechanism-focused. The critic's
  seven-test fake-novelty detector and the "strip the adjectives" epistemic rule are
  genuinely good thinking tools.
 
---
 
## 3. Primary concerns
 
### 3.1 Activation is unreliable and undiagnosed (product-breaking)
The README reports the skill activated in 3 of 7 Claude Code runs, with three
proposed explanations all disproven. This is the single biggest threat to the
product: a user cannot tell a no-op run from a real one without inspecting the
output structure. Current mitigations are documentation-only ("name it explicitly",
"check for a kill list").
 
Recommendations:
- Add a **self-identifying banner** the protocol must emit on activation (e.g. a
  first line `⟦innovate-or-die v2.0.2 · stage 6 delivery⟧`). This converts the
  silent-no-op into a visible signal and gives the "did it run?" check a single
  deterministic anchor instead of "look for a kill list."
- Treat activation as a measured metric with a denominator, not an anecdote. The
  README itself flags the 3-of-7 as "a raw count, not a rate." Until there is an N,
  it cannot be tracked as it changes across model/skill versions.
 
### 3.2 Efficacy is unproven and the evals are in-sample
This is stated openly, but it bears repeating as the second-order risk: the
evaluator's dimensions mirror the protocol's own output spec, so the skill is
partly graded against its own template. `docs/NOTE-efficacy-roadmap.md` correctly
scopes what a real study needs. Until then, avoid any external phrasing that could
read as "produces better decisions" — the current README is careful here, keep it
that way in marketing/release notes.
 
### 3.3 The Python harness has no unit tests
CI runs exactly one job: `assemble.py --check` (drift). The grading/judging/
aggregation code (`grade.py`, `judge.py`, `aggregate.py`, `report.py`) — which is
where subtle correctness bugs live, and where two were *just* fixed (unmatched-arm
deltas, the non-majority winner bug) — has no automated tests. Those bugs were
found by inspection, not by a regression test that now guards them.
 
Recommendation: add a minimal `pytest` suite covering at least:
- `aggregate.py` matched-pair logic (the bug fixed in 2.0.2) with a fixture that
  includes an unmatched arm and asserts it is dropped and named.
- `judge.py` majority logic — assert a 1/1/1 A/B/tie split yields no winner.
- `assemble.py` `_sub()` raising on a missing anchor, and `check_references()`
  flagging a single-file surface that contains a `` `*.md` `` reference.
 
These are cheap, and they turn "fixed once" into "cannot regress."
 
---
 
## 4. Secondary issues
 
- **`WEB_TARGETS` caps are partly unverified but treated structurally as hard.**
  The Gemini cap is a "WORKING BUDGET" (accepted-but-unknown), while ChatGPT/M365
  are verified. The generator correctly annotates the warning with `[WORKING
  BUDGET]`, which is good — but the instructions files sit only 33 chars under an
  8,000 cap. That is a fragile margin: any core wording change that adds a line
  will flip an *unverified* budget into a *fatal* over-cap for a target whose true
  cap may actually be higher. Consider carrying a small explicit slack target
  (e.g. warn below ~200 chars of headroom) so a near-miss is visible before it
  becomes fatal.
- **Two instruction-cap sources remain unverified** (ChatGPT/Gemini per README),
  and this is acknowledged. No action beyond keeping the `docs/COMPATIBILITY.md`
  dates fresh — but a calendar reminder to re-verify before each release would
  prevent silent staleness.
- **README install matrix mixes concepts users may conflate.** The table is
  excellent but dense; a first-time user has to parse plugin vs. repo vs. Custom
  GPT vs. fallback in one pass. A one-line "if unsure, do this" default above the
  table would lower the bar.
- **The single-paste fallback (~25k chars) exceeds every known cap and grows each
  version.** This is shipped knowingly as the degraded rung and documented as such
  — fine. But it will keep drifting upward. Worth a hard ceiling in the generator
  that *fails* (not warns) if the fallback exceeds, say, 30k, forcing a conscious
  decision rather than unbounded growth.
- **No `LICENSE`-to-`skill-meta.json` cross-check.** Minor: the license string
  lives in two places (`LICENSE` file, `skill-meta.json`). Not worth a check on its
  own, but if a test suite is added, a one-line assertion is trivial insurance.
 
---
 
## 5. Nits
 
- `docs/` mixes durable reference (ADRs, COMPATIBILITY) with dated working notes
  (`HANDOFF-2026-08-19.md`, `SESSION-STATE-2026-08-19.md`, and now this file).
  Consider a `docs/notes/` subfolder so the ADRs and compatibility matrix — the
  documents a contributor must read — aren't buried among session ephemera.
- The orchestrator `.agent.md` relies on the human to manually open a fresh chat
  per role (Level 2 fidelity). This is documented, but it is the most error-prone
  path and the one most likely to be used incorrectly. A short "you did it wrong
  if…" checklist in that profile would help.
- `evals/results/` filenames encode date + provider + model; good, but there is no
  index. A short `evals/results/README.md` table (already partially mirrored in the
  main README) that lives next to the files would help future readers.
 
---
 
## 6. Suggested priority order
 
1. **Emit a self-identifying activation banner** (§3.1) — cheapest fix for the
   biggest risk; makes "did it run?" deterministic.
2. **Add a `pytest` suite for the harness** (§3.3) — guards the two just-fixed
   correctness bugs against regression.
3. **Add a hard ceiling on the fallback size and a slack-margin warning on web
   instruction caps** (§4) — prevents a future core edit from silently shipping an
   unusable artifact.
4. **Give activation a measured denominator** (§3.1) — track it as versions change.
5. Housekeeping: `docs/notes/` split, an `evals/results/` index, and an
   orchestrator "you did it wrong if…" note.
 
---
 
## 7. Bottom line
 
The scaffolding around this skill is stronger than the evidence that the skill
works — which the authors already say out loud. That honesty is the project's best
feature and should be preserved. Close the activation-visibility gap and put a test
net under the harness, and the engineering will fully match the rigor of the
documentation.