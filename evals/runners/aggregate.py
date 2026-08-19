#!/usr/bin/env python3
"""Aggregate per-run grading + timing into benchmark.json for an iteration."""
from __future__ import annotations
import argparse, json, statistics as st, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def ms(vals): return {"mean": round(st.mean(vals), 2),
                      "stddev": round(st.stdev(vals), 2) if len(vals) > 1 else None}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--provider", required=True)
    ap.add_argument("--tier", required=True, choices=["workhorse", "flagship"])
    args = ap.parse_args()

    cases = json.loads((ROOT / "evals/evals.json").read_text())["evals"]
    base = ROOT / "evals-workspace" / f"iteration-{args.iteration}" / args.provider / args.tier
    summary, resolved = {}, set()

    # Two named deltas (Gate D ruling 2):
    #   deployed        -- every case, misses and stalls included: what an
    #                      installing user actually experiences.
    #   per_activation  -- cases where the skill fired: protocol quality when it
    #                      works. An activated-but-failed run (e.g. stage0-stall)
    #                      counts here; only genuine non-activations are excluded.
    # Neither alone is the headline; the gap between them IS the
    # activation/execution-reliability finding.
    def delta_set(only_activated: bool):
        ds = []
        for c in cases:
            gw, go = base/c["slug"]/"with_skill"/"grading.json", base/c["slug"]/"without_skill"/"grading.json"
            tw = base/c["slug"]/"with_skill"/"timing.json"
            if not (gw.exists() and go.exists() and tw.exists()):
                continue
            if only_activated and not json.loads(tw.read_text()).get("activated"):
                continue
            w = json.loads(gw.read_text())["summary"]["pass_rate"]
            o = json.loads(go.read_text())["summary"]["pass_rate"]
            if w is not None and o is not None:
                ds.append((c["slug"], round(w - o, 4)))
        return ds

    for arm in ("with_skill", "without_skill"):
        rates, secs, toks = [], [], []
        for c in cases:
            d = base / c["slug"] / arm
            g, t = d / "grading.json", d / "timing.json"
            if g.exists():
                r = json.loads(g.read_text())["summary"]["pass_rate"]
                if r is not None: rates.append(r)
            if t.exists():
                j = json.loads(t.read_text())
                secs.append(j["duration_ms"] / 1000); toks.append(j["total_tokens"])
                resolved.add(j.get("resolved_model", "UNKNOWN"))
        summary[arm] = {"pass_rate": ms(rates) if rates else None,
                        "time_seconds": ms(secs) if secs else None,
                        "tokens": ms(toks) if toks else None,
                        "n": len(secs)}

    w, o = summary["with_skill"], summary["without_skill"]
    delta = {}
    for k in ("pass_rate", "time_seconds", "tokens"):
        if w[k] and o[k]:
            delta[k] = round(w[k]["mean"] - o[k]["mean"], 4)
    dep, act = delta_set(False), delta_set(True)
    excluded = [s for s, _ in dep if s not in {s2 for s2, _ in act}]
    doc = {"run_summary": {**summary, "delta": delta},
           "deltas": {
               "deployed": {"mean": round(sum(d for _, d in dep)/len(dep), 4) if dep else None,
                            "n": len(dep), "per_case": dict(dep),
                            "meaning": "every case, misses and stalls included -- what an installing user experiences"},
               "per_activation": {"mean": round(sum(d for _, d in act)/len(act), 4) if act else None,
                                  "n": len(act), "per_case": dict(act),
                                  "meaning": "cases where the skill fired; activated-but-failed runs included"},
               "excluded_from_per_activation": excluded,
               "gap_is": "activation/execution reliability"},
           "resolved_models": sorted(resolved), "provider": args.provider,
           "iteration": args.iteration}
    (base / "benchmark.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(doc, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
