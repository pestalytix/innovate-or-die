# Grader variance — LLM-graded assertions are nondeterministic

**Measured 2026-08-20**, accidentally: iteration-1's Codex workhorse tier was
re-graded to pick up an unrelated re-run, and the grades came back different. Same
response files, same assertions, same pinned grader (`claude-sonnet-5`), two draws.

This document exists because the finding changes how every other number in the eval
history should be read. Its companion is
[`2026-08-20-judge-validity-dental.md`](2026-08-20-judge-validity-dental.md), which
records the same class of problem in the *pairwise judge* rather than the assertion
grader.

## The two draws

| case | draw 1 (committed) | draw 2 | shift |
|---|---|---|---|
| `eval-route-density` | −0.4285 | −0.4285 | — |
| `eval-saas-onboarding-churn` | +0.2857 | +0.2857 | — |
| `eval-dental-no-shows` | +0.2500 | +0.3750 | +0.125 |
| `eval-municipal-water-loss` | +0.1428 | 0.0000 | −0.143 |
| `eval-bookstore-events` | +0.4285 | +0.1429 | **−0.286** |
| **tier deployed delta** | **+0.1357** | **+0.0750** | **−0.061** |

Nothing about the inputs changed between draws.

## Why it matters

The tier mean moved **±0.061 against a +0.136 headline** — roughly half the size of
the effect being reported. A single case moved 0.286 on its own. Any comparison
between tiers, versions, or providers built on one grading draw is comparing two
samples from overlapping distributions and calling the difference a result.

The pre-existing statistical-modesty banner said "one run per case, per arm". That
was true and insufficient: it assumed **grading** was deterministic. There are two
noise sources, not one — model output variance *and* grader variance — and only the
first was disclosed.

## Mechanical vs LLM stability

The two unchanged cases are the ones whose assertions are dominated by mechanical
checks. Every case that moved did so on LLM-graded assertions.

- **Mechanical checks** (`delivers_answer`, `falsifier_with_number`,
  `experiment_spec_complete`, `kill_list_min_5`, `conventional_winner_labelled`) are
  pure Python over the response text: deterministic by construction, identical across
  draws, free to run.
- **LLM-graded assertions** (mechanism quality, fact/assumption separation, the
  per-case ones) are model judgements and vary run to run.

This is a strong argument for mechanizing assertions wherever the check can be
expressed in code, independent of cost.

## Methodology change forced by this

From **iteration-2 onward**:

1. **N=3 independent grading passes per LLM assertion**, with the grade set by
   **per-assertion majority vote**.
2. **Vote splits recorded** in `grading.json` (`vote_split`, `llm_votes_per_assertion`).
3. **2-1 splits flagged `unstable`** and collected into `unstable_assertions` — that
   list is the mechanization/rewording candidate queue. An assertion that cannot be
   graded consistently is a defective assertion, not a defective answer.
4. **Blind judge likewise N=3 majority**, with `vote_split` and `unanimous` recorded
   per pair.

Majority voting suppresses the noise; recording the splits measures it rather than
hiding it.


## Connection to iteration-2's unstable-assertion list

Iteration-2's N=3 grading recorded which assertions the three passes disagreed on. The
most frequent by a clear margin — **6 split votes across 10 graded arms** — is:

> *"At least one proposed opportunity is supported by a named causal mechanism rather
> than an analogy or a gesture."*

That is the **most load-bearing assertion in the suite**: it is the one that most
directly tests what the protocol claims to add over a bare answer, and it appears in
every case. An assertion that central being the least reliably gradeable **strengthens
the single-draw caveat on every iteration-1 LLM-graded figure** — the noise measured
above is not spread evenly, it concentrates in the assertion carrying the most weight.

Second most unstable (4 splits) is one of the three *new* actionability assertions,
which matters before it anchors any conclusion about the thoroughness/actionability
trade-off it was written to test.

Both are at the top of the mechanization/rewording queue.

## Status of existing results

**Iteration-1 committed files are annotated, never re-graded.** Their grades are
single draws and are labelled as such in each file. Re-grading them would replace one
draw with another draw — no more correct, and it would silently rewrite a published
baseline.

**Draw 2 is preserved as evidence**, not promoted to anyone's grade:
`evals-workspace/grader-variance/`. Since that workspace is gitignored, the table
above is the durable record.

## What is not affected

Findings that rest on **mechanical, categorical** outcomes are outside this noise
band — most importantly the ADR-002 regression, where `delivers_answer` flipped
FAIL→PASS deterministically and the case delta swung 0.857, an order of magnitude
larger than the largest observed grader shift. See
`2026-08-19-adr002-regression.md`.

Activation findings are also unaffected: activation is observed from the stream, not
graded.
