# ADR-001 — Merge innovate-or-die v1 and innovation-mode into core protocol v2.0.0

**Date:** 2026-08-19 · **Status:** Draft, pending Ken sign-off · **Supersedes:** both source protocols

## Context

Two forked implementations of the same idea existed:

- **innovate-or-die v1** (public repo, 4-role): innovator / critic / reviser / evaluator with context isolation, a structured critic audit schema, an 8-dimension quality gate (≥4 threshold, one correction loop), and hidden scaffolding. Strong architecture; weak enforcement — no quotas, no distinctness tests, no falsifier standard, so a lazy run can satisfy it.
- **innovation-mode** (private Claude user skill, 8-phase): quotas (10+ assumptions, 30 candidates, ≥5 kills), the lens bank with provocations, the fake-novelty detector (7 named tests), the adversarial checklist, the falsifier standard, and the experiment spec. Strong enforcement; weak architecture — the author self-critiques in the same context, which is the anchoring failure mode the repo's isolation exists to prevent.

The fork is the maintainability bug (same class as `enrich_llm.py` prompt drift). One canonical protocol, v2.0.0, replaces both.

## Decision

**Architecture from v1. Enforcement from innovation-mode.** Specifically:

| Component | Source | Disposition |
|---|---|---|
| 4-role structure + context isolation | v1 | Kept unchanged. Isolation is the load-bearing design choice. |
| Critic audit schema (9 fields) | v1 | Kept; extended to 10 fields — `ideas_to_discard` renamed `kill_list`, `adversarial_findings` added (see D2). |
| 8-dimension evaluator gate, ≥4, one loop | v1 | Kept unchanged. |
| Hidden scaffolding in final answer | v1 | Kept, amended (see D5). |
| "Strong conventional beats weak unconventional" | both | Kept (present in both). |
| Phase 1 quotas: 10+ assumptions real-vs-inherited, 5 reformulations | innovation-mode | → Innovator role. |
| Lens bank + provocations, 8+ lenses | innovation-mode | → Innovator role, `references/lenses.md` carried near-verbatim. |
| 30-candidate quota + sub-quotas + 2 distinctness tests | innovation-mode | → Innovator role. |
| Fake-novelty detector (7 tests) + kill-list + calibration (8–15 of 30) | innovation-mode | → **Critic** role (see D2). |
| Adversarial checklist (9 probes) + falsifier standard | innovation-mode | → Critic role. |
| Asymmetric-selection criteria (Phase 5) | innovation-mode | → **Reviser** role (see D3). |
| "More radical version" questions (Phase 7) | both | → Reviser (already half-present in v1). |
| Experiment spec + solo-operator scale rule | innovation-mode | → `references/experiment-spec.md`, required in final answer. |
| Standing epistemic rules | both | Merged into `principles.md` (near-total overlap). |

## Key decisions and rationale

**D1 — Isolation wins over self-critique.** innovation-mode's Phases 4–6 have the author filter its own output. v2 moves all filtering to the isolated critic. Rationale: an author that knows the filter optimizes for the filter; that is the anchoring failure this protocol exists to defeat. Consequence: the innovator's brief explicitly forbids self-censoring against the detector. Boundary: the workflow orchestrator may name the existence of downstream stages (a critique occurs, a scored gate occurs); the isolation requirement applies to their criteria — detector tests, probe lists, and dimension definitions stay in role files loaded only at their stage.

**D2 — The fake-novelty detector becomes the critic's instrument.** v1's critic already audits `fake_novelty` but gives no operational test. The 7 named tests operationalize it. The kill list becomes a critic output field with the 8–15-of-30 calibration.

**D3 — Selection moves to the reviser.** Someone must choose finalists using the asymmetric criteria (limited downside + cheap validation + large upside + high learning). Not the innovator (premature convergence), not the critic (auditors don't decide). The reviser — which already reopens, compares, and re-ranks — selects.

**D4 — One correction loop, kept.** innovation-mode specifies none; v1's single targeted revision on gate failure is kept. Unbounded loops burn tokens polishing; one bounded loop with named deficiencies is a discipline.

**D5 — Scaffolding hidden, kill list surfaced.** Conflict: v1 hides all internals; innovation-mode publishes the search log as evidence of breadth. Resolution: drafts, audits, and scores stay hidden unless requested; a **compact kill list** (top 5 kills, one line each with reason) appears in the final answer. Rationale: the kill list is user-valuable information ("what was considered and rejected"), not scaffolding; the full search log is available on request.

**D6 — Final answer shape merged.** Lead with the strongest surviving thesis (v1), followed by innovation-mode's structure: reframing · top opportunities with mechanism/failure-reason · most contrarian hypothesis · cheapest high-information experiment (full spec) · compact kill list · what may still be missing. Conventional answers are allowed to win and must be labeled as such.

**D7 — Name and version.** Public name stays `innovate-or-die` (repo and brand exist). Core protocol is semver'd starting **2.0.0**. `innovation-mode` is retired from the Claude project after v2 ships — running both re-forks the merge and invites dual-trigger conflicts.

**D8 — Core stays model-agnostic.** No model names, token budgets, or host-specific syntax in `core/`. Host adaptations (frontmatter, invocation, subagent availability, char limits) live in generated adapters only.

## Rejected alternatives

- **Adopt innovation-mode wholesale, add isolation note** — loses the audit schema and gate; isolation as a "note" is ignored under load.
- **Adopt v1 wholesale, tighten wording** — enforcement by exhortation demonstrably fails; the quotas are what force a real search.
- **Keep both, position as "lite" and "full"** — is the fork, permanently.
- **Two-name rebrand for v2** — discards existing repo history and inbound links for no functional gain.

## Consequences

- Both source protocols become historical; `docs/` retains them for reference.
- The critic's job grows (audit + detector + checklist + kill list); its reference file is the longest. Acceptable: the critic is where the value is created.
- v2 is more token-expensive than v1 (quotas guarantee volume). Mitigation: terse-format rules (one line per candidate) are part of the quota spec, and the evaluator does not reward length.
- Every adapter regenerates from `core/`; hand-edits to generated files are prohibited and CI-guarded.
