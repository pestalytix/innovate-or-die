#!/usr/bin/env python3
"""Grade assertions against run outputs, writing grading.json per arm.

Assertions live in evals/evals.json and are authored AFTER the first run.
Each assertion is either:
  {"text": "...", "check": "<mechanical-check-name>"}   graded by code
  {"text": "..."}                                        graded by an LLM
Mechanical checks are preferred -- they are deterministic and reusable across
iterations. The LLM path shells to `claude -p` with a strict evidence rule.
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ---- mechanical checks: (passed, evidence) from the response text ----------

def _falsifier_with_number(t: str):
    hits = [l for l in t.splitlines()
            if re.search(r"falsif|would (dis)?prove|kill(s)? the thesis", l, re.I)
            and re.search(r"\d", l)]
    return bool(hits), (f"{len(hits)} falsifier line(s) carrying a number; first: "
                        f"{hits[0].strip()[:160]}" if hits else
                        "no line matching a falsifier pattern also contains a number")

def _kill_list_5(t: str):
    m = re.search(r"kill list.*?$", t, re.I | re.M)
    if not m:
        return False, "no section heading matching 'kill list'"
    tail = t[m.end():]
    stop = re.search(r"\n#{1,4}\s", tail)
    block = tail[:stop.start()] if stop else tail
    items = [l for l in block.splitlines() if re.match(r"\s*([-*+]|\d+[.)])\s+\S", l)]
    return len(items) >= 5, f"{len(items)} list item(s) under the kill-list heading"

def _experiment_spec(t: str):
    need = ["hypothesis", "critical assumption", "success threshold",
            "failure threshold", "learned either way"]
    low = t.lower()
    missing = [n for n in need if n not in low]
    return not missing, ("all five required experiment-spec fields present"
                         if not missing else f"missing: {', '.join(missing)}")

def _conventional_labelled(t: str):
    hits = [l for l in t.splitlines()
            if re.search(r"\bconventional\b|\bstandard practice\b|\bwell-established\b", l, re.I)]
    return bool(hits), (f"{len(hits)} line(s) explicitly labelling the conventional option; first: "
                        f"{hits[0].strip()[:160]}" if hits else
                        "no explicit labelling of a conventional winner")

def _thirty_candidates(t: str):
    n = len(re.findall(r"^\s*(?:\d+[.)]|[-*+])\s+\S", t, re.M))
    return n >= 20, f"{n} enumerated items in the visible answer (scaffolding is hidden by design)"

def _delivers_answer(t: str):
    """Stage 0 permits up to three clarifying questions but says to proceed
    regardless. A single-shot run that asks and stops has failed the protocol,
    not the harness -- there is no second turn in `codex exec` / `claude -p`."""
    qs = len(re.findall(r"\?\s*$", t, re.M))
    has_rec = bool(re.search(r"recommend|thesis|opportunit|experiment|hypothes", t, re.I))
    short = len(t) < 1500
    failed = qs >= 2 and (short or not has_rec)
    return (not failed), (f"{qs} question-final line(s), {len(t)} chars, "
                          f"recommendation markers {'present' if has_rec else 'ABSENT'}")


CHECKS = {
    "delivers_answer": _delivers_answer,
    "falsifier_with_number": _falsifier_with_number,
    "kill_list_min_5": _kill_list_5,
    "experiment_spec_complete": _experiment_spec,
    "conventional_winner_labelled": _conventional_labelled,
    "enumerated_options": _thirty_candidates,
}

LLM_PROMPT = """You are grading one assertion against a model's answer.

ASSERTION: {a}

ANSWER:
---
{t}
---

Reply with ONLY a JSON object: {{"passed": true|false, "evidence": "<quote or reference from the answer, max 200 chars>"}}
Require concrete evidence for a pass. A heading without substance beneath it is a FAIL.
Do not give the benefit of the doubt."""


RESOLVED_GRADER: set[str] = set()


def grade_llm(assertion: str, text: str, model: str) -> tuple[bool, str]:
    p = subprocess.run(["claude", "-p", LLM_PROMPT.format(a=assertion, t=text[:60000]),
                        "--model", model, "--output-format", "json"],
                       capture_output=True, text=True, timeout=600)
    try:
        out = json.loads(p.stdout)
        # MODEL_POLICY rule 2: record the resolved grader id, not the alias.
        mu = out.get("modelUsage", {}) or {}
        fam = "-".join(model.split("-")[:2])
        for k in mu:
            if k.startswith(fam):
                RESOLVED_GRADER.add(k)
        raw = out.get("result", "")
        m = re.search(r"\{.*\}", raw, re.S)
        d = json.loads(m.group(0))
        return bool(d["passed"]), str(d.get("evidence", ""))[:200]
    except Exception as e:
        return False, f"grader error: {e}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--provider", required=True)
    ap.add_argument("--tier", required=True, choices=["workhorse", "flagship"])
    ap.add_argument("--grader-model", default="claude-sonnet-5",
                    help="MODEL_POLICY: grader pinned to the workhorse tier")
    ap.add_argument("--mechanical-only", action="store_true",
                    help="skip LLM-graded assertions (zero Claude quota)")
    args = ap.parse_args()

    cases = json.loads((ROOT / "evals/evals.json").read_text())["evals"]
    base = ROOT / "evals-workspace" / f"iteration-{args.iteration}" / args.provider / args.tier

    for c in cases:
        for arm in ("with_skill", "without_skill"):
            d = base / c["slug"] / arm
            resp = d / "outputs" / "response.md"
            if not resp.exists():
                print(f"skip (no output): {c['slug']}/{arm}"); continue
            text = resp.read_text(encoding="utf-8")
            results = []
            for a in c.get("assertions", []):
                a = {"text": a} if isinstance(a, str) else a
                if a.get("check") in CHECKS:
                    ok, ev = CHECKS[a["check"]](text)
                    ev = f"[mechanical:{a['check']}] {ev}"
                    results.append({"text": a["text"], "passed": ok, "evidence": ev,
                                    "grader": "mechanical"})
                elif args.mechanical_only:
                    results.append({"text": a["text"], "passed": None,
                                    "evidence": "NOT GRADED -- LLM grading skipped",
                                    "grader": "skipped"})
                else:
                    ok, ev = grade_llm(a["text"], text, args.grader_model)
                    results.append({"text": a["text"], "passed": ok, "evidence": ev,
                                    "grader": "llm"})
            scored = [r for r in results if r["passed"] is not None]
            passed = sum(bool(r["passed"]) for r in scored)
            (d / "grading.json").write_text(json.dumps({
                "assertion_results": results,
                "summary": {"passed": passed, "failed": len(scored) - passed,
                            "total": len(scored), "not_graded": len(results) - len(scored),
                            "pass_rate": round(passed / len(scored), 4) if scored else None},
                "grader_model_requested": args.grader_model,
                "grader_model_resolved": sorted(RESOLVED_GRADER) or None,
            }, indent=2) + "\n", encoding="utf-8")
            print(f"{c['slug']:34s} {arm:15s} {passed}/{len(scored)}"
                  + (f"  ({len(results)-len(scored)} ungraded)" if len(results) > len(scored) else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
