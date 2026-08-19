# Changelog

All notable changes to the core protocol. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the protocol is
versioned with [semver](https://semver.org/). Protocol changes require an ADR
and a version bump.

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
