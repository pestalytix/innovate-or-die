# ADR-002 — Stage 0 must complete in a single turn

**Date:** 2026-08-19 · **Status:** ACCEPTED 2026-08-19 · **Affects:** core protocol v2.0.0 → v2.0.1

## Context

Iteration-1 evals (see `evals/results/2026-08-19-codex-gpt-5.6-terra.md`) surfaced a
reproducible failure. On `eval-route-density`, the `with_skill` arm returned **771 bytes
(761 characters; the delta is multi-byte UTF-8 punctuation): three clarifying
questions and nothing else.** It scored **0.143 against its
own control's 0.571 — a delta of −0.428**, the only negative case in the baseline,
and the blind pairwise judge independently scored that case for the control arm.

The run had activated correctly. Asking a batch of up to three questions *is* Stage 0
behaviour. The defect is what happened next: nothing.

`core/workflow.md` Stage 0 currently reads:

> If two or more of those are missing, ask up to three questions in a single batch,
> **then proceed regardless** — one round only. If the user says "just go," go,
> marking gaps as assumptions.

"Then proceed regardless" presumes a conversational host where the author sees a
reply. In a single-shot invocation — `claude -p`, `codex exec`, a scheduled run, an
API call, any non-interactive host — **there is no second turn.** The questions are
the entire output. The user receives no analysis at all, and every downstream stage
is skipped.

This is not a model failure. The instruction is ambiguous about *when* to proceed,
and a model that asks and waits is reading it defensibly.

## Decision

Amend Stage 0 with an explicit no-second-turn clause. Questions become optional and
non-blocking; proceeding is mandatory **within the same response**.

Proposed wording (exact text subject to review):

> If two or more of those are missing, do not ask and wait. Assume the most probable
> answer to each gap and carry it forward as a labelled assumption. **Never emit a
> standalone block of questions:** many hosts give you no second turn, so a reply that
> ends in questions has failed regardless of how good the questions are. The gaps
> surface in the Stage 6 delivery instead — each as a stated assumption noting what
> changes if it is wrong — so the canonical output structure is preserved and the run
> always completes. If the user later corrects an assumption, revise then.

The key move is structural rather than exhortative. Rather than telling the model to
ask *and also* proceed — which is what v2.0.0 already said, and which failed — the
questions are **relocated into an output section that already exists.** A standalone
question block has nowhere to live in the Stage 6 structure, so ending in questions
becomes structurally impossible rather than merely discouraged.

Semver: **patch → v2.0.1.** This clarifies an instruction that was already meant to
mandate proceeding; it changes no role, quota, gate, or output structure.

## Scope — what is deliberately NOT in this ADR

Three other iteration-1 findings were considered and excluded (Gate D ruling 2):

**Stage 6 workhorse non-compliance — OUT.** `gpt-5.6-terra` omits the compact kill
list and the "what may still be missing" section. This is recorded as a **documented
limitation under the gradient framing**, not fixed: compliance and cost scale with
model tier, and full Stage 6 compliance was observed only on flagship-tier models.
Tightening the protocol to force compliance from weaker models would add words to
solve a capability gap, which the ADR-001 consequences section already warns against.

**Thoroughness-vs-actionability — OUT.** The judge preferred the *control* arm on two
flagship cases for being more concrete and implementable, while preferring the skill
arm elsewhere for sharper falsifiers and explicit thresholds. That is a real
hypothesis about a trade-off the protocol may be making — and it is **untested**.
It becomes an **iteration-2 assertion** (recorded in `evals/evals.json` under
`_iteration_2_assertions_pending`, with authored-after-observation provenance) so the
next baseline measures it rather than assuming it. Changing the protocol on n=5
single-run anecdote would be exactly the reasoning the protocol itself forbids.

**Cross-host activation variance — OUT, and not a protocol matter.** On identical v1
prompts, Claude missed `eval-dental-no-shows` while Codex activated on it; Codex
stalled `eval-route-density` while Claude ran it fully. Activation is governed by the
`description` frontmatter and each host's dispatch implementation, neither of which
lives in the protocol body. See `docs/NOTE-activation-variance.md` — description-field
optimization is its own workstream.

## Consequences

- One-line-scale change to `core/workflow.md` Stage 0; every generated adapter
  regenerates from it via `build/assemble.py`, and CI's `--check` enforces that.
- `CHANGELOG.md` gains a 2.0.1 entry linking here.
- Iteration-2 re-runs `eval-route-density` on `gpt-5.6-terra` as the direct
  regression test: the fix works if that case's `delivers_answer` assertion passes
  and its delta moves off −0.428.
- **Risk — confident analysis on bad assumptions.** Instructing the model never to
  wait may produce a fully-formed answer built on a wrong guess. Mitigated by
  requiring every assumption be labelled with what changes if it is wrong.
- **Risk — cost on conversational hosts.** Where a second turn *was* available, one
  clarifying question could have cost a few hundred tokens; proceeding on a wrong
  assumption instead spends a complete protocol run to reach a misaimed answer. On
  Claude that is the **~500,000-token scale** measured in iteration-1
  (`claude-sonnet-5`: 523,224 tokens, 713 s for a single `with_skill` run), and the
  user pays it again on the corrected re-run.

  **Accepted anyway**, for two reasons. Host-type detection is unreliable — the model
  cannot tell from inside a turn whether a reply will ever be read, and a
  wrong guess in that direction is exactly what produced this defect. And the failure
  modes are not symmetric: proceeding on a labelled wrong assumption yields a
  recoverable answer the user can correct, whereas stopping yields nothing at all.
  Expensive-and-wrong beats cheap-and-absent, and the labelling requirement makes the
  wrongness visible rather than buried.

## Evidence

| Case | arm | assertions | tokens | duration | outcome |
|---|---|---|---|---|---|
| `eval-route-density` (terra) | with_skill | **1/7** | 8,058 | 16s | asked 3 questions, stopped |
| `eval-route-density` (terra) | without_skill | 4/7 | 1,440 | 17s | answered |

Reclassified `activated=true, failure_mode="stage0-stall"` — the failure is charged
to this defect, not to activation reliability.
