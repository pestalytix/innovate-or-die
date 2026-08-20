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
"""
from __future__ import annotations
import argparse, datetime as dt, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


# ----------------------------------------------------------------- sections

def banners(args, L):
    L += ["> **Version span.** Iteration-1 spans **two protocol versions**: runs before "
          "the ADR-002 Stage 0 fix are **v2.0.0**, runs after it are **v2.0.1**. Each arm "
          "below is labelled. Cross-version comparisons within this iteration are "
          "confounded and flagged where they occur." if args.iteration == 1 else
          "> **Single protocol version.** Every run in this iteration used **v2.0.1** "
          "(post ADR-002 Stage 0 fix), so within-iteration comparisons are clean.", ""]
    L += ["> **Statistical modesty.** Five cases, **one run per case, per arm**. Every "
          "number here is **directional only** — no repeated trials of the runs "
          "themselves, so no variance estimate and no significance. `stddev` across cases "
          "measures case-to-case spread, not run-to-run stability. Treat differences of a "
          "few points as indistinguishable from noise, and win/loss tallies as anecdote. "
          "The qualitative verdicts and named findings carry more weight than any mean "
          "here.", ""]
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
    L += ["> **Reproducibility.** `evals-workspace/` holds the raw transcripts and is "
          "**local-only (gitignored)**. `evals/evals.json` plus `evals/runners/` "
          "regenerate it; this file is the durable record.", ""]


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


def judge_section(jdoc, L):
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
    L += ["", f"(Tally for completeness only: with_skill {w}, without_skill {o}, other "
          f"{len(verdicts)-w-o}. **At n=5 with one run per case this count is noise and "
          "carries no claim.** Answers were shown as 'A'/'B' with presentation order "
          "alternating per case, so position bias cannot align with arm.)", ""]


def opus_section(L):
    """Flagship envelope probe — claude only, iteration-1."""
    t = load(ROOT / "evals-workspace/iteration-1/claude/flagship/eval-route-density/"
                    "with_skill/timing.json")
    if not t:
        return
    W = ROOT / "evals-workspace/iteration-1/claude/workhorse/eval-route-density"
    a = load(W / "with_skill-ORIGINAL-inferred/timing.json")
    b = load(W / "with_skill/timing.json")
    L += ["## Opus envelope probe (flagship, n=1, not aggregated)", "",
          "The 10-run flagship tier was replaced by a single envelope probe (MODEL_POLICY "
          "scope amendment). One case, `with_skill` only, `claude-opus-5`, **default "
          "effort — the deployed condition on a Max plan**, so the result carries the "
          "upward-compatibility claim. **It completed**, so the medium-effort mitigation "
          "arm was not run.", "",
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
           "## Reproducing", "**Statistical modesty.**", "**Reproducibility.**"]
    if args.iteration == 1:
        req += ["**Post-baseline annotation.**", "## Budget and metering"]
        if args.provider == "claude":
            req += ["## Opus envelope probe", "## Activation ledger",
                    "## The route-density result"]
        if args.provider == "codex" and args.tier == "workhorse":
            req += ["**ADR-002 regression measured post-baseline**"]
    else:
        req += ["**Grading method.**", "## Cost"]
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
    if not bench:
        print(f"no benchmark.json at {base}", file=sys.stderr); return 1
    cases = json.loads((ROOT / "evals/evals.json").read_text())["evals"]
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
         "Paired design: every case ran twice, with and without the skill, same prompt, "
         "same model, clean context. The delta is the result.", ""]
    banners(args, L)

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
    judge_section(jdoc, L)

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
          f"--model <alias> --iteration {args.iteration}",
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
