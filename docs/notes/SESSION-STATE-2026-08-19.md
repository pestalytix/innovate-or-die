# Session state — 2026-08-19/20 (last updated 2026-08-20, v2.1.0 release)

Working state, standing constraints, and traps, written so the next session (human or
agent) can resume without re-deriving any of it. Session insurance and decision record.

---

## Where things stand

**Phases A–D complete. Phase E prep complete; the flip has not happened.**

| | state |
|---|---|
| Protocol version | **v2.1.0** (ADR-004 activation banner; v2.0.2 was ADR-003) |
| Repo visibility | **PUBLIC**, released |
| CI | `.github/workflows/check.yml` — `assemble.py --check` **and `pytest`** on push, green |
| Generated trees | 42 files from `core/`, committed, drift-guarded |
| Evals | iteration-1 (v2.0.0, 2 providers) + iteration-2 (v2.0.1, Codex workhorse) + iteration-3 (v2.1.0, Codex workhorse, `with_skill` only — banner emission) |
| Instruction headroom | **301 chars** of the 8,000 cap (was 33 before ADR-004's dedup) |

**Everything outside `core/`, `docs/`, `evals/` and `build/` is generated.** Hand-edits
are reverted by the next `assemble.py` run and caught by CI.

---

## Standing constraints — do not violate without an explicit new decision

1. **Claude eval lanes are PAUSED** (weekly quota protection). No `claude -p` eval run
   — workhorse, flagship, or diagnostic — without explicit go-ahead. **Grading and
   judging are the sole authorized exception.** Claude workhorse is a **4-case** tier
   (dental dropped by predicate); Claude flagship was replaced by a single envelope
   probe per the MODEL_POLICY scope amendment.
2. **Grading is metered on `cost_usd`, not tokens**, ceiling **$25.00** per batch. The
   token metric overstates many-small-calls workloads by >10x (see traps). Both figures
   are logged; only cost gates.
3. **Results files are generated artifacts.** `evals/runners/report.py` is the single
   generator; it enforces a required-section manifest re-read from disk. **Never
   hand-edit a results file** — regenerate. Adding a section means adding it to
   `report.py` *and* its manifest.
4. **Iteration-1 files are the v2.0.0 record: annotate, never re-grade.** Re-grading
   replaces one draw with another, no more correct, and silently rewrites a published
   baseline.
5. **Never blend protocol versions in a tier mean.** Every run carries `skill_version`.
   Cross-version comparisons get their own document.
6. **Assertions are authored after observation**, never in advance, and provenance is
   recorded in `evals/evals.json`.
7. **Activation claims must state their method**: `observed` (Skill tool call seen),
   `heuristic` (output markers), or `inferred` (backfilled). Never present inferred as
   measured.

---

## Phase E — remaining sequence

Author's items are marked; the rest are executable.

1. **Flip the repo public.** Everything else depends on this; install paths 404 while
   private.
2. **Verify install end-to-end from a clean machine**: `/plugin marketplace add
   pestalytix/innovate-or-die` then `/plugin install innovate-or-die@pestalytix`.
   Gate E is a clean-machine test on >=2 hosts.
3. **skills.sh listing** — *deferred deliberately*: no authoritative submission
   procedure was found. Read the mechanism from skills.sh itself post-flip.
4. **Publish the Custom GPT and the Gem** from `adapters/web/*-instructions.md` +
   `*-knowledge.md`. *(author — personal accounts, not scriptable)*
5. **Cross-link** repo <-> kenpendergast.com. *(author)*
6. **Retire `innovation-mode`** from the Claude project — only after the published
   skill is confirmed working there.

Done in prep: docs pre-publication pass, README amendments, knowledge-file retrieval
test (PASS on Gemini Gem), install-path audit (no auth-assuming URLs).

---

## Open backlog

**Blocked on the author**
- **Gemini leg** — CLI installed and authenticated, but `security.auth.selectedType`
  is `gemini-api-key` and those AI Studio prepay credits are **depleted (429)**.
  Switching to the **Code Assist** path should use subscription quota instead. Runner is
  written and wired but **UNVALIDATED** — the response envelope's field names were never
  observed, so it digs defensively and records `parse_confidence`. Also needs the exact
  `/model` strings; MODEL_POLICY pins are **PROVISIONAL and unusable** until read from
  a live `/model`.
- **Claude iteration-2 leg** — waits on the quota window.
- **Banner-vs-Skill-tool validity check (ADR-004 regression test 3)** — waits on the
  quota window. **Pre-registered before the runs, per the H2 discipline:** on Claude,
  where an observed `Skill` tool call is independent ground truth, record for every
  `with_skill` run both *activated* (tool call) and *banner present*. The prediction
  on record is that **banner presence equals observed activation**; the cell that
  matters is activated-but-no-banner, which is the banner's false-negative rate. The
  ADR's stated mechanism predicts it lands well above the 71% compliance seen on
  Stage 6 item 5, because the banner is item 0 and carries no generation load.
  Run it as `--arm with_skill` on the workhorse tier; the control arm cannot emit a
  banner and adds nothing here. Until it runs, the banner's false-negative rate is
  measured on Codex only, where there is **no ground truth to check it against**.

**Substantive open questions**
- **Activation mechanism is unknown.** Three hypotheses falsified. Next step is the
  **observe-and-abort** instrument: kill the run the moment a `Skill` call is seen (or
  after a short no-activation window), measuring activation at ~1% of a full run's cost
  and making a 20+ prompt survey affordable. **Any fourth hypothesis must be
  pre-registered before its test runs.**
- **Unstable assertions** — the 6x-split causal-mechanism assertion is the most
  load-bearing in the suite; mechanize or reword it and the 4x-split actionability one.
- **Thoroughness vs actionability** — judge preferred controls for concreteness on some
  flagship cases. Iteration-2 assertions exist to test it; not yet analysed.
- **Web instructions headroom: 126 chars** under ChatGPT's *confirmed hard* 8,000 cap.
  The next core edit over ~126 chars breaks the primary web install path and hard-fails
  `--check`.
- **Gemini Gem cap** is a lower bound only (>= ~7.9k); upper bound untested.
- **Consumer (non-M365) Copilot** support: inconclusive, re-check after Microsoft's app
  unification.
- **Low priority:** the web knowledge file carries repo-relative paths
  (`../references/lenses.md`) that are meaningless on web hosts. Cosmetic.

---

## Known traps — each cost real time here

1. **Codex writes its banner to stderr.** `codex exec` puts the answer on **stdout** and
   `model:` / `tokens used` on **stderr**. Parsing the banner off stdout yields
   `resolved_model: UNKNOWN` and trips the mismatch guard on runs that actually
   succeeded. A smoke test using shell `2>&1` **masks this** — capture the streams
   separately.
2. **`claude -p` silently resolves to Haiku.** With no `--model`, an unpinned run was
   observed resolving to `claude-haiku-4-5-20251001`. Always pin, always record the
   **resolved** id from `modelUsage` — and note Claude Code reports **several** models
   per run (utility calls alongside the pinned one), so match the requested family
   first rather than taking the highest-token entry.
3. **`str.replace` fails silently.** It returns the string unchanged when the anchor
   does not match. Four results sections were dropped this way while the writes
   succeeded and success was reported. **Assert the anchor count before replacing, and
   read the artifact back after writing.** This is why `report.py` has a completeness
   gate.
4. **The token metric overstates small calls by >10x.** A cold `claude -p` call carries
   ~85,000 tokens of `cacheCreation` — harness scaffolding, charged per invocation,
   near-independent of payload. One grading call: 88,424 tokens / $0.52, of which 96%
   was cache. **Run small calls serially and back-to-back** (consecutive calls hit
   `cacheRead`: 6x cheaper per call) and **budget on cost, not tokens**.
5. **`pgrep -f "<pattern>"` matches other shells containing the pattern**, including
   your own monitoring commands and sibling waiters built the same way. Two waiters
   each blocked on the other's command-line text and deadlocked. **Watch a log file for
   a completion marker instead of polling `pgrep`.**
6. **Background driver budget counters only see their own runs.** A standalone run
   launched outside the driver was invisible to its cap. Compute the true total from
   the workspace, not from the driver's tally.

---

## Reproducing the evals

```bash
python3 evals/runners/run_evals.py --provider <p> --tier <t> --model <full-string> --iteration <n>
python3 evals/runners/grade.py     --provider <p> --tier <t> --iteration <n> --votes 3
python3 evals/runners/judge.py     --provider <p> --tier <t> --iteration <n> --votes 3
python3 evals/runners/aggregate.py --provider <p> --tier <t> --iteration <n>
python3 evals/runners/report.py    --provider <p> --tier <t> --iteration <n>
```

`evals-workspace/` is gitignored and local-only; `evals/evals.json` plus the runners
regenerate it. The results files in `evals/results/` are the durable record.
