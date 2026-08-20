#!/usr/bin/env python3
"""Blind pairwise judge: score two answers without knowing which arm is which.

Arm labels are replaced with "Answer A"/"Answer B" and the presentation order is
drawn independently FOR EVERY BALLOT from a seeded RNG keyed on
(provider, tier, iteration, slug, vote_index).

Index alternation -- used through iteration 2 -- pinned one fixed order per case,
which removes the crudest confound but is not randomization: the arm-to-position
map was a deterministic function of case order, so any position effect landed on
the same arm every time that case was judged. Randomizing per ballot means a
residual alignment between position and arm is chance, not design. It is not
eliminated; at these ballot counts it is simply no longer systematic.

The order each ballot actually saw is recorded in that ballot's `presented_first`,
and the case-level `presented_first` carries ballot 0's value. The mapping is
written out only after the verdict is recorded.
"""
from __future__ import annotations
import argparse, hashlib, json, random, re, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _sh(*cmd: str) -> str | None:
    """First line of a command's output, or None. Used for harness provenance."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        out = (p.stdout or p.stderr).strip()
        return out.splitlines()[0] if out else None
    except Exception:
        return None


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



ARMS = ("with_skill", "without_skill")
# `decide()` tallies whatever labels it is handed. Ballots are unblinded to ARMS
# before tallying now (each ballot had its own A/B mapping), so the mapping it
# applies afterwards is the identity.
ARM_IDENTITY = {"with_skill": "with_skill", "without_skill": "without_skill",
                "tie": "tie"}


def order_seed(provider: str, tier: str, iteration: int, slug: str,
               vote_index: int) -> int:
    """Stable seed for one ballot's presentation order.

    sha256, not the builtin `hash()`: string hashing is salted per interpreter
    process, so a `hash()`-derived seed would give a different order on every
    invocation and the recorded seed inputs would not reproduce the run.
    """
    key = f"{provider}|{tier}|{iteration}|{slug}|{vote_index}"
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big")


def ballot_order(provider: str, tier: str, iteration: int, slug: str,
                 vote_index: int) -> tuple[str, str]:
    """(presented_first, presented_second) for one ballot."""
    rng = random.Random(order_seed(provider, tier, iteration, slug, vote_index))
    return ARMS if rng.getrandbits(1) else (ARMS[1], ARMS[0])


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


def decide(ballots: list[dict], mapping: dict[str, str]) -> tuple[str, bool, Counter, int]:
    """Resolve a set of ballots to a winning ARM, unblinding only at the end.

    A/B/tie is a THREE-way split, so the most common vote is not necessarily a
    majority: 1-1-1 would otherwise award a win on a single ballot. Require
    strictly more than half; anything less is a tie. An even split (2-2) is a
    tie for the same reason.

    Returns (winner_arm, has_majority, tally, top_count). `tally` counts the
    labels as handed in and `mapping` is applied only to the result, so this
    works either way round: blind A/B labels with an A/B->arm mapping, or
    already-unblinded arm labels with ARM_IDENTITY. main() uses the second form
    because per-ballot randomization gives each ballot its own A/B mapping.
    """
    tally = Counter(b.get("winner") for b in ballots)
    top, n_top = tally.most_common(1)[0]
    has_majority = n_top * 2 > len(ballots)
    return (mapping.get(top, "tie") if has_majority else "tie"), has_majority, tally, n_top


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

    for c in cases:
        paths = {a: base / c["slug"] / a / "outputs" / "response.md"
                 for a in ARMS}
        if not all(p.exists() for p in paths.values()):
            print(f"skip (missing output): {c['slug']}"); continue
        # Presentation order is drawn per BALLOT, not per case, so each ballot
        # carries its own A/B->arm mapping and must be unblinded with its own.
        ballots = []
        for _v in range(max(1, args.votes)):
          first, second = ballot_order(args.provider, args.tier, args.iteration,
                                       c["slug"], _v)
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
            ballots.append((first, second,
                            json.loads(re.search(r"\{.*\}", raw, re.S).group(0))))
          except Exception as e:
            print(f"  judge error on {c['slug']}: {e}")
        if not ballots:
            continue
        # unblind only now -- each ballot with the mapping it was actually shown
        # Every ballot is evidence. Keeping one "representative" ballot threw
        # away the disagreement that makes a split verdict worth reading.
        unblinded = []
        for first, second, b in ballots:
            m = {"A": first, "B": second}
            unblinded.append({"winner_arm": m.get(b.get("winner"), "tie"),
                              "scores": {m[k]: v for k, v in b.items()
                                         if k in ("A", "B")},
                              "reason": b.get("reason", ""),
                              "presented_first": first})
        # Tally over ARMS, not over A/B: with per-ballot order an A/B tally sums
        # positions across different mappings and means nothing.
        winner, has_majority, tally, n_top = decide(
            [{"winner": bb["winner_arm"]} for bb in unblinded], ARM_IDENTITY)
        dims = ("non_obviousness", "mechanism", "testability", "honesty", "usefulness")
        scores_mean = {}
        for arm in ARMS:
            vals = [bb["scores"][arm] for bb in unblinded if arm in bb["scores"]]
            if vals:
                scores_mean[arm] = {d_: round(sum(v.get(d_, 0) for v in vals) / len(vals), 2)
                                    for d_ in dims}
        agreeing = [bb["reason"] for bb in unblinded if bb["winner_arm"] == winner]
        rec = {"slug": c["slug"], "presented_first": unblinded[0]["presented_first"],
               "vote_split": dict(tally), "votes": len(ballots),
               "unanimous": n_top == len(ballots),
               "majority": has_majority,
               "ballots": unblinded,
               "scores_mean": scores_mean,
               "winner_arm": winner,
               "reason": (agreeing[0] if agreeing else
                          "no majority across ballots -- recorded as a tie; "
                          "see `ballots` for each judge's reasoning")}
        out.append(rec)
        print(f"{c['slug']:34s} winner={winner}"
              f"{'' if has_majority else '  (NO MAJORITY -> tie)'}")

    (base / "judge.json").write_text(json.dumps(
        {# Method provenance travels WITH the artifact. A reader -- including
         # report.py -- must not have to infer how a run was judged from its
         # iteration number: iteration is a label, not a record of method, and
         # a re-run of an old iteration under a new harness would be described
         # wrongly by any rule keyed on it.
         "presentation_method": "per-ballot-seeded-sha256",
         "harness_commit": _sh("git", "-C", str(ROOT), "rev-parse", "HEAD"),
         "judge_model_requested": args.judge_model,
         "judge_model_resolved": sorted(resolved_judge) or None,
         "limitation": ("A Claude-family judge scores both providers. Blind pairwise "
                        "cancels arm bias WITHIN a provider; cross-provider comparisons "
                        "carry possible same-family leniency toward Claude outputs."),
         "verdicts": out,
         "budget": _cost_report("judge")}, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
