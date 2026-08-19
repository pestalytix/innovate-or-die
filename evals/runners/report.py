#!/usr/bin/env python3
"""Emit evals/results/YYYY-MM-DD-<provider>-<resolved-model>.md.

The results file is the public record: evals-workspace/ is gitignored, so every
number needed to interpret the run is inlined here, including benchmark.json
verbatim.
"""
from __future__ import annotations
import argparse, datetime as dt, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--provider", required=True)
    ap.add_argument("--tier", required=True, choices=["workhorse", "flagship"])
    ap.add_argument("--date", default=dt.date.today().isoformat())
    args = ap.parse_args()

    base = ROOT / "evals-workspace" / f"iteration-{args.iteration}" / args.provider / args.tier
    bench = json.loads((base / "benchmark.json").read_text())
    cases = json.loads((ROOT / "evals/evals.json").read_text())["evals"]
    jdoc = json.loads((base / "judge.json").read_text()) if (base / "judge.json").exists() else {}
    judge = jdoc.get("verdicts", []) if isinstance(jdoc, dict) else jdoc
    jmap = {j["slug"]: j for j in judge}

    models = [m for m in bench["resolved_models"] if m not in ("UNKNOWN", "TIMEOUT")]
    slug = models[0] if models else "unknown-model"
    rs = bench["run_summary"]

    L = [f"# Eval baseline — {args.provider} / {slug}", "",
         f"**Date:** {args.date} · **Iteration:** {args.iteration} · "
         f"**Provider:** {args.provider}", "",
         f"**Resolved model(s):** {', '.join(bench['resolved_models'])} — "
         "this is the resolved id reported by the run, not a requested alias.", "",
         "Paired design: every case ran twice, with and without the skill, same "
         "prompt, same model, clean context. The delta is the result.", "",
         "> **Statistical modesty.** Five cases, **one run per case, per arm**. "
         "Every number here is **directional only** — no repeated trials, so no "
         "variance estimate and no significance. `stddev` across cases measures "
         "case-to-case spread, not run-to-run stability. Treat differences of a "
         "few points as indistinguishable from noise, and treat win/loss tallies "
         "as anecdote. The qualitative verdicts and the named findings carry more "
         "weight than any mean in this document.", "",
         "## Headline", ""]

    def cell(arm, key, fmt="{:.2f}"):
        v = rs[arm].get(key)
        return fmt.format(v["mean"]) if v and v.get("mean") is not None else "—"

    L += ["| Metric | with_skill | without_skill | delta |", "|---|---|---|---|",
          f"| Assertion pass rate | {cell('with_skill','pass_rate')} | "
          f"{cell('without_skill','pass_rate')} | "
          f"{rs['delta'].get('pass_rate','—')} |",
          f"| Duration (s) | {cell('with_skill','time_seconds','{:.0f}')} | "
          f"{cell('without_skill','time_seconds','{:.0f}')} | "
          f"{rs['delta'].get('time_seconds','—')} |",
          f"| Tokens | {cell('with_skill','tokens','{:,.0f}')} | "
          f"{cell('without_skill','tokens','{:,.0f}')} | "
          f"{rs['delta'].get('tokens','—')} |", ""]

    dl = bench.get("deltas", {})
    if dl:
        L += ["### Two deltas", "",
              "| Delta | Mean | n | Meaning |", "|---|---|---|---|",
              f"| **deployed** | {dl['deployed']['mean']} | {dl['deployed']['n']} | "
              f"{dl['deployed']['meaning']} |",
              f"| **per-activation** | {dl['per_activation']['mean']} | {dl['per_activation']['n']} | "
              f"{dl['per_activation']['meaning']} |", "",
              (f"Excluded from per-activation: `{', '.join(dl['excluded_from_per_activation'])}`."
               if dl.get("excluded_from_per_activation")
               else "No genuine non-activations in this tier, so the two deltas are **identical**. "
                    "The gap between them is the activation/execution-reliability signal; here it is **0.000**."),
              "", "Per case (deployed): " +
              ", ".join(f"`{k}` {v:+.3f}" for k, v in dl["deployed"]["per_case"].items()), ""]
    if judge:
        L += [f"**Judge model:** requested `{jdoc.get('judge_model_requested')}`, resolved "
              f"`{', '.join(jdoc.get('judge_model_resolved') or ['unknown'])}`.", "",
              f"> **Limitation.** {jdoc.get('limitation','')}", ""]
        wins = sum(1 for j in judge if j["winner_arm"] == "with_skill")
        loss = sum(1 for j in judge if j["winner_arm"] == "without_skill")
        L += ["### What the judge actually said", "",
              "The verdict *text* is the finding here. Read the reasoning, not the "
              "tally.", ""]
        for j in judge:
            L.append(f"- **{j['slug']}** → *{j['winner_arm']}* — {j['reason']}")
        L += ["", f"(Tally, for completeness only: with_skill {wins}, without_skill "
              f"{loss}, tie {len(judge)-wins-loss}. **At n=5 with one run per case "
              "this count is noise and carries no claim.** The judge saw answers as "
              "'A'/'B' with presentation order alternating per case, so position bias "
              "cannot align with arm.)", ""]

    L += ["## Per case", ""]
    for c in cases:
        L.append(f"### {c['slug']} — {c['domain']}, {c['phrasing']}"
                 + ("  ·  **control: conventional is near-optimal**" if "control" in c else ""))
        L.append("")
        for arm in ("with_skill", "without_skill"):
            g = base / c["slug"] / arm / "grading.json"
            t = base / c["slug"] / arm / "timing.json"
            if not t.exists():
                L += [f"- `{arm}`: no run recorded", ""]; continue
            tj = json.loads(t.read_text())
            bits = [f"{tj['total_tokens']:,} tok", f"{tj['duration_ms']/1000:.0f}s"]
            if g.exists():
                s = json.loads(g.read_text())["summary"]
                bits.insert(0, f"{s['passed']}/{s['total']} assertions")
            if "error" in tj:
                bits.append(f"**{tj['error']}**")
            L.append(f"- `{arm}`: " + " · ".join(bits))
        if c["slug"] in jmap:
            L.append(f"- judge: **{jmap[c['slug']]['winner_arm']}** — "
                     f"{jmap[c['slug']]['reason']}")
        L.append("")

    L += ["## benchmark.json (verbatim)", "", "```json",
          json.dumps(bench, indent=2), "```", "",
          "## Reproducing", "",
          "```bash",
          f"python3 evals/runners/run_evals.py --provider {args.provider} "
          f"--model <alias> --iteration {args.iteration}",
          f"python3 evals/runners/grade.py     --provider {args.provider} --iteration {args.iteration}",
          f"python3 evals/runners/judge.py     --provider {args.provider} --iteration {args.iteration}",
          f"python3 evals/runners/aggregate.py --provider {args.provider} --iteration {args.iteration}",
          f"python3 evals/runners/report.py    --provider {args.provider} --iteration {args.iteration}",
          "```", "",
          "Raw transcripts live in `evals-workspace/`, which is gitignored; "
          "`evals/evals.json` plus these runners regenerate them.", ""]

    out = ROOT / "evals/results" / f"{args.date}-{args.provider}-{slug}.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
