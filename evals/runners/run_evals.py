#!/usr/bin/env python3
"""Run the paired with_skill / without_skill evals against a subscription CLI.

Each run gets a fresh temp workspace so the skill is discovered project-locally
(.claude/skills/ or .agents/skills/) -- nothing global is mutated, and the
without_skill arm is guaranteed to have no skill in scope.

    python3 evals/runners/run_evals.py --provider claude --model claude-opus-5
    python3 evals/runners/run_evals.py --provider codex  --model gpt-5.6-sol

The RESOLVED model is read back out of the run and recorded per run; the
requested alias is recorded separately and never used to name results.
"""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# A with_skill run drives the full four-role protocol; on hosts with subagents
# it fans out per role, so the ceiling has to be generous.
TIMEOUT_S = int(__import__("os").environ.get("IOD_EVAL_TIMEOUT", "5400"))
SKILL = ROOT / "skills" / "innovate-or-die"


SKILL_NAME = "innovate-or-die"


# ------------------------------------------------------------- provenance
# A number without its provenance cannot be reproduced or trusted later: the
# same command against a different commit, skill version, or CLI build is a
# different experiment. Captured once at run start, recorded per run.

def _sh(*cmd: str) -> str | None:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return (p.stdout or p.stderr).strip().splitlines()[0] if (p.stdout or p.stderr) else None
    except Exception:
        return None


def skill_version() -> tuple[str, str]:
    """Read the version from the skill tree AS IT IS AT RUN TIME, not from a
    hardcoded map. The tree is what the run actually used."""
    m = re.search(r'^\s*version:\s*"?([^"\n]+?)"?\s*$',
                  (SKILL / "SKILL.md").read_text(encoding="utf-8"), re.M)
    if m:
        return m.group(1).strip(), "read:SKILL.md-frontmatter"
    meta = ROOT / "core" / "skill-meta.json"
    if meta.exists():
        return json.loads(meta.read_text())["version"], "read:core/skill-meta.json"
    return "UNKNOWN", "unresolved"


def provenance(provider: str) -> dict:
    ver, how = skill_version()
    cli = {"claude": ("claude", "--version"), "codex": ("codex", "--version"),
           "gemini": ("gemini", "--version")}[provider]
    return {"repo_commit": _sh("git", "-C", str(ROOT), "rev-parse", "HEAD"),
            "repo_dirty": bool(_sh("git", "-C", str(ROOT), "status", "--porcelain")),
            "skill_version": ver,
            "skill_version_method": how,
            "cli_name": cli[0],
            "cli_version": _sh(*cli)}


def assert_uncontaminated(provider: str) -> None:
    """A without_skill arm is only a valid control if the skill is genuinely out
    of scope. Project-local scope is guaranteed by the empty temp cwd, but a
    USER-level install would silently contaminate every control run and make the
    baseline understate the skill. Fail loudly rather than produce quiet garbage.
    """
    homes = [Path.home() / ".claude" / "skills" / SKILL_NAME,
             Path.home() / ".codex" / "skills" / SKILL_NAME,
             Path.home() / ".gemini" / "skills" / SKILL_NAME,
             Path.home() / ".agents" / "skills" / SKILL_NAME]
    found = [h for h in homes if h.exists()]
    if found:
        raise SystemExit(
            "CONTAMINATED CONTROL ARM: the skill is installed at user level and "
            "would be in scope for without_skill runs:\n  "
            + "\n  ".join(str(f) for f in found)
            + "\nUninstall it or run the baseline elsewhere. Refusing to produce "
              "an invalid control.")


def assert_skill_present(ws: Path, provider: str) -> None:
    """Inverse of the contamination assert: a with_skill arm is only valid if the
    skill is actually on disk where the host will look for it. A silently-failed
    copy would make every with_skill run a baseline and manufacture a fake
    'activation reliability' finding."""
    sub = {"claude": ".claude/skills", "gemini": ".gemini/skills"}.get(
        provider, ".agents/skills")
    sk = ws / sub / SKILL_NAME / "SKILL.md"
    if not sk.exists():
        raise SystemExit(f"WITH_SKILL ARM INVALID: {sk} missing -- the skill was not "
                         "copied into the run workspace. Refusing to record a run that "
                         "would look like a non-activation.")


def workspace(arm: str, provider: str) -> Path:
    d = Path(tempfile.mkdtemp(prefix=f"iod-{arm}-"))
    if arm == "with_skill":
        sub = {"claude": ".claude/skills", "gemini": ".gemini/skills"}.get(
            provider, ".agents/skills")
        dest = d / sub / SKILL_NAME
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SKILL, dest)
    return d


TRACE_DIR: Path | None = None   # set per run; raw stream is evidence, keep it


def run_claude(prompt: str, cwd: Path, model: str, effort: str | None = None) -> dict:
    """Uses stream-json so skill ACTIVATION is measured, not inferred.

    `--output-format json` reports no tool calls, so a with_skill run where the
    skill never fired is indistinguishable from one where it did. Observed
    2026-08-19: a run whose description-match failed returned in 36s/41k tokens
    and looked exactly like its own control. Activation is now recorded per run.
    """
    t0 = time.time()
    cmd = ["claude", "-p", prompt, "--model", model,
           "--output-format", "stream-json", "--verbose"]
    if effort:
        cmd += ["--effort", effort]
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT_S)
    dur = int((time.time() - t0) * 1000)
    if TRACE_DIR is not None:      # raw stream = the audit trail for a negative
        TRACE_DIR.mkdir(parents=True, exist_ok=True)
        (TRACE_DIR / "stream.jsonl").write_text(p.stdout, encoding="utf-8")
        if p.stderr:
            (TRACE_DIR / "stderr.txt").write_text(p.stderr, encoding="utf-8")
    activated, skill_args, final = False, None, None
    tools: dict[str, int] = {}
    for line in p.stdout.splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") == "assistant":
            for c in d.get("message", {}).get("content", []):
                if c.get("type") == "tool_use":
                    tools[c["name"]] = tools.get(c["name"], 0) + 1
                    if c["name"] == "Skill":
                        activated = True
                        skill_args = str(c.get("input", {}).get("skill", ""))
        elif d.get("type") == "result":
            final = d
    if final is None:
        return {"text": p.stdout[-4000:] or p.stderr, "resolved_model": "UNKNOWN",
                "total_tokens": 0, "duration_ms": dur, "error": "no result event",
                "activated": activated, "tools": tools}
    mu = final.get("modelUsage", {}) or {}
    # Resolve by requested family first -- Claude reports utility models
    # (e.g. haiku) alongside the pinned one. MODEL_POLICY rule 4.
    if model in mu:
        resolved = model
    else:
        fam = "-".join(model.split("-")[:2])
        same = [k for k in mu if k.startswith(fam)]
        resolved = (same[0] if same else
                    (max(mu, key=lambda k: mu[k].get("outputTokens", 0)) if mu else "UNKNOWN"))
    tok = sum(v.get("inputTokens", 0) + v.get("outputTokens", 0)
              + v.get("cacheReadInputTokens", 0) + v.get("cacheCreationInputTokens", 0)
              for v in mu.values())
    return {"text": final.get("result", ""), "resolved_model": resolved,
            "total_tokens": tok, "duration_ms": final.get("duration_ms", dur),
            "cost_usd": final.get("total_cost_usd"), "all_models": list(mu),
            "activated": activated, "activation_method": "observed:Skill-tool-call",
            "skill": skill_args, "tools": tools, "num_turns": final.get("num_turns")}


def run_codex(prompt: str, cwd: Path, model: str, effort: str | None = None) -> dict:
    """Codex writes the answer to stdout and its banner/accounting to STDERR.

    Verified 2026-08-19 against codex-cli 0.147.0: stdout is the clean answer
    body; stderr carries `model: <resolved>` and a trailing `tokens used\n<n>`.
    Parsing the banner off stdout silently yields UNKNOWN -- caught by
    MODEL_POLICY rule 3 rather than being mistaken for a real mismatch.
    """
    t0 = time.time()
    p = subprocess.run(["codex", "exec", "--skip-git-repo-check", "-s", "read-only",
                        "-m", model, prompt],
                       cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT_S)
    dur = int((time.time() - t0) * 1000)
    err = p.stderr or ""
    resolved = "UNKNOWN"
    for line in err.splitlines():
        s = line.strip()
        if s.startswith("model:"):
            resolved = s.split(":", 1)[1].strip()
            break
    tokens = 0
    if "tokens used" in err:
        tail = err.split("tokens used", 1)[1].strip().splitlines()
        if tail:
            try:
                tokens = int(tail[0].replace(",", "").strip())
            except ValueError:
                pass
    # Codex exposes no tool-call stream, so activation here is a HEURISTIC:
    # protocol-specific structure that a bare answer does not produce.
    body = p.stdout.strip()
    markers = sum(bool(re.search(k, body, re.I)) for k in
                  (r"kill list", r"falsifi", r"contrarian", r"reframing",
                   r"most instructive", r"still missing", r"critical assumption"))
    return {"text": body, "resolved_model": resolved,
            "total_tokens": tokens, "duration_ms": dur, "cost_usd": None,
            "all_models": [resolved], "activated": markers >= 2,
            "activation_method": "heuristic:markers", "marker_count": markers}


def run_gemini(prompt: str, cwd: Path, model: str, effort: str | None = None) -> dict:
    """Gemini CLI leg. `-p` is headless; `-o json` emits a structured envelope.

    UNVALIDATED as of 2026-08-19: the CLI is installed (0.56.0) but has no auth
    configured, so the response envelope's exact field names could not be observed.
    The parser below reads defensively and records `parse_confidence` so a first
    authenticated run reveals any mismatch instead of silently logging zeros.
    """
    t0 = time.time()
    p = subprocess.run(["gemini", "-p", prompt, "-m", model, "-o", "json",
                        "--approval-mode", "plan"],
                       cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT_S)
    dur = int((time.time() - t0) * 1000)
    try:
        d = json.loads(p.stdout)
    except json.JSONDecodeError:
        return {"text": p.stdout or p.stderr, "resolved_model": "UNKNOWN",
                "total_tokens": 0, "duration_ms": dur,
                "error": "non-JSON output", "parse_confidence": "failed"}
    if isinstance(d, dict) and d.get("error"):
        return {"text": "", "resolved_model": "UNKNOWN", "total_tokens": 0,
                "duration_ms": dur, "error": f"gemini error: {d['error'].get('message','')}",
                "parse_confidence": "error-envelope"}

    def dig(obj, *names):
        """Find the first matching key at any depth -- field names unconfirmed."""
        stack = [obj]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                for k, v in o.items():
                    if k in names and not isinstance(v, (dict, list)):
                        return v
                    if isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(o, list):
                stack.extend(o)
        return None

    body = dig(d, "response", "text", "output", "content") or ""
    resolved = dig(d, "model", "modelVersion", "model_version") or "UNKNOWN"
    tokens = dig(d, "totalTokenCount", "total_tokens", "totalTokens") or 0
    markers = sum(bool(re.search(k, str(body), re.I)) for k in
                  (r"kill list", r"falsifi", r"contrarian", r"reframing",
                   r"most instructive", r"still missing", r"critical assumption"))
    return {"text": str(body), "resolved_model": str(resolved),
            "total_tokens": int(tokens or 0), "duration_ms": dur, "cost_usd": None,
            "all_models": [str(resolved)], "activated": markers >= 2,
            "activation_method": "heuristic:markers", "marker_count": markers,
            "parse_confidence": ("ok" if body and resolved != "UNKNOWN"
                                 else "PARTIAL -- verify field names against a real run")}


RUNNERS = {"claude": run_claude, "codex": run_codex, "gemini": run_gemini}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True, choices=sorted(RUNNERS))
    ap.add_argument("--model", required=True, help="requested alias; the RESOLVED id is logged separately")
    ap.add_argument("--tier", required=True, choices=["workhorse", "flagship"],
                    help="MODEL_POLICY tier this pin belongs to")
    ap.add_argument("--effort", default=None,
                    choices=["low", "medium", "high", "xhigh", "max"],
                    help="claude --effort level; recorded in timing.json as configuration. "
                         "Omit for the deployed default condition.")
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--only", help="run a single eval slug")
    ap.add_argument("--arm", choices=["with_skill", "without_skill"],
                    help="run only one arm (default: both)")
    args = ap.parse_args()

    assert_uncontaminated(args.provider)   # control-arm validity gate
    prov = provenance(args.provider)
    print(f"provenance: commit {str(prov['repo_commit'])[:8]}"
          f"{' DIRTY' if prov['repo_dirty'] else ''}  skill v{prov['skill_version']}  "
          f"{prov['cli_name']} {prov['cli_version']}", flush=True)
    cases = json.loads((ROOT / "evals/evals.json").read_text())["evals"]
    if args.only:
        cases = [c for c in cases if c["slug"] == args.only]
    base = (ROOT / "evals-workspace" / f"iteration-{args.iteration}"
            / args.provider / args.tier)

    for c in cases:
        for arm in (("with_skill", "without_skill") if not args.arm else (args.arm,)):
            out = base / c["slug"] / arm
            (out / "outputs").mkdir(parents=True, exist_ok=True)
            if (out / "timing.json").exists():
                print(f"skip (exists): {c['slug']}/{arm}", flush=True); continue
            print(f"RUN {args.provider} {c['slug']} {arm} ...", flush=True)
            globals()["TRACE_DIR"] = out / "trace"
            ws = workspace(arm, args.provider)
            if arm == "with_skill":
                assert_skill_present(ws, args.provider)
            try:
                r = RUNNERS[args.provider](c["prompt"], ws, args.model, args.effort)
            except subprocess.TimeoutExpired:
                r = {"text": "", "resolved_model": "TIMEOUT", "total_tokens": 0,
                     "duration_ms": 1800000, "error": "timeout"}
            finally:
                shutil.rmtree(ws, ignore_errors=True)
            (out / "outputs" / "response.md").write_text(r.pop("text") or "", encoding="utf-8")
            fam = "-".join(args.model.split("-")[:2])
            mismatch = not str(r["resolved_model"]).startswith(fam)
            rec = {"total_tokens": r["total_tokens"], "duration_ms": r["duration_ms"],
                   "requested_model": args.model, "resolved_model": r["resolved_model"],
                   "model_mismatch": mismatch, "tier": args.tier,
                   "cost_usd": r.get("cost_usd"), "provider": args.provider,
                   "all_models": r.get("all_models"),
                   "activated": r.get("activated"),
                   "activation_method": r.get("activation_method") or "unknown:run-failed",
                   "tools": r.get("tools"), "num_turns": r.get("num_turns"),
                   "effort": args.effort or "default (deployed condition)",
                   "parse_confidence": r.get("parse_confidence"),
                   "marker_count": r.get("marker_count"),
                   **prov}
            if arm == "with_skill" and r.get("activated") is False:
                rec["error"] = ("SKILL DID NOT ACTIVATE -- with_skill arm ran as a "
                                "baseline; exclude from headline delta")
            if "error" in r:
                rec["error"] = r["error"]
            if mismatch:
                rec["error"] = (f"MODEL MISMATCH: requested {args.model}, resolved "
                                f"{r['resolved_model']} -- run failed per MODEL_POLICY rule 3")
            (out / "timing.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
            act = "" if arm == "without_skill" else (
                " [activated]" if r.get("activated") else " [NOT ACTIVATED]")
            print(f"  done: {r['resolved_model']}{' MISMATCH!' if mismatch else ''}{act}  "
                  f"{r['total_tokens']:,} tok  {r['duration_ms']/1000:.0f}s", flush=True)
    print("ALL RUNS COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
