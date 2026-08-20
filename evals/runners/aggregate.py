#!/usr/bin/env python3
"""Aggregate per-run grading + timing into benchmark.json for an iteration."""
from __future__ import annotations
import argparse, json, statistics as st, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def ms(vals): return {"mean": round(st.mean(vals), 2),
                      "stddev": round(st.stdev(vals), 2) if len(vals) > 1 else None}


# ------------------------------------------------------------ run validity
# MODEL_POLICY rule 3: a requested-vs-resolved mismatch is a run FAILURE and is
# excluded from headline numbers. The same applies to a run that timed out or
# whose output could not be parsed -- in each case the number does not measure
# what it claims to.
#
# A non-activation is deliberately NOT in this list. It is a valid measurement
# of a real deployed outcome, and the `deployed` delta exists to include it;
# dropping it here would delete the activation-reliability finding instead of
# reporting it. Harness failure and protocol miss are different things.
ACTIVATION_NOTICE = "SKILL DID NOT ACTIVATE"


def invalid_reasons(t: dict | None, g: dict | None) -> list[str]:
    if t is None:
        return ["no timing.json"]
    r = []
    if t.get("model_mismatch"):
        r.append(f"model_mismatch (requested {t.get('requested_model')}, "
                 f"resolved {t.get('resolved_model')})")
    if t.get("resolved_model") in ("UNKNOWN", "TIMEOUT"):
        r.append(f"resolved_model={t.get('resolved_model')}")
    err = str(t.get("error") or "")
    if err and ACTIVATION_NOTICE not in err:
        r.append(f"error: {err[:60]}")
    if t.get("parse_confidence") in ("failed", "error-envelope"):
        r.append(f"parse_confidence={t.get('parse_confidence')}")
    if g is None:
        r.append("no grading.json")
    elif g.get("summary", {}).get("pass_rate") is None:
        r.append("grading pass_rate is null (parse failure)")
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--provider", required=True)
    ap.add_argument("--tier", required=True, choices=["workhorse", "flagship"])
    args = ap.parse_args()

    cases = json.loads((ROOT / "evals/evals.json").read_text())["evals"]
    base = ROOT / "evals-workspace" / f"iteration-{args.iteration}" / args.provider / args.tier
    summary, resolved = {}, set()

    def load(c_slug, arm, name):
        p = base / c_slug / arm / name
        return json.loads(p.read_text()) if p.exists() else None

    # The design is PAIRED: a delta is only meaningful between two arms of the
    # same case. Means taken over per-arm sets that do not contain the same
    # cases are not comparable, so every figure below is computed over matched
    # valid pairs and the dropped pairs are named in the output.
    pairs, dropped_pairs = [], []
    for c in cases:
        rec = {a: {"t": load(c["slug"], a, "timing.json"),
                   "g": load(c["slug"], a, "grading.json")} for a in
               ("with_skill", "without_skill")}
        why = {a: invalid_reasons(rec[a]["t"], rec[a]["g"]) for a in rec}
        if any(why.values()):
            if any(rec[a]["t"] or rec[a]["g"] for a in rec):   # a partial pair
                dropped_pairs.append({"slug": c["slug"],
                                      "with_skill": why["with_skill"],
                                      "without_skill": why["without_skill"]})
            continue
        pairs.append((c["slug"], rec))

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
        for slug, rec in pairs:
            if only_activated and not rec["with_skill"]["t"].get("activated"):
                continue
            w = rec["with_skill"]["g"]["summary"]["pass_rate"]
            o = rec["without_skill"]["g"]["summary"]["pass_rate"]
            ds.append((slug, round(w - o, 4)))
        return ds

    for arm in ("with_skill", "without_skill"):
        rates, secs, toks = [], [], []
        for _slug, rec in pairs:
            t, g = rec[arm]["t"], rec[arm]["g"]
            rates.append(g["summary"]["pass_rate"])
            secs.append(t["duration_ms"] / 1000)
            toks.append(t["total_tokens"])
            resolved.add(t.get("resolved_model", "UNKNOWN"))
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
           "pairing": {
               "rule": ("matched valid pairs only: both arms present, neither "
                        "carrying model_mismatch, TIMEOUT/UNKNOWN resolution, a "
                        "harness error, a parse failure, or a null grade"),
               "note": ("a non-activated with_skill run is NOT invalid -- it is a "
                        "real deployed outcome and is included in the deployed "
                        "delta; see `deltas`"),
               "pairs_used": [s for s, _ in pairs],
               "excluded_pairs": dropped_pairs},
           "resolved_models": sorted(resolved), "provider": args.provider,
           "iteration": args.iteration}
    (base / "benchmark.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(doc, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
