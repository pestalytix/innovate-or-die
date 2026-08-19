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
access is **retrieval-mediated**, so a role brief may arrive in fragments rather
than whole. Quota lines are exactly the kind of text retrieval breaks up.

**Rung 4 — Single-paste fallback.** Everything inlined in one document, for hosts
that take no attachment. The whole protocol — including what the critic checks
for — is in context from the first token, which is the anchoring failure the
design exists to defeat. It also exceeds every known instruction-field cap
(~19,800 chars), so it may be truncated. Shipped because a documented degraded
path beats an undocumented one, not because it is recommended.

## Limitations

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
