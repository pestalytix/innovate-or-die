# Redacted eval transcripts

The raw evidence behind the files in [`evals/results/`](../results/). Published so
a reader can check a reported number against the run that produced it, rather
than taking the results file's word for it.

## What is here

The tree mirrors the working tree's layout — `iteration-<n>/<provider>/<tier>/<slug>/<arm>/`
— plus two side studies that sit outside the iteration structure because they
were not full tier runs:

| Path | What it covers | Behind |
|---|---|---|
| `iteration-1/` | the baseline: claude and codex, workhorse and flagship | the four `2026-08-19-*` and `2026-08-20-*` results files |
| `iteration-2/` | codex workhorse, N=3 majority grading | `2026-08-19-codex-gpt-5.6-sol.md`, `2026-08-20-codex-gpt-5.6-terra.md` |
| `iteration-3/` | codex workhorse, v2.1.0 activation-banner runs | `docs/NOTE-activation-variance.md` |
| `adr002-regression/` | the same case under v2.0.0 and v2.0.1 | `2026-08-19-adr002-regression.md` |
| `grader-variance/` | repeated grading draws over one fixed set of answers | `2026-08-19-grader-variance.md` |

Six artifact kinds are published, by **allowlist** — not by excluding known-bad
names, which would publish whatever a future run happened to leave behind:

- `outputs/response.md` — the answer the model actually returned
- `timing.json` — tokens, duration, resolved model, activation, provenance
- `grading.json` — per-assertion results and the evidence quoted for each
- `trace/stream.jsonl` — the raw Claude event stream, where one exists (3 runs).
  This is the audit trail for an activation negative: it is what makes
  "the `Skill` tool was never called" checkable rather than asserted.
- `trace/stderr.txt` — where one exists

- `judge.json` — per tier: the blind judge's verdict, dimension scores and stated
  reason for every case. The results files quote the winner and the reason; the
  **scores** appear only here.

  What each vintage actually holds, since it is not uniform:

  | Tier | Judging | What the file records |
  |---|---|---|
  | `iteration-1/*` | N=1 | one ballot per case, with its five dimension scores per arm. Nothing was discarded — at N=1 there was nothing to discard. |
  | `iteration-2/codex/workhorse` | N=3 majority | the vote tally (`vote_split`, `votes`, `unanimous`) and **one ballot's scores**. The other two ballots' scores were not retained: **per-ballot scores unavailable for this iteration.** Disagreement is visible as a split tally, not as individual ballots. |

  The `ballots` array and `scores_mean` that `judge.py` writes today postdate
  every judge run in this repo, so no published file carries them yet. Runs
  judged from harness `d4c7269` onward will.

Deliberately **not** published: `benchmark.json` (reproduced verbatim inside each
results file, under "benchmark.json (verbatim)"), `cost-grading-*.json`, and the
working notes.

## What was redacted, and how

By [`evals/runners/redact_transcripts.py`](../runners/redact_transcripts.py),
which does the copy and the redaction in one reproducible step:

```bash
python3 evals/runners/redact_transcripts.py --copy-from evals-workspace --dry-run
python3 evals/runners/redact_transcripts.py --copy-from evals-workspace
```

| Pattern | Replacement |
|---|---|
| `/Users/<name>/…` (any user, with or without a trailing slash) | `/Users/REDACTED/…` |
| `/var/folders/<xx>/<hash>/T/…` (machine temp dir, both encodings) | `/var/folders/REDACTED/T/…` |
| `/tmp/claude-<uid>/…` (scratchpad root, both spellings) | `/tmp/claude-REDACTED/…` |
| `sk-…`, `sk-ant-…`, `sk-proj-…` | `[REDACTED-SECRET]` |
| `Bearer <token>`, `*_API_KEY=<value>` | `[REDACTED-SECRET]` |
| email addresses | `[REDACTED-EMAIL]` |
| init-event host environment (below) | `[REDACTED-HOST-ENV]` |

What that actually removed on this corpus: **174 replacements across 3 of 175
files** — 18 host-environment values, 3 home-directory paths, 129 machine
temp-directory segments and 24 scratchpad user ids. The first two land in the
three `stream.jsonl` init events; the temp-directory and scratchpad paths recur
throughout those same three streams, wherever a tool call named a file. No secret
or email pattern matched anything, before or after.

(21 rather than 24 for the host-environment and home-directory rules, because the
structural rule runs first: it discards the whole `plugins` value, which was
itself carrying one of the two home-directory paths in each file, so the textual
rule then has one path left to fix rather than two.)

### Host environment, stripped

A `stream.jsonl` opens with a `{"type":"system","subtype":"init"}` event that
describes the **machine**, not the run. Six of its values are replaced with
`[REDACTED-HOST-ENV]`:

`session_id` · `uuid` · `plugins` · `skills` · `slash_commands` · `mcp_servers`

They named the operator's installed plugins and skills and the third-party
services connected to that machine. None of it is a credential — `apiKeySource`
is `none` in all three — and none of it matched a secret pattern, which is
exactly why it needed its own rule rather than being caught by the regexes. It
also has no evidentiary role: no claim in any results file rests on which plugins
were installed.

**`plugins`, `skills`, `slash_commands` and `mcp_servers` occur only in the init
event**, so for those four the value is gone from the file entirely.
**`session_id` and `uuid` also appear on every subsequent event line**, where this
rule does not reach: the rule is scoped to the init event, so those two survive
elsewhere in the stream. They are a per-session random UUID and a per-event random
UUID — no credential, and meaningless outside the machine that generated them.

`claude_code_version`, `model` and `tools` are **kept**, because those do carry
evidence. `tools` especially: it is what makes *"the `Skill` tool was never
called"* checkable against the stream instead of merely asserted, which is the
whole reason the streams are published.

The rule is structural — it parses the event and replaces whole values — and
rewrites a line only when a value actually changed, so in each of the three files
exactly one line differs from the working copy and every other byte is identical.

The script re-reads every file **from disk** after writing and re-scans it; a
surviving match exits 1. It is idempotent, so a second run reports zero
replacements and is a cheap way to verify the committed tree. Secret shapes it
does *not* handle — AWS `AKIA…`, Google `AIza…`, GitHub `ghp_…` — are scanned for
and reported as misses with an exit code of 2, so an unhandled shape fails loudly
instead of passing quietly. None occur here.

### What the redaction does *not* remove

Stated rather than left to be discovered:

- **`session_id` and `uuid` on non-init event lines**, as described above — the
  init-event rule is scoped to the init event by design, and these two fields
  recur on every line of a stream.
- **The operator's business domain, in model reasoning.** In
  `iteration-1/claude/flagship/eval-route-density/with_skill/trace/stream.jsonl`,
  the model wrote the operator's email domain into its own Stage 0 assumptions and
  carried it through its subagent fan-out. It is not redacted because it is not
  metadata — it is the reasoning under test, and removing it would damage the
  evidence. It does **not** appear in that run's delivered answer. See the
  confound note below.
- **Model reasoning generally.** Nothing inside an answer, a grading rationale or
  an assistant turn is rewritten. Only host metadata and the patterns tabled
  above are touched.

### Known confound: uncontrolled host context in the flagship pair

The prompt for `eval-route-density` mentions no operator, domain or data
warehouse. **Both arms of the flagship pair drew on the host machine anyway**,
and they drew on different parts of it:

| Run | What leaked in | Reached the delivered answer? |
|---|---|---|
| `iteration-1/claude/flagship/eval-route-density/with_skill` | the operator's account email domain, recorded in its Stage 0 assumptions and passed through its subagent fan-out (17 occurrences across intermediate turns) | **No** — confined to the stream; the `result` event and `response.md` contain none of it |
| `iteration-1/claude/flagship/eval-route-density/without_skill` | a `BigQuery` dataset connected to the host as an MCP server, which the model offered to query | **Yes** — *"If you've got service history in BigQuery, I can pull the actual numbers"* |

Measured scope, by scanning all 57 `response.md` files across both arms and every
tier plus all three event streams for ten identifying terms: **these two runs
only.** No other Claude run shows it.

**On Codex: no leakage observed — but absence is unobservable there, not
established.** Codex exposes no event stream, so the scan could only read
delivered answers; the intermediate reasoning that carried the leak on the Claude
side has no equivalent artifact to search. A genuinely clean Codex lane and an
unmeasurable one look identical from outside. Read the Codex result as "nothing
found in what can be seen", not as "nothing there".

Why it matters: the paired design holds prompt, model and workspace constant, and
`run_evals.py`'s `assert_uncontaminated` checks that the *skill* is out of scope
for the control. Neither controls the host's ambient account context. Here it
entered **both** arms, unequally and in different forms, so it does not cancel.

What it does and does not touch: assertion grades score output structure and are
unaffected. The blind judge scored the delivered answers — where the treatment's
leak is absent and the control's is present — so the `eval-route-density` verdict
carries that asymmetry.

## Relationship to `evals-workspace/`

[`evals-workspace/`](../../README.md) remains the **local-only working tree** and
stays gitignored. It is where runs land, where the graders and the judge read
from, and it holds intermediate state that is not evidence. This directory is the
published, redacted slice of it — a derived artifact, not the working copy. Do
not edit files here by hand; re-run the script.

**From iteration 3 onward, transcripts ship with each results file.** Iterations
1 and 2 were published retroactively, after external review #2 (2026-08-20).
