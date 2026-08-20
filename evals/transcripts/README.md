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

Five artifact kinds are published, by **allowlist** — not by excluding known-bad
names, which would publish whatever a future run happened to leave behind:

- `outputs/response.md` — the answer the model actually returned
- `timing.json` — tokens, duration, resolved model, activation, provenance
- `grading.json` — per-assertion results and the evidence quoted for each
- `trace/stream.jsonl` — the raw Claude event stream, where one exists (3 runs).
  This is the audit trail for an activation negative: it is what makes
  "the `Skill` tool was never called" checkable rather than asserted.
- `trace/stderr.txt` — where one exists

Deliberately **not** published: `benchmark.json` and `judge.json` (both are
reproduced verbatim or in full inside the results files themselves),
`cost-grading-*.json`, and the working notes.

## What was redacted, and how

By [`evals/runners/redact_transcripts.py`](../runners/redact_transcripts.py),
which does the copy and the redaction in one reproducible step:

```bash
python3 evals/runners/redact_transcripts.py --copy-from evals-workspace --dry-run
python3 evals/runners/redact_transcripts.py --copy-from evals-workspace
```

| Pattern | Replacement |
|---|---|
| `/Users/<name>/…` (any user) | `/Users/REDACTED/…` |
| `sk-…`, `sk-ant-…`, `sk-proj-…` | `[REDACTED-SECRET]` |
| `Bearer <token>`, `*_API_KEY=<value>` | `[REDACTED-SECRET]` |
| email addresses | `[REDACTED-EMAIL]` |
| init-event host environment (below) | `[REDACTED-HOST-ENV]` |

What that actually removed on this corpus: **21 replacements across 3 of 171
files** — 18 host-environment values and 3 home-directory paths, all in the three
`stream.jsonl` init events. No secret or email pattern matched anything, before
or after.

(21 rather than 24 because the structural rule runs first: it discards the whole
`plugins` value, which was itself carrying one of the two home-directory paths in
each file, so the textual rule then has one path left to fix rather than two.)

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

- **Temporary paths.** `cwd` and `memory_paths` still carry the per-run temp
  directory (`/private/var/folders/…/iod-with_skill-<random>`). The username
  within them is redacted; the run-scoped random suffix is not.
- **`session_id` and `uuid` on non-init event lines**, as described above — the
  init-event rule is scoped to the init event by design, and these two fields
  recur on every line of a stream.
- **The operator's business domain, in model output.** In
  `iteration-1/claude/flagship/eval-route-density/with_skill/`, the model wrote
  the operator's email domain into its own Stage 0 assumptions and built a ranked
  opportunity on it. It is not redacted because it is not metadata — it is the
  reasoning under test, it is discussed in the results narrative, and removing it
  would damage the evidence. See the note on uncontrolled context below.
- **Model reasoning generally.** Nothing inside an answer, a grading rationale or
  an assistant turn is rewritten. Only host metadata and the patterns tabled
  above are touched.

### Known confound: uncontrolled context in one flagship run

The prompt for `eval-route-density` does not mention the operator or any domain.
The flagship `with_skill` run nonetheless recorded *"user email domain:
pestalytix.com"* among its Stage 0 assumptions, having taken it from the host
environment rather than the prompt, and one of its ranked opportunities is built
on that inference. The paired design holds the prompt, model and workspace
constant; it does not hold the host's ambient context constant, and here that
context entered one arm of one pair. It does not affect the assertion grades —
those score output structure — but any reading of that run's *content* against
its control should account for an input the control did not have.

## Relationship to `evals-workspace/`

[`evals-workspace/`](../../README.md) remains the **local-only working tree** and
stays gitignored. It is where runs land, where the graders and the judge read
from, and it holds intermediate state that is not evidence. This directory is the
published, redacted slice of it — a derived artifact, not the working copy. Do
not edit files here by hand; re-run the script.

**From iteration 3 onward, transcripts ship with each results file.** Iterations
1 and 2 were published retroactively, after external review #2 (2026-08-20).
