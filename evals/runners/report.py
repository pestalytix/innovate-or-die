#!/usr/bin/env python3
"""Emit evals/results/YYYY-MM-DD-<provider>-<resolved-model>.md.

**This is the single generator of results files.** Results are generated
artifacts, not hand-edited documents: every section below is emitted from data
in the workspace, and a completeness manifest is checked against the file as
re-read from disk after writing. If any required section is missing, the file is
deleted and the run fails loudly.

That assertion exists because an earlier version of this pipeline used unguarded
`str.replace` to graft sections on after the fact. `str.replace` returns the
string unchanged when its anchor does not match, so four sections were silently
dropped while the write itself succeeded. Never trust a write; verify the artifact.

The workspace is gitignored, so the results file is the durable public record and
must be self-sufficient.

## Method statements are version-gated. Always.

**Every sentence in this file that describes a METHOD -- how answers were graded,
how the judge was run, how presentation or arm order was chosen, how activation
was detected -- must be gated on the iteration or protocol version from which
that method applies.** Never write the current method as unconditional prose.

The reason is specific to this generator being the only writer. A results file is
regenerated whenever anything else about it changes: a corrected banner, a new
annotation, a derived line that used to be a literal. Each regeneration re-emits
every sentence from TODAY's source. So an ungated method sentence does not merely
go stale -- it is silently rewritten, and a file recording a 2026-08-19 run comes
to assert a method that did not exist until 2026-08-20. The numbers stay honest
while the prose describing how they were produced quietly becomes false, and
nothing in the completeness gate can catch it, because the section is present and
the sentence is well-formed.

Worked example, `judge_section()`: presentation order was index alternation
through iteration 2 and per-ballot randomization from iteration 3. The function
takes `iteration` and selects the sentence accordingly. Regenerating the
iteration-1 file for an unrelated reason had already begun writing "drawn
independently per ballot from a seeded RNG" over a run that alternated by index;
the gate is what stops that. `banners()` does the same for the version-span and
grading-method text, and for annotations scoped to one lane.

The test for a new method sentence is not "is this true?" but "is this true of
every run this generator can be pointed at?" If not, gate it.
"""
from __future__ import annotations
import argparse, datetime as dt, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


# ----------------------------------------------------------------- sections

def tier_skill_versions(base) -> set[str]:
    """Every distinct `skill_version` recorded under a tier.

    Read from the runs themselves rather than assumed. The banner below asserts
    that one protocol version produced every number in the file; asserting it
    from a literal meant the sentence stayed true-looking across a version bump
    while silently becoming false. A run with no recorded version counts as
    UNKNOWN so it shows up in the refusal instead of vanishing from the set.
    """
    return {str(json.loads(t.read_text()).get("skill_version") or "UNKNOWN")
            for t in sorted(base.rglob("timing.json"))}


def banners(args, L, skill_version: str | None = None):
    L += ["> **Version span.** Iteration-1 spans **two protocol versions**: runs before "
          "the ADR-002 Stage 0 fix are **v2.0.0**, runs after it are **v2.0.1**. Each arm "
          "below is labelled. Cross-version comparisons within this iteration are "
          "confounded and flagged where they occur." if args.iteration == 1 else
          f"> **Single protocol version.** Every run in this iteration used "
          f"**v{skill_version}**, so within-iteration comparisons are clean.", ""]
    L += ["> **Statistical modesty.** Five cases, **one run per case, per arm**. Every "
          "number here is **directional only** — no repeated trials of the runs "
          "themselves, so no variance estimate and no significance. `stddev` across cases "
          "measures case-to-case spread, not run-to-run stability. Treat differences of a "
          "few points as indistinguishable from noise, and win/loss tallies as anecdote. "
          "The qualitative verdicts and named findings carry more weight than any mean "
          "here.", ""]
    if args.iteration == 1 and args.provider == "claude" and args.tier == "workhorse":
        L += ["> **Aggregation corrected in v2.0.2 per external review finding 5.** The "
              "figures in this file were previously computed over **unmatched** arms: "
              "`eval-dental-no-shows` contributed a `with_skill` run with no control, so "
              "a 5-case `with_skill` mean was subtracted from a 4-case control mean. The "
              "tier is now computed over **matched valid pairs only** and this file has "
              "been regenerated. What moved: `with_skill` pass rate 0.53 → 0.54, delta "
              "0.14 → 0.15, `with_skill` tokens 299,802 → 364,742, token delta 259,511 → "
              "324,451, n 5 → 4. The narrative below already described this tier as "
              "4-case; the numbers now agree with it. No run was re-executed and no "
              "grade was re-drawn.", ""]
    if args.iteration == 1 and args.provider == "claude":
        L += ["> **Uncontrolled context (found 2026-08-20).** Both arms of "
              "`eval-route-density` on the **flagship** tier drew on the host "
              "machine's context — information the prompt did not supply and the "
              "paired design does not hold constant. **`with_skill`** recorded the "
              "operator's account email domain among its Stage 0 assumptions and "
              "carried the inference through its subagent fan-out; it stayed in the "
              "intermediate turns and is **not** in the delivered answer. "
              "**`without_skill`** offered to query a `BigQuery` dataset connected "
              "to the host as an MCP server, and that offer **is** in its delivered "
              "answer. So `clean context` held for neither arm of this pair, and "
              "the two were contaminated **differently**, not equally — this does "
              "not cancel out. Assertion grades score output structure and are "
              "unaffected. The blind judge read the delivered answers, so the "
              "`eval-route-density` verdict should be read knowing the control's "
              "answer carries a host-derived offer the treatment's does not. No "
              "other Claude run in any tier shows this. No Codex run shows it "
              "either, but Codex exposes no event stream, so absence there is "
              "unobservable rather than established. Evidence: "
              "[`evals/transcripts/README.md`]"
              "(../transcripts/README.md#known-confound-uncontrolled-host-context-in-the-flagship-pair).", ""]
    if args.iteration == 1:
        L += ["> **Post-baseline annotation.** LLM-graded assertions were later measured "
              "nondeterministic (see `2026-08-19-grader-variance.md`); the grades in this "
              "file are **single draws**, not replicated measurements. This file is the "
              "v2.0.0 record: annotated, never re-graded.", ""]
        if args.provider == "codex" and args.tier == "workhorse":
            L += ["> **ADR-002 regression measured post-baseline** on "
                  "`eval-route-density`; see `2026-08-19-adr002-regression.md`. "
                  "Deliberately not folded into the tier means here — that would blend "
                  "protocol versions.", ""]
    else:
        L += ["> **Grading method.** LLM-graded assertions use **N=3 independent passes "
              "with per-assertion majority vote**; split (2-1) votes are recorded as "
              "`unstable` and listed below. Introduced after grader nondeterminism was "
              "measured — see `2026-08-19-grader-variance.md`.", ""]
    L += ["> **Reproducibility.** The redacted raw transcripts behind this file are "
          "published under `evals/transcripts/` — per-run `response.md`, "
          "`timing.json`, `grading.json` and, where one exists, the raw "
          "`trace/stream.jsonl`. `evals-workspace/` remains the **local-only "
          "(gitignored)** working tree; `evals/evals.json` plus `evals/runners/` "
          "regenerate it, and `evals/runners/redact_transcripts.py` derives the "
          "published copy from it.", ""]


def paired_design_line(bench, n_cases: int) -> str:
    """State the pairing that actually held, not the one the design intended.

    "every case ran twice" was unconditional prose sitting directly above tables
    computed over matched pairs only. Whenever a pair was dropped the header
    contradicted the exclusions listed later in the same file.
    """
    pr = bench.get("pairing")
    if not pr:
        return "Paired design; pairing metadata absent in this benchmark.json."
    used, excluded = pr.get("pairs_used") or [], pr.get("excluded_pairs") or []
    if len(used) == n_cases and not excluded:
        return ("Paired design: every case ran twice, with and without the skill, "
                "same prompt, same model, clean context. The delta is the result.")
    return (f"Paired design: {len(used)} of {n_cases} cases have a matched valid "
            "pair (see exclusions under Two deltas).")


def scope_section(args, L):
    """What these numbers are evidence OF -- stated before any of them are read.

    Added after external review. The distinction is not a hedge: the assertions
    are derived from the protocol's own output spec, so a high pass rate says
    the protocol ran, not that the answer is good.
    """
    L += ["## What this measures", "",
          "**Protocol compliance and cost, not independent idea quality.** Three "
          "structural reasons, each of which caps what any number below can support:",
          "",
          "1. **The assertions derive from the protocol's own output spec.** "
          "`falsifier_with_number`, `experiment_spec_complete`, `kill_list_min_5` and "
          "the rest test whether the answer has the shape this skill mandates. An arm "
          "running the skill is being scored against its own instructions, so a "
          "positive delta means *the protocol executed*, not *the reasoning improved*.",
          "2. **The blind judge's dimensions mirror the protocol's evaluator.** "
          "non-obviousness, mechanism, testability, honesty and usefulness are close "
          "to the gate criteria in `roles/evaluator.md`. Two instruments sharing a "
          "rubric with the thing they measure are not independent of it.",
          "3. **Iteration-2 is in-sample.** Its additional assertions were authored "
          "after reading iteration-1 outputs, and the cases are the same five. "
          "Measurement on observed cases is a consistency check, not a held-out test.",
          "",
          "Nothing here establishes that the protocol produces better decisions, or "
          "that a reader acting on its output does better than one acting on the "
          "control's. That experiment has not been run — see "
          "`docs/NOTE-efficacy-roadmap.md` for what it would take.", ""]


def deltas_section(bench, L):
    dl = bench.get("deltas") or {}
    if not dl:
        return
    L += ["### Two deltas", "", "| Delta | Mean | n | Meaning |", "|---|---|---|---|",
          f"| **deployed** | {dl['deployed']['mean']} | {dl['deployed']['n']} | "
          f"{dl['deployed']['meaning']} |",
          f"| **per-activation** | {dl['per_activation']['mean']} | "
          f"{dl['per_activation']['n']} | {dl['per_activation']['meaning']} |", "",
          (f"Excluded from per-activation: "
           f"`{', '.join(dl['excluded_from_per_activation'])}` — the skill did not fire, "
           "so those arms are baseline runs."
           if dl.get("excluded_from_per_activation") else
           "No genuine non-activations in this tier, so the two deltas are **identical**; "
           "the gap between them is the activation-reliability signal and here it is "
           "**0.000**."), "",
          "Per case (deployed): " +
          ", ".join(f"`{k}` {v:+.3f}" for k, v in dl["deployed"]["per_case"].items()), ""]
    pr = bench.get("pairing")
    if pr:
        L += [f"Computed over **matched valid pairs only** ({len(pr['pairs_used'])}): "
              + ", ".join(f"`{s}`" for s in pr["pairs_used"]) + ".", ""]
        if pr["excluded_pairs"]:
            L += ["Pairs excluded, with reasons:", ""]
            for e in pr["excluded_pairs"]:
                why = "; ".join(f"{a}: {', '.join(e[a])}" for a in
                                ("with_skill", "without_skill") if e[a])
                L.append(f"- `{e['slug']}` — {why}")
            L += ["", f"_{pr['note']}_", ""]


def judge_section(jdoc, L, iteration: int = 1):
    if not jdoc:
        return
    verdicts = jdoc.get("verdicts", jdoc if isinstance(jdoc, list) else [])
    if not verdicts:
        return
    L += ["### What the judge actually said", "",
          f"Judge model: requested `{jdoc.get('judge_model_requested')}`, resolved "
          f"`{', '.join(jdoc.get('judge_model_resolved') or ['unknown'])}`.", "",
          f"> **Limitation.** {jdoc.get('limitation','')}", "",
          "The verdict *text* is the finding. Read the reasoning, not the tally.", ""]
    for v in verdicts:
        split = f" _(votes: {v['vote_split']})_" if v.get("vote_split") else ""
        L.append(f"- **{v['slug']}** → *{v['winner_arm']}*{split} — {v['reason']}")
    w = sum(1 for v in verdicts if v["winner_arm"] == "with_skill")
    o = sum(1 for v in verdicts if v["winner_arm"] == "without_skill")
    # Per-ballot randomization landed for iteration 3. Describing an iteration-1
    # or -2 judge run with it would put a false method statement into a
    # historical file the moment that file is regenerated for any other reason.
    method = ("presentation order drawn independently per ballot from a seeded "
              "RNG, so any residual alignment between position and arm is chance "
              "rather than design; the order each ballot saw is recorded in "
              "`presented_first`" if iteration >= 3 else
              "presentation order alternating per case — index alternation, not "
              "randomization: it removes the crudest confound but fixes one order "
              "per case. Randomized per ballot from iteration 3 onward")
    L += ["", f"(Tally for completeness only: with_skill {w}, without_skill {o}, other "
          f"{len(verdicts)-w-o}. **At n=5 with one run per case this count is noise and "
          f"carries no claim.** Answers were shown as 'A'/'B' with {method}.)", ""]


def opus_section(L):
    """Flagship envelope probe — claude only, iteration-1."""
    t = load(ROOT / "evals-workspace/iteration-1/claude/flagship/eval-route-density/"
                    "with_skill/timing.json")
    if not t:
        return
    W = ROOT / "evals-workspace/iteration-1/claude/workhorse/eval-route-density"
    a = load(W / "with_skill-ORIGINAL-inferred/timing.json")
    b = load(W / "with_skill/timing.json")
    # The probe is one-armed, but a control run for the same case DOES exist on
    # disk. Saying "with_skill only" without saying so read as "no control was
    # run", which is a different claim -- and the uncontrolled-context banner
    # above names that very run, so the file contradicted itself.
    c = load(ROOT / "evals-workspace/iteration-1/claude/flagship/eval-route-density/"
                    "without_skill/timing.json")
    control = ((f" A `without_skill` arm for this case **does exist on disk** — "
                f"`{c['resolved_model']}`, v{c.get('skill_version','?')}, "
                f"{c['total_tokens']:,} tok, "
                + ("non-activated, as a control should be" if c.get("activated") is False
                   else f"activated={c.get('activated')}")
                + " — but it is **excluded from the probe by design**: the probe asks "
                  "whether the flagship tier carries the protocol at all, which is a "
                  "one-arm question, and its figures are not aggregated with any tier. "
                  "It is the run named in the uncontrolled-context banner above.")
               if c else "")
    L += ["## Opus envelope probe (flagship, n=1, not aggregated)", "",
          "The 10-run flagship tier was replaced by a single envelope probe (MODEL_POLICY "
          "scope amendment). One case, `with_skill` only, `claude-opus-5`, **default "
          "effort — the deployed condition on a Max plan**, so the result carries the "
          "upward-compatibility claim. **It completed**, so the medium-effort mitigation "
          "arm was not run." + control, "",
          "| | value |", "|---|---|",
          f"| resolved model | `{t['resolved_model']}` |",
          f"| skill version | **v{t.get('skill_version','?')}** |",
          f"| effort | {t.get('effort')} |",
          f"| tokens | {t['total_tokens']:,} |",
          f"| duration | {t['duration_ms']//1000:,}s ({t['duration_ms']/60000:.1f} min) |",
          f"| turns | {t.get('num_turns')} |",
          f"| cost | ${t.get('cost_usd',0):.2f} |",
          f"| activation | {t.get('activation_method')} |",
          f"| tools | `{json.dumps(t.get('tools'))}` |", "",
          "`Agent`x3 is three isolated subagents — ADR-001 D1's isolation executing as "
          "designed. `WebSearch`x4 is the protocol gathering external evidence where "
          "load-bearing facts were missing, which `principles.md` requires and which no "
          "other run in the baseline did. This is the protocol at full fidelity: 24.5 "
          "minutes and $4.84 for one question.", "",
          "### Cost variance caveat — the same prompt, three runs", "",
          "| run | skill version | tokens | duration | turns |", "|---|---|---|---|---|"]
    if a:
        L.append(f"| sonnet, before the pause (inferred activation) | v{a.get('skill_version')} "
                 f"| {a['total_tokens']:,} | {a['duration_ms']//1000}s | — |")
    if b:
        L.append(f"| sonnet, repeat (observed) | v{b.get('skill_version')} | "
                 f"{b['total_tokens']:,} | {b['duration_ms']//1000}s | {b.get('num_turns')} |")
    L += [f"| **opus, default effort (observed)** | **v{t.get('skill_version')}** | "
          f"**{t['total_tokens']:,}** | **{t['duration_ms']//1000}s** | {t.get('num_turns')} |", "",
          "**Version confound.** The two sonnet runs are *not* a clean repeat measurement: "
          "the first ran v2.0.0 and the second v2.0.1, so the token difference confounds "
          "run-to-run variance with the ADR-002 change. Only the sonnet-v2.0.1 vs "
          "opus-v2.0.1 pair is a clean same-version comparison. An earlier opus attempt on "
          "this prompt also timed out at 1800s where this one finished in 1,472s. **No "
          "single cost figure here should be read as representative**; the tier ordering is "
          "consistent, the magnitudes are not.", "",
          "**Resolved post-baseline:** a `gpt-5.6-terra` re-run of `eval-route-density` "
          "under v2.0.1 supplied the first clean same-provider cross-version pair — see "
          "`2026-08-19-adr002-regression.md`.", ""]


def activation_section(L):
    """Claude activation ledger, iteration-1."""
    W = ROOT / "evals-workspace/iteration-1/claude"
    rows = [
        ("eval-route-density", "casual", "with_skill-ORIGINAL-inferred", "workhorse"),
        ("eval-route-density (repeat)", "casual", "with_skill", "workhorse"),
        ("eval-dental-no-shows v1", "precise", "with_skill", "workhorse-v1"),
        ("eval-dental-no-shows v2", "precise", "with_skill", "workhorse-v2"),
        ("eval-municipal-water-loss", "precise", "with_skill", "workhorse"),
        ("eval-bookstore-events", "casual", "with_skill", "workhorse"),
        ("eval-saas-onboarding-churn", "precise", "with_skill", "workhorse"),
    ]
    paths = {
        "eval-route-density": W/"workhorse/eval-route-density/with_skill-ORIGINAL-inferred/timing.json",
        "eval-route-density (repeat)": W/"workhorse/eval-route-density/with_skill/timing.json",
        "eval-dental-no-shows v1": W/"workhorse/eval-dental-no-shows-v1prompt/with_skill/timing.json",
        "eval-dental-no-shows v2": W/"workhorse/eval-dental-no-shows/with_skill/timing.json",
        "eval-municipal-water-loss": W/"workhorse/eval-municipal-water-loss/with_skill/timing.json",
        "eval-bookstore-events": W/"workhorse/eval-bookstore-events/with_skill/timing.json",
        "eval-saas-onboarding-churn": W/"workhorse/eval-saas-onboarding-churn/with_skill/timing.json",
    }
    got = [(n, reg, load(paths[n])) for n, reg, _, _ in rows if load(paths[n])]
    if not got:
        return
    act = sum(1 for _, _, d in got if d.get("activated"))
    obs = [(n, r, d) for n, r, d in got if str(d.get("activation_method","")).startswith("observed")]
    obs_act = sum(1 for _, _, d in obs if d.get("activated"))
    L += ["## Activation ledger", "",
          "Raw counts, deliberately not rates — n is far too small for a percentage to "
          f"mean anything. **{act} of {len(got)} `with_skill` runs activated; {obs_act} of "
          f"{len(obs)} by observed method.**", "",
          "| case | register | version | method | activated |", "|---|---|---|---|---|"]
    for n, reg, d in got:
        m = str(d.get("activation_method","")).split(":")[0]
        L.append(f"| `{n}` | {reg} | v{d.get('skill_version','?')} | "
                 f"{'**observed**' if m=='observed' else m} | "
                 f"{'**YES**' if d.get('activated') else 'no'} |")
    L += ["", "A non-activated `with_skill` run shows `turns: 1`, `tools: {}`, and costs "
          "within a few percent of its own control — it *is* a baseline run. Such runs are "
          "included in the **deployed** delta and excluded from **per-activation**.", "",
          "**Mechanism unknown.** Three hypotheses were proposed and all three falsified: "
          "the **exclusion-clause** explanation (killed by the v2 dental rewrite, which "
          "made the prediction and failed it), **conversational register** "
          "(pre-registered, then falsified in *both* directions by bookstore and saas), "
          "and **near-literal trigger-phrase overlap** (killed by saas, which contains no "
          "trigger phrase and activated). Full record with falsifying observations: "
          "`docs/NOTE-activation-variance.md`. No surviving hypothesis.", "",
          "`eval-dental-no-shows` has no `without_skill` arm on this tier: the restart "
          "predicate dropped it after its v2 `with_skill` run failed to activate, so this "
          "tier is **4-case**, not 5.", ""]


def route_density_section(bench, L):
    L += ["## The route-density result", "",
          "`eval-route-density` scored **3/7 with_skill and 3/7 without_skill — delta "
          "0.00** — despite activating, spawning subagents, and spending **767,382 tokens "
          "against the control's 40,099 (19x)**.", "",
          "Graded twice: a mechanical-only pass showed 0.00 and the **full LLM pass "
          "reproduced 0.00 exactly**. So \"did the mechanical set simply miss it?\" is "
          "answered **no** — the complete assertion set, including mechanism quality, "
          "fact/assumption separation and the case-specific inherited-constraint check, "
          "finds no measurable difference.", "",
          "**Interpretation (testable in iteration-2).** The control arm itself scored "
          "3/7 — where the base model natively produces protocol-shaped output, the "
          "marginal delta collapses. The delta measures the **gap between base behaviour "
          "and the protocol, per problem**, not the protocol in isolation. A problem the "
          "model already handles in a protocol-like way leaves the skill nothing to add, "
          "at full cost.", "",
          "The blind judge scored this case *for* `with_skill` on Claude, having scored it "
          "for the *control* on Codex flagship — the methods disagree on direction while "
          "agreeing there is no large assertion-level gap.", "",
          "Whether the 0.00 generalises is unknown: `eval-saas-onboarding-churn`, same "
          "model and tier, scored **6/7 vs 3/7 (+0.428)** and its control also scored 3/7. "
          "Case-to-case variance dominates any tier mean here, which is why the per-case "
          "tables matter more than the headline numbers.", ""]


def budget_section(L):
    L += ["## Budget and metering", "",
          "Eval runs were gated on a **token cap** (3,000,000 new Claude tokens). Two "
          "figures were tracked and they differ:", "",
          "| Figure | Value | Counts |", "|---|---|---|",
          "| Driver-counted | 1,990,576 | the unattended driver's own runs |",
          "| **True cumulative** | **2,846,382** | adds a standalone positive-control run "
          "(767,382) and a metering probe (88,424) launched outside the driver |", "",
          "The discrepancy is not an error in either number — the driver could only see "
          "runs it started. The **true** figure was the enforced one.", "",
          "### The token metric misprices small calls", "",
          "One cold grading call measured **88,424 tokens, of which 85,071 was "
          "`cacheCreation`** — the harness caching its own system prompt and tool "
          "definitions, charged per invocation and near-independent of payload. Actual "
          "response text across all grading and judge calls was ~41,000 tokens, about 1.5% "
          "of the projected cost. Under that metric 31 short classification calls would "
          "'cost' more than the entire opus envelope probe (2.65M vs 1.14M) — a run that "
          "took 15 turns, spawned 3 subagents and ran 4 web searches. Grading was therefore "
          "moved to a **cost basis**.", "",
          "### Measured: batching changes the price by 6x", "",
          "| | cold call | serial batch (27 calls) |", "|---|---|---|",
          "| cost per call | $0.5201 | **$0.0846** |",
          "| tokens per call | 88,424 | **42,549** |", "",
          "Run back-to-back, consecutive calls hit `cacheRead` instead of re-creating the "
          "cache. Cached share of the token sum stayed at **95.9%**: batching changes "
          "*which* cache field is charged, not the fact that ~96% of the token sum is "
          "scaffolding rather than work. Iteration-1 grading + judge totalled **$2.73** "
          "against a $25.00 ceiling.", "",
          "> **Neither metric is a verified proxy for subscription weekly-quota "
          "weighting.** `cost_usd` is an assumption, labelled as such. How either figure "
          "maps to quota consumption is unknown and was not measured.", ""]


def cost_line(args, L):
    g = load(ROOT / f"evals-workspace/iteration-{args.iteration}/"
                    f"cost-grading-{args.provider}-{args.tier}.json")
    jb = (load(ROOT / f"evals-workspace/iteration-{args.iteration}/{args.provider}/"
                      f"{args.tier}/judge.json") or {}).get("budget")
    if not (g or jb):
        return
    calls = (g or {}).get("calls", 0) + (jb or {}).get("calls", 0)
    usd = (g or {}).get("cost_usd", 0) + (jb or {}).get("cost_usd", 0)
    share = (g or {}).get("cached_share_of_tokens")
    L += ["## Cost", "",
          f"Grading and judging: **{calls} calls, ${usd:.2f}** against a $25.00 ceiling "
          f"(N=3 majority voting triples call volume). Cached scaffolding was "
          f"**{100*share:.1f}%** of the token sum — see the budget section of the "
          "iteration-1 results for why this project meters grading on cost rather than "
          "tokens.", ""]


def unstable_section(args, L):
    base = ROOT / f"evals-workspace/iteration-{args.iteration}/{args.provider}/{args.tier}"
    from collections import Counter
    c = Counter()
    for g in base.rglob("grading.json"):
        for r in json.loads(g.read_text())["assertion_results"]:
            if r.get("unstable"):
                c[r["text"]] += 1
    if not c:
        return
    L += ["## Unstable assertions (split votes)", "",
          "Assertions where the three grading passes disagreed. These are "
          "**mechanization/rewording candidates** — an assertion that cannot be graded "
          "consistently is a defective assertion, not a defective answer.", "",
          "| splits | assertion |", "|---|---|"]
    for k, v in c.most_common():
        L.append(f"| {v}x | {k} |")
    L.append("")


# --------------------------------------------------------- completeness gate

def required_sections(args) -> list[str]:
    req = ["## Headline", "### Two deltas", "## Per case", "## benchmark.json (verbatim)",
           "## Reproducing", "**Statistical modesty.**", "**Reproducibility.**",
           "## What this measures", "**Protocol compliance and cost, not independent"]
    if args.iteration == 1:
        req += ["**Version span.**", "**Post-baseline annotation.**",
                "## Budget and metering"]
        if args.provider == "claude":
            req += ["**Uncontrolled context (found 2026-08-20).**",
                    "## Opus envelope probe", "## Activation ledger",
                    "## The route-density result"]
            if args.tier == "workhorse":
                req += ["**Aggregation corrected in v2.0.2 per external review finding 5.**"]
        if args.provider == "codex" and args.tier == "workhorse":
            req += ["**ADR-002 regression measured post-baseline**"]
    else:
        # The version banner is now derived from the runs, so the gate checks the
        # sentence is present; main() refuses to write at all unless the tier
        # resolved to exactly one version.
        req += ["**Single protocol version.**", "**Grading method.**", "## Cost"]
    return req


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True)
    ap.add_argument("--tier", required=True, choices=["workhorse", "flagship"])
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--date", default=dt.date.today().isoformat())
    args = ap.parse_args()

    base = ROOT / f"evals-workspace/iteration-{args.iteration}/{args.provider}/{args.tier}"
    bench = load(base / "benchmark.json")
    # The reproduction command must name the model actually requested, not a
    # placeholder: `--model <alias>` is not a command anyone can run.
    prov = {}
    for t in sorted(base.rglob("timing.json")):
        prov = json.loads(t.read_text())
        break
    requested = prov.get("requested_model") or "<alias>"
    if not bench:
        print(f"no benchmark.json at {base}", file=sys.stderr); return 1
    cases = json.loads((ROOT / "evals/evals.json").read_text())["evals"]

    # Iteration-1's banner is a historical record of a two-version span and stays
    # as written. Every later iteration claims a SINGLE version, so that claim is
    # resolved from the runs and the run is refused if it does not hold -- before
    # anything is written, so a mixed-version tier produces no file rather than a
    # file asserting something false.
    tier_version = None
    if args.iteration != 1:
        versions = tier_skill_versions(base)
        if len(versions) != 1:
            print(f"REFUSING TO EMIT: iteration {args.iteration} "
                  f"{args.provider}/{args.tier} does not have exactly one skill "
                  f"version across its runs; found {sorted(versions)}",
                  file=sys.stderr)
            return 1
        tier_version = next(iter(versions))
    jdoc = load(base / "judge.json")
    jmap = {j["slug"]: j for j in (jdoc.get("verdicts", []) if isinstance(jdoc, dict) else (jdoc or []))}
    models = [m for m in bench["resolved_models"] if m not in ("UNKNOWN", "TIMEOUT")]
    slug = models[0] if models else "unknown-model"
    rs = bench["run_summary"]

    L = [f"# Eval baseline — {args.provider} / {slug}", "",
         f"**Date:** {args.date} · **Iteration:** {args.iteration} · "
         f"**Provider:** {args.provider}", "",
         f"**Resolved model(s):** {', '.join(bench['resolved_models'])} — the resolved id "
         "reported by the run, not a requested alias.", "",
         paired_design_line(bench, len(cases)), ""]
    if prov.get("repo_commit"):
        L += [f"**Provenance:** repo `{prov['repo_commit'][:12]}`"
              + ("**(dirty tree)**" if prov.get("repo_dirty") else "")
              + f" · skill **v{prov.get('skill_version','?')}** "
              f"({prov.get('skill_version_method','?')}) · "
              f"`{prov.get('cli_name')}` {prov.get('cli_version')}", ""]
    banners(args, L, tier_version)
    scope_section(args, L)

    L += ["## Headline", "", "| Metric | with_skill | without_skill | delta |",
          "|---|---|---|---|"]
    cell = lambda a, k, f="{:.2f}": (f.format(rs[a][k]["mean"])
                                     if rs[a].get(k) and rs[a][k].get("mean") is not None else "—")
    L += [f"| Assertion pass rate | {cell('with_skill','pass_rate')} | "
          f"{cell('without_skill','pass_rate')} | {bench['run_summary']['delta'].get('pass_rate','—')} |",
          f"| Duration (s) | {cell('with_skill','time_seconds','{:.0f}')} | "
          f"{cell('without_skill','time_seconds','{:.0f}')} | "
          f"{bench['run_summary']['delta'].get('time_seconds','—')} |",
          f"| Tokens | {cell('with_skill','tokens','{:,.0f}')} | "
          f"{cell('without_skill','tokens','{:,.0f}')} | "
          f"{bench['run_summary']['delta'].get('tokens','—')} |", ""]
    deltas_section(bench, L)
    judge_section(jdoc, L, args.iteration)

    L += ["## Per case", ""]
    for c in cases:
        L += [f"### {c['slug']} — {c['domain']}, {c['phrasing']}"
              + ("  ·  **control: conventional is near-optimal**" if "control" in c else ""), ""]
        for arm in ("with_skill", "without_skill"):
            t = load(base / c["slug"] / arm / "timing.json")
            if not t:
                L += [f"- `{arm}`: no run recorded", ""]; continue
            g = load(base / c["slug"] / arm / "grading.json")
            bits = []
            if g:
                bits.append(f"{g['summary']['passed']}/{g['summary']['total']} assertions")
            bits += [f"{t['total_tokens']:,} tok", f"{t['duration_ms']/1000:.0f}s",
                     f"v{t.get('skill_version','?')}"]
            if arm == "with_skill" and t.get("activated") is False:
                bits.append("**skill did NOT activate**")
            if t.get("failure_mode"):
                bits.append(f"**{t['failure_mode']}**")
            L.append(f"- `{arm}`: " + " · ".join(bits))
        if c["slug"] in jmap:
            L.append(f"- judge: **{jmap[c['slug']]['winner_arm']}** — {jmap[c['slug']]['reason']}")
        L.append("")

    if args.iteration == 1 and args.provider == "claude":
        opus_section(L); activation_section(L); route_density_section(bench, L)
    unstable_section(args, L)
    if args.iteration == 1:
        budget_section(L)
    else:
        cost_line(args, L)

    L += ["## benchmark.json (verbatim)", "", "```json", json.dumps(bench, indent=2),
          "```", "", "## Reproducing", "", "```bash",
          f"python3 evals/runners/run_evals.py --provider {args.provider} --tier {args.tier} "
          f"--model {requested} --iteration {args.iteration}",
          f"python3 evals/runners/grade.py     --provider {args.provider} --tier {args.tier} "
          f"--iteration {args.iteration}" + (" --votes 3" if args.iteration > 1 else ""),
          f"python3 evals/runners/judge.py     --provider {args.provider} --tier {args.tier} "
          f"--iteration {args.iteration}" + (" --votes 3" if args.iteration > 1 else ""),
          f"python3 evals/runners/aggregate.py --provider {args.provider} --tier {args.tier} "
          f"--iteration {args.iteration}",
          f"python3 evals/runners/report.py    --provider {args.provider} --tier {args.tier} "
          f"--iteration {args.iteration}", "```", ""]

    out = ROOT / "evals/results" / f"{args.date}-{args.provider}-{slug}.md"
    out.write_text("\n".join(L), encoding="utf-8")

    # Completeness gate: re-read from disk, never trust the write.
    written = out.read_text(encoding="utf-8")
    missing = [s for s in required_sections(args) if s not in written]
    if missing:
        out.unlink()
        print(f"REFUSING TO EMIT {out.name}: missing required sections:", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        return 1
    print(f"wrote {out.relative_to(ROOT)}  ({len(written.splitlines())} lines, "
          f"{len(required_sections(args))} required sections verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
