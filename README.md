# Innovate or Die

Ask an AI assistant for ideas and you tend to get the advice everyone else
gets. This is a skill — a set of instructions you add to your AI assistant —
that makes it search harder: it generates a large pile of ideas, has a second
copy of the AI attack that pile in a separate session, keeps only what survives,
and hands you one cheap experiment you could run this week. It is also built to
tell you plainly when the boring, conventional answer is the right one. The goal
is not novelty for its own sake; it is finding the valuable thing everyone
walked past.

## What you'll get back

- **The best idea first**, with the reason it should work — not just what to do,
  but why it would pay off.
- **The ideas it threw away, and why each one died.** This is more useful than it
  sounds: the objection to an idea you were about to try is worth having before
  you spend the money on it.
- **One experiment**, chosen to be the cheapest way to learn the most, with a
  clear number that counts as pass and a clear number that counts as fail.
- **What it might still be missing** — the assumptions it could not check and the
  facts it had to take on faith.

## Get started

Pick the row for the app you use. Some rows install this as a *plugin* — an
add-on package the app loads for you. A repo is this project's folder on GitHub;
`git clone` copies it to your computer. Custom GPTs (ChatGPT), Gems (Gemini),
Agent Builder (Microsoft 365), Projects and Computer skills (Perplexity), and
Agent Skills are each platform's way of adding custom behavior to its AI.

**If you're not sure, use Claude Code — it's two commands**, and it's the setup
this was designed for: the roles genuinely run in separate sessions there. Then
read the first point under [Good to know](#good-to-know), because on Claude Code
it doesn't always switch on by itself.

| App | What to do |
|---|---|
| **Claude Code** | Run `/plugin marketplace add pestalytix/innovate-or-die`, then `/plugin install innovate-or-die@pestalytix`. |
| **claude.ai** (the website or app) | Download `innovate-or-die-skill-v….zip` — the one *without* `flat` in the name — from the [latest release](https://github.com/pestalytix/innovate-or-die/releases/latest), then go to **Customize → Skills → + → Create skill → Upload a skill**. Needs code execution turned on under Settings → Capabilities. |
| **Codex** | Clone this repo — the skill is already at `.agents/skills/innovate-or-die/` and gets picked up automatically. |
| **GitHub Copilot** | Clone this repo the same way — the skill is already at `.github/skills/innovate-or-die/` and gets picked up automatically. |
| **Codex CLI**, as a plugin | Install this repo as a plugin; the file `.codex-plugin/plugin.json` tells it to look in `skills/`. |
| **Any app that accepts Agent Skills** | Copy the folder `skills/innovate-or-die/` into wherever that app keeps its skills. |
| **VS Code / Visual Studio** | Copy `adapters/copilot/agents/*.agent.md` into `.github/agents/` (or `~/.copilot/agents`), and start with the one named `innovate-or-die`. |
| **ChatGPT** | Easiest: open the [ready-made GPT](https://chatgpt.com/g/g-6a85fa3ea49c8191b4a7c58167f8eff5-innovate-or-die) (a link — it is not listed in the GPT Store). Or build your own: paste `adapters/web/chatgpt-gpt-instructions.md` into the Instructions box, and upload `chatgpt-gpt-knowledge.md` as Knowledge. |
| **Gemini** | Easiest: open the [ready-made Gem](https://gemini.google.com/gem/1XoPOHbLHJCR5zxVRxmOKsZVlBzsK5EWj). Or build your own: paste `adapters/web/gemini-gem-instructions.md` into the Gem's instructions, and attach `gemini-gem-knowledge.md`. |
| **Microsoft 365 Copilot**, in Agent Builder | Paste `adapters/web/m365-copilot-instructions.md` into Instructions (that field holds 8,000 characters), and add `m365-copilot-knowledge.md` as a knowledge source. |
| **Perplexity Computer** | Download the **flat** skill zip (`…-skill-flat-….zip`) from the [latest release](https://github.com/pestalytix/innovate-or-die/releases/latest) — Perplexity needs a different zip layout from claude.ai — then go to **Computer → Skills → Create skill → Upload a skill**. |
| **Perplexity**, as a Project | Paste `adapters/web/perplexity-project-instructions.md` into the Project instructions, and upload `perplexity-project-knowledge.md` to the Project's Files. |
| **Any app that can't take file attachments** | Paste the whole of `adapters/web/<target>-fallback.md` (pick the file matching your app) into the chat — the weakest option, and [there is a catch](#what-you-get-on-each-app-fidelity-levels). |

Then ask it something hard, or just say `innovate or die`.

## Good to know

**Sometimes it doesn't switch on, and won't tell you.** The safest habit is to
name it in your request instead of hoping the app notices the topic matches:

```
Use the innovate-or-die skill on this: we run residential pest control in three
towns and windshield time is eating us alive. what are we missing?
```

To check whether it actually ran: **look at the first line.** From v2.1.0 the
answer opens with a marker naming the skill and the version that produced it,
like `⟦innovate-or-die v2.1.0⟧`. If that line is there, it ran — nothing else
writes it.

If it is *missing*, that is a strong hint but not proof: a model that ran the
protocol can still skip the line. The older tell still applies — no list of
rejected ideas and no experiment with a pass/fail number means it didn't run.
There is no error message either way; a run where the skill sat out otherwise
looks exactly like an ordinary answer. In our published testing, the skill was installed for 7
runs on Claude Code and **actually switched on in 3 of them** (that is a raw
count, not a rate — the sample is far too small to be one), while it started
reliably every time in Codex. We do not know why: three explanations were
proposed and all three turned out to be wrong. The write-up is in [docs/NOTE-activation-variance.md](docs/NOTE-activation-variance.md).

**It is slow and it eats your usage allowance**, because it genuinely does more
work — it generates dozens of ideas and discards them down to a few before it
answers you. That cost is the trade. Formatting rules keep the output from
sprawling, and nothing in the design rewards long answers.

**It doesn't know your prices, your local rules, or your regulations.** When an
idea depends on a number or a law it wasn't given, it is instructed to say so and
name what you need to look up, rather than invent a plausible figure. Look those
up before you act on anything.

**It's the wrong tool for two jobs.** If you already have your options and just
need to pick one, that's a decision, not a search. If you have the plan and need
it carried out, that's execution. This does neither.

## Does it actually work?

We tested it by running the same set of problems twice — once with the skill,
once without, same question and same AI both times — and we did it on two
different companies' AI systems. With the skill, the models reliably produce the
protocol's full output structure — falsifiers, a kill list, an experiment spec —
which they rarely produce unprompted. Whether that structure yields better
*decisions* is not yet tested. And it is not always worth the cost: in one case
the skill spent 19 times the tokens for no measurable gain — [see the
results](#evaluation).

---

# For developers and evaluators

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

The quotas exist to force volume. Whether each quota earns its cost is
untested — no ablation has been run.

## What you get on each app (fidelity levels)

Keeping the roles apart is the design choice everything else rests on: an author
who knows the filter optimizes for the filter. Hosts differ in how much real
separation they can provide, so fidelity degrades in four known steps.

**Level 1 — Agentic hosts with subagents.** Claude Code, Codex, Copilot coding
agent. The innovator and critic run in genuinely separate contexts. Full fidelity.

**Level 2 — Copilot `.agent.md` profiles.** One profile per role plus an
orchestrator. The separation is real but *manual*: you open a fresh chat per role
and hand forward only what the next role is entitled to see. Fidelity depends on
you following that.

**Level 3 — One context, staged reading.** ChatGPT GPTs, Gems, Agent Builder,
Perplexity Projects, and Perplexity Computer. The instructions file carries the
principles and workflow, the role briefs live in an attached knowledge file
read stage by stage.
Two caveats — there is no true isolation, only discipline; and knowledge-file
access is **retrieval-mediated**, so a role brief may in principle arrive in
fragments. **Tested once and passed:** a verbatim quota-extraction probe on a
Gemini Gem (2026-08-19) returned all eight Innovator quotas intact and exact, with
no fragmentation of enumerated lines. ChatGPT GPTs and M365 Agent Builder use
different retrieval implementations and remain untested.

**Perplexity Computer sits here too, and is the most capable host on this rung.**
It is the only Level 3 host that installs as a **full zip** rather than a paste
plus an attachment, and the only one that runs **live web search inside the
protocol** — in testing it went and cited sources for an industry figure the
argument depended on, instead of flagging it as something you should look up. It
also **draws on what Perplexity already knows about you**: one run referenced four
facts about the user's projects and location that were nowhere in the prompt,
which is useful more often than not, but worth knowing before you use it on
anything sensitive.

It is not Level 1. Level 1 would require Perplexity to dispatch the skill's
stages as separate sub-agents, and on two observed runs **it did not** — the
roles shared one context, the same as every other host on this rung. The install
being excellent is not the same as the isolation being real, and only the second
one moves a host up.

**Level 4 — Single-paste fallback.** Everything inlined in one document, for hosts
that take no attachment. The whole protocol — including what the critic checks
for — is in context from the first token, which is the anchoring failure the
design exists to defeat. The inlined document (~25k chars, and growing with each
protocol version) also exceeds every known instruction-field cap, so it may be
truncated. Shipped because a documented degraded path beats an undocumented
one, not because it is recommended.

Not every cap behind those levels is equally solid: the Gemini Gem limit is a
lower bound we have watched hold, not a published figure, and the Perplexity
Projects limit is reported by its help centre but never paste-tested. See
[docs/COMPATIBILITY.md](docs/COMPATIBILITY.md), which states the method for each.

## Evaluation

This skill is evaluated against itself: every test case runs twice, once with the skill
and once without (the `with_skill` and `without_skill` arms), same prompt and model, and
the **delta** is the result. The activation counts quoted above are over `with_skill` runs.
Iteration-1 is the v2.0.0 two-provider baseline; iteration-2 re-measures the Codex workhorse tier under
v2.0.1 after the [ADR-002](docs/ADR-002-stage0-single-turn.md) Stage 0 fix, with N=3
majority-vote grading — each judgment made three times, majority wins, because AI graders
vary — introduced after grader nondeterminism was measured.

| Results | |
|---|---|
| [Codex workhorse, v2.0.0](evals/results/2026-08-19-codex-gpt-5.6-terra.md) | iteration-1 baseline |
| [Codex flagship, v2.0.0](evals/results/2026-08-19-codex-gpt-5.6-sol.md) | iteration-1 baseline |
| [Claude workhorse, v2.0.0](evals/results/2026-08-19-claude-claude-sonnet-5.md) | + opus envelope probe, activation ledger |
| [Codex workhorse, v2.0.1](evals/results/2026-08-20-codex-gpt-5.6-terra.md) | iteration-2, N=3 grading |
| [ADR-002 regression](evals/results/2026-08-19-adr002-regression.md) | cross-version pair |
| [Grader variance](evals/results/2026-08-19-grader-variance.md) | why grades are replicated |
| [Judge validity](evals/results/2026-08-20-judge-validity-dental.md) | the judge rewarded novelty on the control case |

The same table, generated from the files themselves and kept next to them, is at
[evals/results/README.md](evals/results/README.md).

Note what this does *not* establish: **role separation is not evidence.** The evaluator is
a quality gate, not proof of correctness. A protocol that scores itself well can still be
wrong.

## How this repo is built

`core/` is the single source of truth. Every install surface above is
**generated** from it:

```
python3 build/assemble.py            # regenerate
python3 build/assemble.py --dry-run  # show what would change
python3 build/assemble.py --check    # CI drift guard
pip install pytest && python3 -m pytest   # harness unit tests
python3 build/package.py             # build both release zips into dist/
```

CI runs `--check` and the tests on every push. The tests cover the generator's
two refusal mechanisms (a substitution that will not silently no-op, a reference
check that will not let an unresolvable path ship), the packager's zip-layout
assertions, and the eval harness's two corrected correctness bugs (matched-pair
aggregation, strict-majority judging).

### Releases

**Release assets are built only by
[.github/workflows/release.yml](.github/workflows/release.yml), on a `v*` tag
push.** Running `package.py` by hand is for inspecting what a release would
contain; it is not how anything gets published. The job re-runs the drift check
and the tests, then refuses to go further unless **the tag equals the `version`
in `core/skill-meta.json`** — without that guard, tagging `v2.2.0` against an
unbumped `skill-meta.json` would publish assets named `…-v2.1.0.zip` and every
download link would point at a file that is not there.

**Two zips ship per release**, because claude.ai wants the skill *folder* as the
zip root and Perplexity Computer wants `SKILL.md` itself there. A zip built for
one does not load on the other — it does not degrade, it fails — so each layout
is asserted against the finished zip before it can be uploaded. The quoted
requirements are in [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md). Assets are
built from the tag with `git archive`, never from the working tree, and are
reproducible: `python3 build/package.py --ref vX.Y.Z` rebuilds the published
bytes. `dist/` is gitignored and never committed.

Cutting a release, in four lines:

```
# 1. protocol change? write the ADR first — docs/ADR-00N-*.md
# 2. bump "version" in core/skill-meta.json
python3 build/assemble.py && git add -A && git commit -m "vX.Y.Z: ..."
git tag vX.Y.Z && git push && git push --tags
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
