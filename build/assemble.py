#!/usr/bin/env python3
"""Assemble every generated tree from core/.

Source of truth is core/. Nothing here is hand-edited; run this instead.

    python3 build/assemble.py            # write
    python3 build/assemble.py --dry-run  # show what would change
    python3 build/assemble.py --check    # CI drift guard: exit 1 if committed != generated

Stdlib only, so it runs anywhere without an install step -- core/skill-meta.json
is JSON precisely so no YAML parser is needed. YAML is only ever *written*
(SKILL.md frontmatter), which is the safe direction.
"""

from __future__ import annotations

import argparse
import difflib
import json
import posixpath
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "core"

# ---------------------------------------------------------------- core loading

ROLE_ORDER = ["innovator", "critic", "reviser", "evaluator"]  # execution order


def read(rel: str) -> str:
    return (CORE / rel).read_text(encoding="utf-8")


def load_core() -> dict:
    meta = json.loads(read("skill-meta.json"))
    for field in ("name", "version", "license", "description"):
        if field not in meta:
            raise SystemExit(f"core/skill-meta.json missing required field: {field}")
    # core/ carries `{{CORE_VERSION}}` rather than a literal version, so a
    # heading cannot drift from skill-meta.json. Substituted once, here.
    def v(rel: str) -> str:
        return read(rel).replace("{{CORE_VERSION}}", meta["version"])

    return {
        "meta": meta,
        "principles": v("principles.md"),
        "workflow": v("workflow.md"),
        "roles": {r: v(f"roles/{r}.md") for r in ROLE_ORDER},
        "lenses": v("references/lenses.md"),
        "experiment": v("references/experiment-spec.md"),
    }


# ------------------------------------------------------- agentskills.io limits
# Verified 2026-08-19 against https://agentskills.io/specification -- see
# docs/COMPATIBILITY.md. Allowed frontmatter keys are exactly:
#   name description license compatibility metadata allowed-tools
NAME_MAX, DESC_MAX = 64, 1024
SKILL_ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def yaml_escape(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_skill_md(c: dict, problems: list[str]) -> str:
    m = c["meta"]
    name, desc = m["name"], " ".join(m["description"].split())

    if len(name) > NAME_MAX:
        problems.append(f"SKILL.md name is {len(name)} chars (spec max {NAME_MAX})")
    if len(desc) > DESC_MAX:
        problems.append(f"SKILL.md description is {len(desc)} chars (spec max {DESC_MAX})")

    author = m.get("author", {})
    fm = [
        "---",
        f"name: {name}",
        f"description: {yaml_escape(desc)}",
        f"license: {m['license']}",
        "metadata:",
        f"  version: {yaml_escape(m['version'])}",
    ]
    # version/author are NOT top-level spec keys -- they belong under metadata,
    # whose values must be strings.
    if isinstance(author, dict):
        if author.get("name"):
            fm.append(f"  author: {yaml_escape(author['name'])}")
        if author.get("url"):
            fm.append(f"  author_url: {yaml_escape(author['url'])}")
    elif author:
        fm.append(f"  author: {yaml_escape(str(author))}")
    fm.append("---")
    return "\n".join(fm) + "\n\n" + c["workflow"].lstrip("\n")


def skill_package(c: dict, problems: list[str]) -> dict[str, str]:
    """The canonical Agent Skills package. Paths inside SKILL.md resolve
    because this mirrors core/'s own layout (principles.md at root, roles/ and
    references/ as siblings)."""
    files = {
        "SKILL.md": build_skill_md(c, problems),
        "principles.md": c["principles"],
        "references/lenses.md": c["lenses"],
        "references/experiment-spec.md": c["experiment"],
    }
    for r in ROLE_ORDER:
        files[f"roles/{r}.md"] = c["roles"][r]
    return files


# ------------------------------------------------------------------ manifests

def claude_plugin(c: dict) -> str:
    m = c["meta"]
    a = m.get("author", {})
    doc = {
        "name": m["name"],
        "displayName": "Innovate or Die",
        "version": m["version"],
        "description": " ".join(m["description"].split()).split(". ")[0] + ".",
        "author": {"name": a.get("name", ""), "url": a.get("url", "")},
        "homepage": a.get("url", ""),
        "repository": "https://github.com/pestalytix/innovate-or-die",
        "license": m["license"],
        "keywords": ["innovation", "strategy", "critical-thinking",
                     "assumption-testing", "experimentation"],
        "skills": "./skills/",
    }
    return json.dumps(doc, indent=2) + "\n"


def claude_marketplace(c: dict) -> str:
    """Schema verified 2026-08-19 against `claude plugin validate` itself, not
    the docs page: `owner` is REQUIRED, and `source` is a relative-path string
    (or an object) -- there is no `sourceDetails` field. The plugin lives at the
    root of this same repo, so its source is "."."""
    m = c["meta"]
    a = m.get("author", {})
    doc = {
        "name": "pestalytix",
        "description": "Plugins by Ken Pendergast.",
        "owner": {"name": a.get("name", ""), "url": a.get("url", "")},
        "plugins": [{
            "name": m["name"],
            "displayName": "Innovate or Die",
            "version": m["version"],
            "description": " ".join(m["description"].split()).split(". ")[0] + ".",
            "author": {"name": a.get("name", ""), "url": a.get("url", "")},
            "homepage": a.get("url", ""),
            "license": m["license"],
            "keywords": ["innovation", "strategy", "critical-thinking"],
            "source": ".",
        }],
    }
    return json.dumps(doc, indent=2) + "\n"


def codex_plugin(c: dict) -> str:
    m = c["meta"]
    a = m.get("author", {})
    doc = {
        "name": m["name"],
        "version": m["version"],
        "description": " ".join(m["description"].split()).split(". ")[0] + ".",
        "author": {"name": a.get("name", ""), "url": a.get("url", "")},
        "license": m["license"],
        "keywords": ["innovation", "strategy", "critical-thinking",
                     "assumption-testing", "experimentation"],
        "skills": "./skills/",
        "interface": {
            "displayName": "Innovate or Die",
            "shortDescription": "Find bold ideas that survive reality checks",
            "longDescription": ("A staged innovation workflow that generates unconventional "
                                "hypotheses, attacks them in isolation, revises the survivors, "
                                "and converts the strongest ideas into cheap falsifiable tests."),
            "developerName": a.get("name", ""),
            "category": "Productivity",
            "capabilities": ["Interactive"],
            "defaultPrompt": [
                "Find a non-obvious solution to this problem.",
                "Challenge the assumptions behind this strategy.",
                "Turn this idea into falsifiable experiments.",
            ],
        },
    }
    return json.dumps(doc, indent=2) + "\n"


# ------------------------------------------------------- copilot .agent.md set
# Frontmatter keys verified 2026-08-19 against
# https://code.visualstudio.com/docs/agent-customization/custom-agents

ROLE_BLURB = {
    "innovator": "Stage 1 divergent search. Run this first, in a fresh chat.",
    "critic": "Stage 2 adversarial audit. Fresh chat -- paste only the problem and the innovator draft.",
    "reviser": "Stage 3 reopen, select finalists, push further. Fresh chat.",
    "evaluator": "Stage 4 scored quality gate. Fresh chat -- paste only the proposed final answer.",
}


def agent_profiles(c: dict) -> dict[str, str]:
    out = {}
    for r in ROLE_ORDER:
        body = c["roles"][r]
        if r == "innovator":  # the lens bank is the innovator's working reference
            body = _sub(body, REF_LENS_INLINE, "copilot innovator") \
                + "\n\n---\n\n" + c["lenses"]
        if r == "reviser":    # the experiment spec is the reviser's working reference
            # These profiles install as bare .agent.md copies, so a reference to
            # ../references/ resolves to nothing. Carry the spec instead.
            body = _sub(body, REF_EXP_INLINE, "copilot reviser") \
                + "\n\n---\n\n" + c["experiment"]
        fm = ["---", f"name: innovate-or-die-{r}",
              f"description: {yaml_escape(ROLE_BLURB[r])}", "---", ""]
        out[f"innovate-or-die-{r}.agent.md"] = "\n".join(fm) + body
        
    handoff = "\n".join(
        f"{n}. **{r.capitalize()}** -- open a new chat with `innovate-or-die-{r}`. {ROLE_BLURB[r]}"
        for n, r in enumerate(ROLE_ORDER, 1))
    orch = f"""---
name: innovate-or-die
description: {yaml_escape("Orchestrator for the four-role innovation protocol. Directs a fresh chat per role so each stage stays isolated.")}
---

# Innovate or Die -- orchestrator

This host does not give the roles isolated contexts automatically. **You must
create the isolation by hand: one fresh chat per role, in this order.** Carrying
one chat through all four stages recreates the anchoring failure the protocol
exists to defeat.

{handoff}

Between stages, hand forward **only** what the next role is entitled to see:

- Critic receives the original problem, relevant evidence, and the innovator
  draft -- nothing about what the critic checks for reaches the innovator first.
- Reviser receives the original problem, the draft, and the critic audit.
- Evaluator receives only the proposed final answer.

Then assemble the final answer in the Stage 6 order below.

---

{c['principles']}

---

{_sub(c['workflow'], WF_COPILOT, 'copilot orchestrator')}
"""
    out["innovate-or-die.agent.md"] = orch
    return out


# ------------------------------------------------------ flattened web variants
# Character budgets verified 2026-08-19 -- see docs/COMPATIBILITY.md.
# Each target emits three files:
#   <t>-instructions.md  preamble + principles + workflow   (must fit the cap)
#   <t>-knowledge.md     roles in execution order + lenses + experiment spec
#   <t>-fallback.md      the whole thing in one file, for hosts without
#                        attachments -- knowingly over budget, the degraded rung
WEB_TARGETS = {
    # (label, budget, status) -- status is a human string, not a bool, because
    # "verified hard cap" and "accepted our file but true cap unknown" are
    # different epistemic states and the warning text must say which.
    "chatgpt-gpt":  ("ChatGPT Custom GPT -- Instructions field", 8000,
                     "VERIFIED 2026-08-19: 8,000 hard cap confirmed in the GPT builder UI"),
    "gemini-gem":   ("Gemini Gem -- Instructions field", 8000,
                     "WORKING BUDGET: Gem accepted the full instructions file 2026-08-19, "
                     "so the cap is >= that size; exact cap unknown"),
    "m365-copilot": ("M365 Copilot Agent Builder -- Instructions field", 8000,
                     "VERIFIED 2026-08-19: Microsoft Learn, Instructions field 8,000 chars"),
}

_HEADER = "<!-- GENERATED from core/ by build/assemble.py -- do not hand-edit. -->"

PREAMBLE_SPLIT = _HEADER + """
# Innovate or Die

You are running a four-role innovation protocol **alone, in one context**. This
host provides no context isolation, so fidelity depends on you enforcing it:
run the roles as clearly separated passes, and complete each pass fully before
reading the next role's brief.

The four role briefs, the lens bank, and the experiment spec live in the
**attached knowledge file**. Read each role's section at its stage, not before.

**This ordering is load-bearing.** Do not read the Critic or Evaluator sections
until your Innovator pass is complete. Their criteria in context during the
divergent search recreates the self-censoring that role separation exists to
prevent. Announce each pass as you begin it.
"""

PREAMBLE_FALLBACK = _HEADER + """
# Innovate or Die

You are running a four-role innovation protocol **alone, in one context**. This
host provides no context isolation, so fidelity depends on you enforcing it:
run the roles as clearly separated passes, and complete each pass fully before
reading the next role's section.

**This ordering is load-bearing.** Do not read the Critic or Evaluator sections
until your Innovator pass is complete. Their criteria in context during the
divergent search recreates the self-censoring that role separation exists to
prevent. Announce each pass as you begin it.

*(Degraded variant: this host cannot take an attached knowledge file, so every
section is inlined here and the whole document is in context from the start.)*
"""


def _join(parts: list[str]) -> str:
    return "\n\n".join(p.strip("\n") for p in parts) + "\n"


# README.md describes the fallback's size in prose, and the fallback grows with
# every protocol version -- so a hard figure there goes stale silently. Warn when
# prose and artifact diverge; stay quiet when the prose uses an approximate form
# ("~20k chars") that never needs updating. A warning, not a failure: a stale
# adjective in the README does not make a generated artifact wrong.
README_DRIFT_TOLERANCE = 0.10


def readme_fallback_drift(fallback_len: int) -> str | None:
    """Return a warning if README.md quotes a fallback size that has drifted."""
    path = ROOT / "README.md"
    if not path.exists():
        return None
    para = re.search(r"Single-paste fallback\.(.*?)(?=\n\n)",
                     path.read_text(encoding="utf-8"), re.S)
    if not para:
        return None
    # Both forms are checked. The loose "~25k chars" phrasing ages more slowly
    # than an exact figure, but it still ages: inlining the lens bank moved the
    # fallback from ~20k to ~25k and the loose form went stale silently, which
    # is precisely what this check exists to prevent.
    text = para.group(1)
    quoted = re.search(r"([0-9][0-9,]*)\s*k\b", text, re.I)
    if quoted:
        n = int(quoted.group(1).replace(",", "")) * 1000
    else:
        quoted = re.search(r"([0-9][0-9,]{2,})\s*chars", text)
        if not quoted:
            return None
        n = int(quoted.group(1).replace(",", ""))
    if abs(n - fallback_len) <= README_DRIFT_TOLERANCE * fallback_len:
        return None
    return (f"README.md quotes the single-paste fallback at {n:,} chars; it is now "
            f"{fallback_len:,} -- more than {README_DRIFT_TOLERANCE:.0%} off. Either "
            f"update it or use an approximate phrasing that cannot drift.")



# ------------------------------------------------------- reference resolution
# core/ is authored for the canonical skill package, where `roles/critic.md`
# and `../references/lenses.md` are real files. Every other surface FLATTENS
# that layout, so a path copied through verbatim tells the model to open
# something the install cannot reach -- and the model either invents the
# contents or drops the step. Each context declares how the core's references
# render there, and check_references() fails the build if a path survives into
# a surface that cannot resolve it.

def _sub(text: str, pairs: list[tuple[str, str]], ctx: str) -> str:
    """Literal substitution that REFUSES to no-op.

    `str.replace` returns the string unchanged when its anchor drifts, which is
    exactly how a broken reference survives a green build. If core/ rewording
    breaks an anchor, fail here rather than ship an artifact whose instructions
    point at a file that does not exist.
    """
    for old, new in pairs:
        if old not in text:
            raise SystemExit(
                f"assemble.py: reference anchor missing for {ctx}:\n  {old[:90]!r}\n"
                "core/ wording changed -- update the REF_* tables in build/assemble.py.")
        text = text.replace(old, new)
    return text


LOAD_SENTENCE = (
    "Read `principles.md` now. Load each role file at its stage, not before: "
    "`roles/innovator.md` (with `references/lenses.md`) at Stage 1; `roles/critic.md` "
    "at Stage 2; `roles/reviser.md` at Stage 3; `roles/evaluator.md` at Stage 4; "
    "`references/experiment-spec.md` when assembling the final answer.")

ISOLATION_CLAUSE = ("do not read `roles/critic.md` or `roles/evaluator.md` before "
                    "Stage 1 is complete")

# Stage headers that name a role file, shared by every context.
_STAGE_ANCHORS = [
    ("Follow `roles/innovator.md` in full", "innovator"),
    ("Follow `roles/critic.md`.", "critic"),
    ("Follow `roles/reviser.md` with", "reviser"),
    ("Follow `roles/evaluator.md`.", "evaluator"),
]
_EXPERIMENT_ANCHOR = "full spec per `references/experiment-spec.md`"


def _workflow_pairs(load: str, isolation: str, stage: dict, experiment: str):
    pairs = [(LOAD_SENTENCE, load), (ISOLATION_CLAUSE, isolation)]
    pairs += [(a, a.replace(f"`roles/{r}.md`", stage[r])) for a, r in _STAGE_ANCHORS]
    pairs += [(_EXPERIMENT_ANCHOR, experiment)]
    return pairs


# Everything inlined in one document (web fallback).
WF_SINGLE = _workflow_pairs(
    load=("Everything the method needs is in **this document**. The **Operating "
          "principles** section above applies throughout. Work each role's section at "
          "its stage, not before: **Innovator** (with the **Lens bank**) at Stage 1; "
          "**Critic** at Stage 2; **Reviser** at Stage 3; **Evaluator** at Stage 4; the "
          "**Experiment spec** section when assembling the final answer."),
    isolation="do not read the **Critic** or **Evaluator** sections before Stage 1 is complete",
    stage={r: f"the **{r.capitalize()}** section" for r in ROLE_ORDER},
    experiment="full spec per the **Experiment spec** section of this document")

# Instructions file; the role briefs live in the attached knowledge file.
WF_SPLIT = _workflow_pairs(
    load=("Read the **Operating principles** below now. The role briefs, lens bank, "
          "and experiment spec are in the **attached knowledge file** -- read each at "
          "its stage, not before: **Innovator** (with the **Lens bank**) at Stage 1; "
          "**Critic** at Stage 2; **Reviser** at Stage 3; **Evaluator** at Stage 4; the "
          "**Experiment spec** when assembling the final answer."),
    isolation=("do not read the **Critic** or **Evaluator** briefs before Stage 1 is "
               "complete"),
    stage={r: f"the **{r.capitalize()}** brief" for r in ROLE_ORDER},
    experiment="full spec per the **Experiment spec** in the knowledge file")

# Copilot orchestrator; each role is a separate .agent.md profile.
WF_COPILOT = _workflow_pairs(
    load=("The **Operating principles** section below applies throughout. Open a fresh "
          "chat per role at its stage, not before: `innovate-or-die-innovator` (which "
          "carries the lens bank) at Stage 1; `innovate-or-die-critic` at Stage 2; "
          "`innovate-or-die-reviser` at Stage 3 (which carries the experiment spec); "
          "`innovate-or-die-evaluator` at Stage 4."),
    isolation=("do not open the critic or evaluator profiles before Stage 1 is complete"),
    stage={r: f"the `innovate-or-die-{r}` profile" for r in ROLE_ORDER},
    experiment=("full spec per the **Experiment spec** carried in the "
                "`innovate-or-die-reviser` profile"))

# Role-brief references, by what the surrounding artifact actually carries.
LENS_ANCHOR = "from `../references/lenses.md`"
EXPSPEC_ANCHOR = "per `../references/experiment-spec.md`"
REF_LENS_INLINE = [(LENS_ANCHOR, "from the **Lens bank** included with this brief")]
REF_LENS_DOC = [(LENS_ANCHOR, "from the **Lens bank** section of this document")]
REF_EXP_INLINE = [(EXPSPEC_ANCHOR, "per the **Experiment spec** included with this brief")]
REF_EXP_DOC = [(EXPSPEC_ANCHOR, "per the **Experiment spec** section of this document")]


# A markdown-quoted filename. Deliberately narrow: it matches the form core/
# actually uses, so a prose mention of "a .md file" does not trip the check.
_REF_RE = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.md)`")

# Surfaces that ship as ONE file. Nothing relative can resolve from them.
_SINGLE_FILE_PREFIXES = ("adapters/web/", "adapters/copilot/agents/")


def check_references(files: dict[str, str], fatal: list[str]) -> None:
    """Every relative file reference must resolve in its own install context.

    Repo-tree artifacts resolve against the generated tree; single-file
    artifacts (web adapters, agent profiles) are installed alone, so any file
    reference in them is unresolvable by construction.
    """
    tree = set(files)
    for rel, content in sorted(files.items()):
        if not rel.endswith(".md"):
            continue
        refs = sorted(set(_REF_RE.findall(content)))
        if not refs:
            continue
        if rel.startswith(_SINGLE_FILE_PREFIXES):
            fatal.append(
                f"{rel}: installs as a single file but references "
                + ", ".join(f"`{r}`" for r in refs)
                + " -- nothing relative can resolve there; inline it or name the section")
            continue
        base = posixpath.dirname(rel)
        for r in refs:
            target = posixpath.normpath(posixpath.join(base, r))
            if target not in tree:
                fatal.append(f"{rel}: reference `{r}` resolves to {target}, "
                             "which the generated tree does not contain")


def web_variants(c: dict, problems: list[str], fatal: list[str]) -> dict[str, str]:
    # Role briefs, with their own references pointed at whatever the
    # containing document actually carries.
    def _roles(lens_pairs, exp_pairs):
        out = []
        for r in ROLE_ORDER:
            body = c["roles"][r]
            if r == "innovator":
                body = _sub(body, lens_pairs, f"web role {r}")
            if r == "reviser":
                body = _sub(body, exp_pairs, f"web role {r}")
            out += ["---", body]
        return out

    instructions = _join([PREAMBLE_SPLIT, "---", c["principles"], "---",
                          _sub(c["workflow"], WF_SPLIT, "web instructions")])
    knowledge = _join([_HEADER, "# Innovate or Die -- role briefs and references",
                       "Read each section at its stage, as the instructions direct.",
                       *_roles(REF_LENS_DOC, REF_EXP_DOC),
                       "---", c["lenses"], "---", c["experiment"]])
    # The fallback is the whole method in one paste: the lens bank must be
    # HERE, not referenced. Its absence was the defect this inlining fixes --
    # the text demanded eight lenses from a file the paste never carried.
    fallback = _join([PREAMBLE_FALLBACK, "---", c["principles"], "---",
                      _sub(c["workflow"], WF_SINGLE, "web fallback"),
                      *_roles(REF_LENS_DOC, REF_EXP_DOC),
                      "---", c["lenses"], "---", c["experiment"]])

    out = {}
    for target, (label, budget, status) in WEB_TARGETS.items():
        out[f"{target}-instructions.md"] = instructions
        out[f"{target}-knowledge.md"] = knowledge
        out[f"{target}-fallback.md"] = fallback

        flag = f" [{status.split(':')[0]}]"
        if len(instructions) > budget:
            # Hard failure: the instructions file is the primary install path.
            # An over-cap instructions file cannot be pasted, so the artifact is
            # unusable -- unlike the fallback, which is over budget by design.
            fatal.append(
                f"adapters/web/{target}-instructions.md: {len(instructions):,} chars exceeds "
                f"the {budget:,}-char cap for {label}{flag} -- over by {len(instructions)-budget:,}")
        else:
            problems.append(
                f"adapters/web/{target}-instructions.md: {len(instructions):,} chars, "
                f"{budget - len(instructions):,} under the {budget:,} cap for {label}{flag}")
        problems.append(
            f"adapters/web/{target}-fallback.md: {len(fallback):,} chars, knowingly over the "
            f"{budget:,}-char cap -- degraded no-attachment rung, not the primary install path")

    drift = readme_fallback_drift(len(fallback))
    if drift:
        problems.append(drift)
    return out


# --------------------------------------------------------------- tree assembly

def generate() -> tuple[dict[str, str], list[str], list[str]]:
    c = load_core()
    problems: list[str] = []
    fatal: list[str] = []

    files: dict[str, str] = {}
    pkg = skill_package(c, problems)
    for base in ("skills/innovate-or-die",
                 ".agents/skills/innovate-or-die",
                 ".github/skills/innovate-or-die"):
        for rel, content in pkg.items():
            files[f"{base}/{rel}"] = content

    files[".claude-plugin/plugin.json"] = claude_plugin(c)
    files[".claude-plugin/marketplace.json"] = claude_marketplace(c)
    files[".codex-plugin/plugin.json"] = codex_plugin(c)

    for fname, content in agent_profiles(c).items():
        files[f"adapters/copilot/agents/{fname}"] = content
    for fname, content in web_variants(c, problems, fatal).items():
        files[f"adapters/web/{fname}"] = content

    check_references(files, fatal)
    for rel, content in sorted(files.items()):
        if "{{" in content:
            leftover = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", content)))
            fatal.append(f"{rel}: unsubstituted placeholder(s) {leftover} shipped")
    return files, problems, fatal


def main() -> int:
    ap = argparse.ArgumentParser(description="Assemble generated trees from core/.")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="report changes, write nothing")
    g.add_argument("--check", action="store_true", help="exit 1 if committed trees differ")
    args = ap.parse_args()

    files, problems, fatal = generate()
    created, changed, unchanged, diffs = [], [], [], []

    for rel, content in sorted(files.items()):
        path = ROOT / rel
        if not path.exists():
            created.append(rel)
        elif path.read_text(encoding="utf-8") != content:
            changed.append(rel)
            if args.check:
                diffs.append("\n".join(difflib.unified_diff(
                    path.read_text(encoding="utf-8").splitlines(),
                    content.splitlines(),
                    fromfile=f"committed/{rel}", tofile=f"generated/{rel}", lineterm="")))
        else:
            unchanged.append(rel)

    if args.check:
        if fatal:
            print("FAIL: a generated artifact is unusable as shipped.\n")
            for f in fatal:
                print(f"  error: {f}")
            print("\nCaps live in WEB_TARGETS (sources in docs/COMPATIBILITY.md); "
                  "reference rendering lives in the REF_*/WF_* tables.")
            return 1
        if created or changed:
            print("DRIFT: committed trees do not match core/.\n")
            for rel in created:
                print(f"  missing:  {rel}")
            for rel in changed:
                print(f"  stale:    {rel}")
            if diffs:
                print("\n" + "\n\n".join(diffs[:5]))
            print("\nRun: python3 build/assemble.py")
            return 1
        print(f"OK: {len(unchanged)} generated files match core/.")
        for p in problems:
            print(f"  warning: {p}")
        return 0

    if not args.dry_run:
        for rel, content in files.items():
            path = ROOT / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    verb = "would write" if args.dry_run else "wrote"
    print(f"{verb} {len(files)} files: {len(created)} new, {len(changed)} changed, "
          f"{len(unchanged)} unchanged")
    for f in fatal:
        print(f"  ERROR:   {f}")
    for p in problems:
        print(f"  warning: {p}")
    if fatal:
        print("  -> `--check` will fail on this. A generated artifact is unusable "
              "as shipped: over its cap, or referencing a file its install cannot reach.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
