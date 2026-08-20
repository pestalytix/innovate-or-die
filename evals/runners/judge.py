#!/usr/bin/env python3
"""Blind pairwise judge: score two answers without knowing which arm is which.

Arm labels are replaced with "Answer A"/"Answer B" and the order is flipped on
alternating cases so position bias cannot align with arm. The mapping is written
out only after the verdict is recorded.
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ---- cost-basis budget (Gate D ruling: token metric counts cached scaffolding) ----
COST_CEILING = 25.00
_cost = {"usd": 0.0, "calls": 0, "cacheRead": 0, "cacheCreation": 0,
         "input": 0, "output": 0}


def _account(out: dict) -> None:
    """Tally one claude -p invocation. Records the cacheRead/cacheCreation split
    because that distribution is the whole reason the token metric misprices
    many-small-calls workloads."""
    _cost["calls"] += 1
    _cost["usd"] += float(out.get("total_cost_usd") or 0.0)
    for v in (out.get("modelUsage") or {}).values():
        _cost["cacheRead"] += v.get("cacheReadInputTokens", 0)
        _cost["cacheCreation"] += v.get("cacheCreationInputTokens", 0)
        _cost["input"] += v.get("inputTokens", 0)
        _cost["output"] += v.get("outputTokens", 0)
    if _cost["usd"] > COST_CEILING:
        raise SystemExit(f"COST CEILING HIT: ${_cost['usd']:.2f} > ${COST_CEILING:.2f} "
                         f"after {_cost['calls']} calls. Halting.")


def _cost_report(label: str) -> dict:
    tok = _cost["cacheRead"] + _cost["cacheCreation"] + _cost["input"] + _cost["output"]
    cached = _cost["cacheRead"] + _cost["cacheCreation"]
    d = {"label": label, "calls": _cost["calls"], "cost_usd": round(_cost["usd"], 4),
         "token_sum": tok, "cacheRead": _cost["cacheRead"],
         "cacheCreation": _cost["cacheCreation"],
         "cached_share_of_tokens": round(cached / tok, 4) if tok else None,
         "input": _cost["input"], "output": _cost["output"]}
    print(f"\n  [{label}] {d['calls']} calls  ${d['cost_usd']:.4f}  "
          f"tokens {tok:,} (cacheRead {d['cacheRead']:,} / "
          f"cacheCreation {d['cacheCreation']:,} = "
          f"{100*(d['cached_share_of_tokens'] or 0):.1f}% cached scaffolding)")
    return d



PROMPT = """You are judging two answers to the same problem. You do not know how either was produced.

PROBLEM:
{prompt}

ANSWER A:
---
{a}
---

ANSWER B:
---
{b}
---

Score each answer 1-5 on: non_obviousness (did it leave the default answer
neighbourhood?), mechanism (are causal mechanisms named, not gestured at?),
testability (are claims falsifiable with specifics?), honesty (does it
distinguish fact from assumption, and admit when the conventional option wins?),
usefulness (could the reader act on this next week?).

Do not reward length, eloquence, or exotic vocabulary. A concise answer whose
ideas carry mechanisms outranks an expansive one that gestures.

Reply with ONLY JSON:
{{"A": {{"non_obviousness":n,"mechanism":n,"testability":n,"honesty":n,"usefulness":n}},
  "B": {{...same keys...}},
  "winner": "A"|"B"|"tie",
  "reason": "<one sentence, max 200 chars>"}}"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--provider", required=True)
    ap.add_argument("--tier", required=True, choices=["workhorse", "flagship"])
    ap.add_argument("--votes", type=int, default=1,
                    help="independent judge passes per pair; verdict is the MAJORITY")
    ap.add_argument("--judge-model", default="claude-sonnet-5",
                    help="MODEL_POLICY: judge pinned to the workhorse tier")
    args = ap.parse_args()

    resolved_judge: set[str] = set()
    cases = json.loads((ROOT / "evals/evals.json").read_text())["evals"]
    base = ROOT / "evals-workspace" / f"iteration-{args.iteration}" / args.provider / args.tier
    out = []

    for i, c in enumerate(cases):
        paths = {a: base / c["slug"] / a / "outputs" / "response.md"
                 for a in ("with_skill", "without_skill")}
        if not all(p.exists() for p in paths.values()):
            print(f"skip (missing output): {c['slug']}"); continue
        # alternate which arm is presented first so position bias != arm bias
        first, second = (("with_skill", "without_skill") if i % 2 == 0
                         else ("without_skill", "with_skill"))
        ballots = []
        for _v in range(max(1, args.votes)):
          p = subprocess.run(
            ["claude", "-p", PROMPT.format(prompt=c["prompt"],
                                           a=paths[first].read_text()[:40000],
                                           b=paths[second].read_text()[:40000]),
             "--model", args.judge_model, "--output-format", "json"],
            capture_output=True, text=True, timeout=900)
          try:
            outj = json.loads(p.stdout)
            _account(outj)
            mu = outj.get("modelUsage", {}) or {}
            fam = "-".join(args.judge_model.split("-")[:2])
            resolved_judge.update(k for k in mu if k.startswith(fam))
            raw = outj.get("result", "")
            ballots.append(json.loads(re.search(r"\{.*\}", raw, re.S).group(0)))
          except Exception as e:
            print(f"  judge error on {c['slug']}: {e}")
        if not ballots:
            continue
        from collections import Counter
        tally = Counter(b.get("winner") for b in ballots)
        top, n_top = tally.most_common(1)[0]
        d = next(b for b in ballots if b.get("winner") == top)
        # unblind only now
        mapping = {"A": first, "B": second}
        winner = mapping.get(d.get("winner"), "tie")
        rec = {"slug": c["slug"], "presented_first": first,
               "vote_split": dict(tally), "votes": len(ballots),
               "unanimous": n_top == len(ballots),
               "scores": {mapping[k]: v for k, v in d.items() if k in ("A", "B")},
               "winner_arm": winner, "reason": d.get("reason", "")}
        out.append(rec)
        print(f"{c['slug']:34s} winner={winner}")

    (base / "judge.json").write_text(json.dumps(
        {"judge_model_requested": args.judge_model,
         "judge_model_resolved": sorted(resolved_judge) or None,
         "limitation": ("A Claude-family judge scores both providers. Blind pairwise "
                        "cancels arm bias WITHIN a provider; cross-provider comparisons "
                        "carry possible same-family leniency toward Claude outputs."),
         "verdicts": out,
         "budget": _cost_report("judge")}, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
