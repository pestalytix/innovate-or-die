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
import textwrap
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
    # The OpenAI directory listing is consumer-facing copy plus a publisher
    # identity that is deliberately NOT the author identity (see that file's
    # `_note`). It lives in its own core file so the listing can be edited
    # without touching skill-meta.json, and so nobody has to hand-copy a
    # 4,000-char field into a generated manifest.
    listing = json.loads(read("listing-openai.json"))
    for field in ("publisher", "interface"):
        if field not in listing:
            raise SystemExit(f"core/listing-openai.json missing required field: {field}")
    # core/ carries `{{CORE_VERSION}}` rather than a literal version, so a
    # heading cannot drift from skill-meta.json. Substituted once, here.
    def v(rel: str) -> str:
        return read(rel).replace("{{CORE_VERSION}}", meta["version"])

    return {
        "meta": meta,
        "listing": listing,
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
            # No `version` here on purpose: plugin.json is authoritative for it,
            # and a second copy in the marketplace entry only drifts. Dropped in
            # 01adb87; kept out of the generator so a rebuild cannot restore it.
            "description": " ".join(m["description"].split()).split(". ")[0] + ".",
            "author": {"name": a.get("name", ""), "url": a.get("url", "")},
            "homepage": a.get("url", ""),
            "license": m["license"],
            "keywords": ["innovation", "strategy", "critical-thinking"],
            # Must start with "./": claude.ai marketplace sync rejects a bare
            # ".", which resolves as a plugin name unless metadata.pluginRoot is
            # set, and this marketplace does not set it (01adb87).
            "source": "./",
        }],
    }
    return json.dumps(doc, indent=2) + "\n"


def codex_plugin(c: dict) -> str:
    """The OpenAI/Codex manifest, assembled from two sources that must not merge.

    Identity -- `name`, `version`, `description`, `license`, `keywords`, `skills`
    -- comes from core/skill-meta.json, the same place every other host reads it.
    Publisher identity and the whole `interface` block come from
    core/listing-openai.json, because the OpenAI directory is the ONE surface
    where the publisher is not the author: PESTalytix LLC is the verified
    publisher there, Ken Pendergast is the author everywhere including here.
    The decision, verbatim, is in that file's `_note`.

    `interface` is copied through wholesale rather than field-by-field. A listing
    field added in core/ should reach the manifest by being added in core/, not
    by also editing this function and discovering the omission at submission.
    """
    m = c["meta"]
    listing = c["listing"]
    pub = listing["publisher"]
    doc = {
        "name": m["name"],
        "version": m["version"],
        "description": " ".join(m["description"].split()).split(". ")[0] + ".",
        "author": {"name": pub.get("name", ""), "url": pub.get("url", "")},
        "license": m["license"],
        "keywords": ["innovation", "strategy", "critical-thinking",
                     "assumption-testing", "experimentation"],
        "skills": "./skills/",
        # Keys beginning `_` are ours, not the host's -- notes and comments stay
        # in core/ and never ship inside a manifest a validator will read.
        "interface": {k: v for k, v in listing["interface"].items()
                      if not k.startswith("_")},
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

## You did it wrong if...

This is the most error-prone install path in the project, because the isolation
is yours to maintain rather than the host's. Check yourself against this list
before you trust the output:

- **...two roles shared a chat.** Each role gets a *new* chat, every time. A
  continued chat carries the previous role's framing into the next one.
- **...the innovator's chat contained the critic's tests, the evaluator's
  dimensions, or a kill list.** Stage 1 must not know what Stage 2 checks for.
  An author who knows the filter optimizes for the filter, and the whole design
  exists to prevent exactly that.
- **...you pasted the critic's audit back into the innovator chat and asked for
  a rewrite.** Revision is Stage 3, in `innovate-or-die-reviser`, with a fresh
  context.
- **...the evaluator saw the draft history, the audit, or your own commentary.**
  It receives the proposed final answer and nothing else; anything more turns a
  gate into an agreement.
- **...you skipped the gate because the draft already looked good.** That
  judgement is the one the gate exists to check.
- **...the reviser only polished.** It is required to reopen the territory the
  critic named. Prose improvement with the same candidate set is a skipped stage.
- **...the final answer carries no kill list and no experiment with a pass/fail
  number.** Then the protocol did not run, whatever the individual chats
  produced -- go back rather than ship it.

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

# The single-paste fallback is over every instruction-field cap BY DESIGN -- it
# is the degraded rung, and that is stated wherever it ships. But "knowingly
# over" is not "unbounded": it grows with every protocol version, and past some
# size it stops being a degraded path and becomes one no host will take at all.
# A hard ceiling forces that call to be made deliberately -- raise it in an ADR,
# with a reason -- instead of drifting past it one commit at a time.
FALLBACK_CEILING = 30_000

# An instructions file that fits with almost nothing to spare is not safe, it is
# lucky: the next core edit larger than the headroom turns a passing build into a
# hard failure, and on Gemini it would breach a budget that is only a working
# assumption. Warn while there is still room to act.
INSTRUCTIONS_SLACK = 200

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
    "perplexity-project": ("Perplexity Projects -- Project instructions field", 8000,
                           "REPORTED 2026-08-20: help center says \"up to 8,000 characters\"; "
                           "read via live fetch by the Claude.ai advisory session, NOT "
                           "machine-checkable from this repo (403 to CI-style fetches) "
                           "and not yet paste-tested"),
}

# Targets whose preamble names the host outright instead of saying "this host".
# Naming it grounds the instruction -- the model is told which product's
# limitation it is working around, not just that one exists.
#
# Only the new target is listed. Adding the other three is a one-line change and
# is deliberately not made here: it would rewrite three artifacts that are
# already published and paste-tested, for a wording improvement no evidence asks
# for. Do it in its own commit, with its own headroom check, or not at all.
WEB_PREAMBLE_HOST = {
    "perplexity-project": "Perplexity Projects",
}

# The paragraph the host name is substituted into, quoted at its wrapped width
# because that is how it appears in PREAMBLE_SPLIT. Run through _sub(), so a
# reword of the preamble fails the build rather than silently emitting the
# generic "This host" text under a target that promised to name its host.
PREAMBLE_HOST_ANCHOR = """You are running a four-role innovation protocol **alone, in one context**. This
host provides no context isolation, so fidelity depends on you enforcing it:
run the roles as clearly separated passes, and complete each pass fully before
reading the next role's brief."""

# The width PREAMBLE_SPLIT was authored at. Re-wrapping at any other width would
# reflow lines the host name never touched, so the emitted diff between two
# targets would be the whole paragraph instead of one word. A test asserts that
# filling the anchor with its own words reproduces it byte for byte, which is
# what pins this number to the source rather than to taste.
PREAMBLE_WRAP = 79


def _preamble_host_pair(host: str) -> tuple[str, str]:
    """Swap "This host" for the host's name and re-wrap the paragraph.

    Re-wrapping rather than patching one line: host names differ in length, and
    a substitution that leaves the original line breaks in place produces a
    ragged paragraph whose raggedness varies per target -- a diff that looks
    like an edit every time a name changes. textwrap makes the output a
    function of the text, not of where the old words happened to sit.
    """
    unwrapped = " ".join(PREAMBLE_HOST_ANCHOR.split())
    named = unwrapped.replace("This host provides", f"{host} provides", 1)
    return PREAMBLE_HOST_ANCHOR, textwrap.fill(named, width=PREAMBLE_WRAP)

_HEADER = "<!-- GENERATED from core/ by build/assemble.py -- do not hand-edit. -->"

# Deliberately short. The two paragraphs that used to sit here -- where the role
# briefs live, and that the reading order is load-bearing -- are both said again,
# more specifically, a few hundred characters below by the substituted workflow
# (WF_SPLIT `load` and `isolation`). They were written before the substitution
# tables existed. ADR-004 removed them to pay for the activation banner: the
# duplication cost 396 characters against a cap with 33 to spare. Do not restore
# it without re-measuring -- `--check` is the gate, and it fails.
PREAMBLE_SPLIT = _HEADER + """
# Innovate or Die

You are running a four-role innovation protocol **alone, in one context**. This
host provides no context isolation, so fidelity depends on you enforcing it:
run the roles as clearly separated passes, and complete each pass fully before
reading the next role's brief.

Announce each pass as you begin it.
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
# The leading dot matters -- core/ writes relative references as
# `../references/lenses.md`, and a first-character class that excluded `.` let
# exactly that form through unchecked into single-file surfaces, which is the
# one place it can never resolve.
_REF_RE = re.compile(r"`([A-Za-z0-9_.][A-Za-z0-9_./-]*\.md)`")

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

    def _instructions(target: str) -> str:
        preamble = PREAMBLE_SPLIT
        host = WEB_PREAMBLE_HOST.get(target)
        if host:
            preamble = _sub(preamble, [_preamble_host_pair(host)],
                            f"web preamble for {target}")
        return _join([preamble, "---", c["principles"], "---",
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
        instructions = _instructions(target)
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
            headroom = budget - len(instructions)
            problems.append(
                f"adapters/web/{target}-instructions.md: {len(instructions):,} chars, "
                f"{headroom:,} under the {budget:,} cap for {label}{flag}")
            if headroom < INSTRUCTIONS_SLACK:
                problems.append(
                    f"adapters/web/{target}-instructions.md: SLACK -- only {headroom:,} chars "
                    f"of headroom against {label}{flag}, under the {INSTRUCTIONS_SLACK:,}-char "
                    "slack target. The next core edit larger than that fails the build outright: "
                    "trim in the same commit, or re-verify the cap (docs/COMPATIBILITY.md).")
        problems.append(
            f"adapters/web/{target}-fallback.md: {len(fallback):,} chars, knowingly over the "
            f"{budget:,}-char cap -- degraded no-attachment rung, not the primary install path")

    if len(fallback) > FALLBACK_CEILING:
        # Not a warning. Over-cap is the fallback's accepted condition; over the
        # CEILING is a size nobody decided on.
        fatal.append(
            f"adapters/web/*-fallback.md: {len(fallback):,} chars exceeds the "
            f"{FALLBACK_CEILING:,}-char hard ceiling by {len(fallback)-FALLBACK_CEILING:,}. "
            "The fallback is over every instruction cap by design, but its growth is not "
            "open-ended -- shrink it, or raise FALLBACK_CEILING in an ADR that says why "
            "the larger paste is still worth shipping.")

    drift = readme_fallback_drift(len(fallback))
    if drift:
        problems.append(drift)
    return out


# ---------------------------------------------------------- evals results index
# The only generated artifact whose source is not core/. It is generated from
# the results directory plus the root README's results table, which is the
# point: an index hand-maintained beside the files it indexes goes stale the
# first time someone adds a file and forgets, and a second hand-written summary
# of each result would immediately disagree with the first. So the files supply
# their own titles and dates, the README supplies the one-line labels it already
# carries, and the guard fails the build if those two sets do not match exactly
# -- in either direction.

EVALS_RESULTS_DIR = "evals/results"
EVALS_INDEX = f"{EVALS_RESULTS_DIR}/README.md"

# `| [label](evals/results/file.md) | what it records |` in the root README.
_README_ROW = re.compile(
    r"\|\s*\[[^\]]+\]\(" + EVALS_RESULTS_DIR + r"/([^)]+\.md)\)\s*\|\s*([^|]*?)\s*\|")
_FILENAME_DATE = re.compile(r"^(20\d\d-\d\d-\d\d)-")


def _plain(t: str) -> str:
    """Strip markdown emphasis and code spans from text lifted into the index.

    Two reasons, both load-bearing: a truncated bold span emits broken markdown,
    and a backticked `*.md` filename surviving into the index would trip
    check_references() against a directory it does not model.
    """
    return " ".join(re.sub(r"[`*_]", "", t).split())


def evals_results_index(fatal: list[str]) -> dict[str, str]:
    d = ROOT / EVALS_RESULTS_DIR
    readme_path = ROOT / "README.md"
    if not d.is_dir() or not readme_path.exists():
        return {}

    labels = {m.group(1): _plain(m.group(2))
              for m in _README_ROW.finditer(readme_path.read_text(encoding="utf-8"))}
    on_disk = {f.name for f in d.glob("*.md")} - {"README.md"}

    for name in sorted(set(labels) - on_disk):
        fatal.append(f"README.md links {EVALS_RESULTS_DIR}/{name} in its results table, "
                     "but no such file exists")
    rows = []
    for name in sorted(on_disk):
        text = (d / name).read_text(encoding="utf-8")
        title = next((l[2:].strip() for l in text.splitlines()[:5] if l.startswith("# ")), "")
        date = _FILENAME_DATE.match(name)
        label = labels.get(name)
        # Each of these is a way the index would silently thin out rather than
        # fail: an untitled file, a file named outside the date convention, or a
        # result nobody has described in the README.
        missing = [n for n, v in (("an H1 title", title),
                                  ("a leading ISO date in its filename", date),
                                  ("a row in the root README results table", label)) if not v]
        if missing:
            fatal.append(f"{EVALS_RESULTS_DIR}/{name}: cannot be indexed -- missing "
                         + " and ".join(missing))
            continue
        rows.append((date.group(1), name, _plain(title), label))
    if not rows:
        return {}
    rows.sort(reverse=True)

    head = [_HEADER, "# Eval results",
            "Every eval write-up in this directory, newest first. **Generated** by "
            "`build/assemble.py` from these files and the results table in the root "
            "README -- add a result, give it a row there, and it appears here. Do not "
            "hand-edit.",
            "Each file states its own method and its own limits, and they differ: read "
            "those before quoting any number. Across all of them the eval measures "
            "protocol compliance and cost, not decision quality.",
            "The date is the date in the filename -- when the runs happened. Several "
            "files were written or annotated later, and say so."]
    table = ["| Date | Result | What it records |", "|---|---|---|"]
    table += [f"| {date} | [{title}]({name}) | {label} |" for date, name, title, label in rows]
    return {EVALS_INDEX: "\n\n".join(head) + "\n\n" + "\n".join(table) + "\n"}


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
    files.update(evals_results_index(fatal))

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
