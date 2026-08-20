# Innovate or Die

A search procedure for hard, open-ended problems. It generates candidate ideas,
attacks them in a separate context, revises what survives, and turns the
strongest hypotheses into experiments you could actually run this week.

The point is not novelty. The point is **overlooked value** — and if the honest
finding is that the conventional approach is near-optimal, the protocol is built
to say so and label it as such.

## What it does

Six stages, four roles, one bounded correction loop:

1. **Frame** — restate the real problem, name what counts as the obvious answer.
2. **Innovate** — at least 10 assumptions classified real-vs-inherited, 5
   reformulations, 8 lenses from distant fields, 30 candidates with mechanisms.
3. **Critique** *(isolated)* — a seven-test fake-novelty detector, a nine-probe
   adversarial checklist, and a falsifier standard. Killing 8–15 of 30 is normal.
4. **Revise and select** — reopen the territory the critic named, pick finalists
   on asymmetric potential, push each to its more radical version.
5. **Gate** — eight dimensions scored 1–5; pass needs every score ≥ 4.
6. **Deliver** — strongest thesis first, then the reframing, top opportunities
   with mechanisms, the most contrarian hypothesis, the cheapest
   high-information experiment, a compact kill list, and what may still be missing.

The quotas are the point. Enforcement by exhortation demonstrably fails; the
numbers are what force a real search.

## Install

| Surface | How |
|---|---|
| **Claude Code** (plugin) | `/plugin marketplace add pestalytix/innovate-or-die` then `/plugin install innovate-or-die@pestalytix` |
| **Any Agent Skills host** | Copy `skills/innovate-or-die/` into the host's skills directory |
| **Codex CLI** (plugin) | Install this repo as a plugin — `.codex-plugin/plugin.json` points at `skills/` |
| **Codex** (repo-local) | Already present at `.agents/skills/innovate-or-die/` — clone and it is discovered |
| **GitHub Copilot** (repo-local) | Already present at `.github/skills/innovate-or-die/` — clone and it is discovered |
| **VS Code / Visual Studio** | Copy `adapters/copilot/agents/*.agent.md` into `.github/agents/` (or `~/.copilot/agents`). Start with the `innovate-or-die` orchestrator |
| **ChatGPT Custom GPT** | Paste `adapters/web/chatgpt-gpt-instructions.md` into Instructions; upload `chatgpt-gpt-knowledge.md` as Knowledge |
| **Gemini Gem** | Paste `adapters/web/gemini-gem-instructions.md` into the Gem instructions; attach `gemini-gem-knowledge.md` |
| **M365 Copilot Agent Builder** | Paste `adapters/web/m365-copilot-instructions.md` into Instructions (8,000-char field); add `m365-copilot-knowledge.md` as a knowledge source |
| **Any host without attachments** | Paste `adapters/web/<target>-fallback.md` whole — see rung four below |

Then ask it something hard, or say `innovate or die`.

## Fidelity ladder

Role separation is the load-bearing design choice: an author that knows the
filter optimizes for the filter. Hosts differ in how much real isolation they
can provide, so fidelity degrades in four known steps.

**Rung 1 — Agentic hosts with subagents.** Claude Code, Codex, Copilot coding
agent. The innovator and critic run in genuinely separate contexts. Full fidelity.

**Rung 2 — Copilot `.agent.md` profiles.** One profile per role plus an
orchestrator. Isolation is real but *manual*: you open a fresh chat per role and
hand forward only what the next role is entitled to see. Fidelity depends on you
following that.

**Rung 3 — Web loader + knowledge file.** ChatGPT GPTs, Gems, Agent Builder. One
context, staged reading: the instructions file carries the principles and
workflow, the role briefs live in an attached knowledge file read stage by stage.
Two caveats — there is no true isolation, only discipline; and knowledge-file
access is **retrieval-mediated**, so a role brief may in principle arrive in
fragments. **Tested once and passed:** a verbatim quota-extraction probe on a
Gemini Gem (2026-08-19) returned all eight Innovator quotas intact and exact, with
no fragmentation of enumerated lines. ChatGPT GPTs and M365 Agent Builder use
different retrieval implementations and remain untested.

**Rung 4 — Single-paste fallback.** Everything inlined in one document, for hosts
that take no attachment. The whole protocol — including what the critic checks
for — is in context from the first token, which is the anchoring failure the
design exists to defeat. It also exceeds every known instruction-field cap
(~19,800 chars), so it may be truncated. Shipped because a documented degraded
path beats an undocumented one, not because it is recommended.

## Limitations

- **The skill does not always activate.** In the published baseline, **3 of 7
  `with_skill` runs activated on Claude Code** (raw counts — the sample is far too small
  for a rate). A non-activated run looks exactly like a normal answer: there is no error
  and no indication the skill was skipped. Activation was reliable on Codex in the same
  baseline. **The mechanism is not understood** — three hypotheses were proposed and all
  three falsified; see [docs/NOTE-activation-variance.md](docs/NOTE-activation-variance.md).

  **Workaround — invoke it explicitly** rather than relying on description matching:

  ```
  Use the innovate-or-die skill on this: we run residential pest control in three
  towns and windshield time is eating us alive. what are we missing?
  ```

  If the answer comes back without a kill list and a falsifiable experiment, the skill
  did not run.

- **Role separation is not evidence.** The evaluator is a quality gate, not proof
  of correctness. A protocol that scores itself well can still be wrong.
- **It is token-expensive by construction.** Quotas guarantee volume. Terse-format
  rules keep it bounded, and the evaluator does not reward length.
- **It does not verify facts you do not give it.** Where a load-bearing claim
  rests on a regulation, cost figure, or market size it does not have, the
  protocol is instructed to say so and name what must be looked up rather than
  invent a number. Check those before acting.
- **Wrong tool for settled questions.** Choosing among already-defined options is
  decision analysis; executing a plan is a delivery workflow. Neither is this.
- **Two web caps are unverified.** The ChatGPT Custom GPT and Gemini Gem
  instruction limits have no first-party source. See `docs/COMPATIBILITY.md`.

## Evaluation

This skill is evaluated against itself: every test case runs twice, once with the skill
and once without, same prompt and model, and the **delta** is the result. Iteration-1 is
the v2.0.0 two-provider baseline; iteration-2 re-measures the Codex workhorse tier under
v2.0.1 after the [ADR-002](docs/ADR-002-stage0-single-turn.md) Stage 0 fix, with N=3
majority-vote grading introduced after grader nondeterminism was measured.

| Results | |
|---|---|
| [Codex workhorse, v2.0.0](evals/results/2026-08-19-codex-gpt-5.6-terra.md) | iteration-1 baseline |
| [Codex flagship, v2.0.0](evals/results/2026-08-19-codex-gpt-5.6-sol.md) | iteration-1 baseline |
| [Claude workhorse, v2.0.0](evals/results/2026-08-19-claude-claude-sonnet-5.md) | + opus envelope probe, activation ledger |
| [Codex workhorse, v2.0.1](evals/results/2026-08-20-codex-gpt-5.6-terra.md) | iteration-2, N=3 grading |
| [ADR-002 regression](evals/results/2026-08-19-adr002-regression.md) | cross-version pair |
| [Grader variance](evals/results/2026-08-19-grader-variance.md) | why grades are replicated |

The results are deliberately unflattering where the evidence is unflattering — including
one case where the skill cost 19x the tokens for no measurable gain.

## How this repo is built

`core/` is the single source of truth. Every install surface above is
**generated** from it:

```
python3 build/assemble.py            # regenerate
python3 build/assemble.py --dry-run  # show what would change
python3 build/assemble.py --check    # CI drift guard
```

Generated trees are committed, because installers read the repo layout. **Do not
hand-edit anything outside `core/`** — CI regenerates and diffs on every push, so
edits to generated files are reverted by the next build.

Protocol changes are ADRs with a semver bump: see
[docs/ADR-001-protocol-merge.md](docs/ADR-001-protocol-merge.md) for why v2
merges a four-role architecture with quota-based enforcement, and
[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md) for every host format fact with
the date it was verified.

## License

MIT © 2026 Ken Pendergast — [kenpendergast.com](https://kenpendergast.com)
