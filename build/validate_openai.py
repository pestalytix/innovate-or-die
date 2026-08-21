#!/usr/bin/env python3
"""Validate a skills-only plugin package against the OpenAI Plugins Directory.

    python3 build/validate_openai.py dist/innovate-or-die-openai-v2.1.0.zip
    python3 build/validate_openai.py /path/to/extracted/          # same rules
    python3 build/validate_openai.py --rules                      # print the table

Two kinds of rule live here and the distinction is load-bearing:

    OPENAI  a rule the submission portal itself enforces. Breaking it means a
            rejected upload or a rejected listing. Every one carries the source
            page and the date it was read.
    POLICY  ours. The portal would accept the package; we refuse it anyway,
            because the thing it accepts is not the thing we meant to publish.

Both exit 1 -- a package that fails either is not one to submit -- but the two
are labelled separately in the report, so nobody ever has to guess whether a
failure came from OpenAI or from us. A POLICY rule that gets mistaken for an
OPENAI one turns into folklore about the portal; the reverse gets waived by
someone who thinks it is only a house style.

SCOPE: skills-only packages. MCP-backed and app-backed plugins carry a larger
rule set (screenshots, four required listing URLs, domain verification, exactly
five positive and three negative test cases) that is deliberately NOT
implemented here -- an unimplemented rule that looks implemented is worse than
an absent one. What IS enforced is that this package stays skills-only.

This validates the SHIPPED ARTIFACT, not the working tree, for the same reason
build/package.py asserts against the finished zip: what gets uploaded is what
gets checked. Stdlib only, like the rest of build/.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# --------------------------------------------------------------- the rule table
# Every OPENAI rule below was read from the source page on the date shown -- not
# recalled, and not inferred from a sample manifest. Re-read before trusting any
# of it after a portal change; the figures move.

ERRORS_DOC = "https://developers.openai.com/plugins/deploy/submission-errors"
VERIFIED = "2026-08-21"

# Repo decisions, not the portal's. Recorded where the decision was made.
POLICY_SRC = "CHANGELOG.md (Unreleased) + core/listing-openai.json `_note`"

RULES: dict[str, dict] = {
    # -- packaging ------------------------------------------------------------
    "single-plugin-root": dict(
        tag="OPENAI", cls="packaging", source=ERRORS_DOC, verified=VERIFIED,
        rule="ZIP must contain exactly one plugin root, either at the archive "
             "root or in one top-level directory."),
    "no-sibling-files": dict(
        tag="OPENAI", cls="packaging", source=ERRORS_DOC, verified=VERIFIED,
        rule="A ZIP with a top-level plugin directory must not contain sibling "
             "files."),
    "manifest-parses": dict(
        tag="OPENAI", cls="packaging", source=ERRORS_DOC, verified=VERIFIED,
        rule=".codex-plugin/plugin.json must be present, readable UTF-8, and "
             "contain a JSON object at the top level."),
    # -- identity -------------------------------------------------------------
    "name-charset-length": dict(
        tag="OPENAI", cls="identity", source=ERRORS_DOC, verified=VERIFIED,
        rule="`name` must start with an ASCII letter or digit, contain only "
             "ASCII letters, digits, `_` or `-`, and be at most 64 characters."),
    "version-semver": dict(
        tag="OPENAI", cls="identity", source=ERRORS_DOC, verified=VERIFIED,
        rule="`version` must be semantic versioning (e.g. 1.0.0) and at most 64 "
             "characters."),
    # -- listing copy ---------------------------------------------------------
    "display-name-length": dict(
        tag="OPENAI", cls="listing", source=ERRORS_DOC, verified=VERIFIED,
        rule="`interface.displayName` at most 30 characters for final directory "
             "submission (package validation alone allows 80 -- the tighter "
             "limit is the one that decides whether the listing goes live)."),
    "short-description-length": dict(
        tag="OPENAI", cls="listing", source=ERRORS_DOC, verified=VERIFIED,
        rule="`interface.shortDescription` at most 30 characters for final "
             "directory submission (package validation alone allows 240 -- a "
             "package that uploads clean can still be rejected at submission)."),
    "long-description-length": dict(
        tag="OPENAI", cls="listing", source=ERRORS_DOC, verified=VERIFIED,
        rule="`interface.longDescription` at most 4,000 characters. Line breaks "
             "are allowed."),
    "developer-name-length": dict(
        tag="OPENAI", cls="listing", source=ERRORS_DOC, verified=VERIFIED,
        rule="`interface.developerName` at most 80 characters for final "
             "directory submission (package validation alone allows 120)."),
    "category-allowed": dict(
        tag="OPENAI", cls="listing", source=ERRORS_DOC, verified=VERIFIED,
        rule="`interface.category` must be one of the published categories."),
    "capabilities-shape": dict(
        tag="OPENAI", cls="listing", source=ERRORS_DOC, verified=VERIFIED,
        rule="At most 20 capabilities; each non-empty, one line, at most 120 "
             "characters."),
    "default-prompt-shape": dict(
        tag="OPENAI", cls="listing", source=ERRORS_DOC, verified=VERIFIED,
        rule="At most 3 starter prompts; each non-empty, unique after Unicode "
             "and whitespace normalization, one line, at most 128 characters, "
             "and carrying no @mention."),
    # -- branding -------------------------------------------------------------
    "branding-assets": dict(
        tag="OPENAI", cls="branding", source=ERRORS_DOC, verified=VERIFIED,
        rule="`interface.logo` and `interface.composerIcon` are required, must "
             "start with `./`, must be a relative path inside the plugin with no "
             "`..` traversal or drive prefix, must exist in the package, and "
             "must end in .png, .jpg, .jpeg, .webp or .svg."),
    "svg-geometry": dict(
        tag="OPENAI", cls="branding", source=ERRORS_DOC, verified=VERIFIED,
        rule="An SVG branding asset must have <svg> as its root element and "
             "define a numeric square viewBox (or numeric square width/height) "
             "of at least 48x48, as positive finite numbers with no units or "
             "percentages."),
    # -- skills-only ----------------------------------------------------------
    "skills-only-exclusions": dict(
        tag="OPENAI", cls="skills", source=ERRORS_DOC, verified=VERIFIED,
        rule="A skills-only upload must not contain `.mcp.json`, `.app.json`, "
             "`mcpServers`, `apps`, or `interface.screenshots`."),
    "skill-md-present": dict(
        tag="OPENAI", cls="skills", source=ERRORS_DOC, verified=VERIFIED,
        rule="Skills live in `skills/`, each in its own subdirectory containing "
             "a SKILL.md; at least one such skill must be present."),
    "qualified-skill-name-length": dict(
        tag="OPENAI", cls="skills", source=ERRORS_DOC, verified=VERIFIED,
        rule="The combined identifier `plugin-name:skill-name` must not exceed "
             "64 characters."),
    # -- ours -----------------------------------------------------------------
    "author-matches-developer-name": dict(
        tag="POLICY", cls="policy", source=POLICY_SRC, verified=VERIFIED,
        rule="`author.name` must equal `interface.developerName`. The portal "
             "documents these as needing to match OR the selected verified "
             "identity being used for both after confirmation -- i.e. it will "
             "normalise a mismatch away during a manual step. We require them "
             "equal in the artifact, so the published publisher identity is "
             "decided in core/ and not by whatever someone clicks at submission."),
    "cross-manifest-agreement": dict(
        tag="POLICY", cls="policy", source=POLICY_SRC, verified=VERIFIED,
        rule="Where both manifests are present, `.codex-plugin/plugin.json` and "
             "`.claude-plugin/plugin.json` must agree on name, version, license "
             "and the skills path. Publisher identity deliberately differs and "
             "is NOT compared -- see core/listing-openai.json `_note`."),
}

CATEGORIES = {
    "Productivity", "Creativity", "Developer Tools", "Business & Operations",
    "Data & Analytics", "Communication", "Education & Research", "Security",
    "Finance", "Healthcare", "Travel", "Entertainment", "Other",
}

IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".svg")
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$")
MENTION_RE = re.compile(r"(?:^|\s)@\w")

MANIFEST = ".codex-plugin/plugin.json"
CLAUDE_MANIFEST = ".claude-plugin/plugin.json"


class Package:
    """A package as the portal sees it: a flat map of archive paths to bytes.

    Built from a zip or from an extracted directory, so the same rules run on the
    artifact that will be uploaded and on a tree someone is iterating on.
    """

    def __init__(self, entries: dict[str, bytes], label: str):
        self.entries = entries
        self.label = label
        self.root = ""  # set by the packaging rules; "" means archive root

    def path(self, rel: str) -> str:
        return posixpath.join(self.root, rel) if self.root else rel

    def get(self, rel: str) -> bytes | None:
        return self.entries.get(self.path(rel))

    def under_root(self) -> list[str]:
        if not self.root:
            return sorted(self.entries)
        cut = len(self.root) + 1
        return sorted(n[cut:] for n in self.entries if n.startswith(self.root + "/"))


def load_package(target: Path) -> Package:
    entries: dict[str, bytes] = {}
    if target.is_dir():
        for p in sorted(target.rglob("*")):
            if p.is_file():
                entries[p.relative_to(target).as_posix()] = p.read_bytes()
        return Package(entries, target.name)
    with zipfile.ZipFile(target) as z:
        bad = z.testzip()
        if bad is not None:
            raise SystemExit(f"{target.name}: corrupt member {bad!r}")
        for info in z.infolist():
            if not info.filename.endswith("/"):
                entries[info.filename] = z.read(info.filename)
    return Package(entries, target.name)


class Report:
    def __init__(self) -> None:
        self.failures: list[tuple[str, str]] = []   # (rule id, detail)
        self.checked: set[str] = set()

    def ok(self, rule_id: str) -> None:
        self.checked.add(rule_id)

    def fail(self, rule_id: str, detail: str) -> None:
        assert rule_id in RULES, f"unknown rule id {rule_id!r}"
        self.checked.add(rule_id)
        self.failures.append((rule_id, detail))

    def by_tag(self, tag: str) -> list[tuple[str, str]]:
        return [f for f in self.failures if RULES[f[0]]["tag"] == tag]


# ------------------------------------------------------------------- the checks

def _check_packaging(pkg: Package, r: Report) -> dict | None:
    """Locate the plugin root and read the manifest. Returns None if unusable.

    Everything downstream needs the manifest, so a failure here short-circuits:
    reporting forty consequential errors because the root was wrong buries the
    one that matters.
    """
    top_files = sorted({n for n in pkg.entries if "/" not in n})
    top_dirs = sorted({n.split("/", 1)[0] for n in pkg.entries if "/" in n})

    if MANIFEST in pkg.entries:
        pkg.root = ""
        # Manifest at the archive root: the whole archive IS the plugin, so
        # `.codex-plugin` being one of several top-level dirs is expected and
        # correct. There is no sibling to speak of.
        r.ok("single-plugin-root")
        r.ok("no-sibling-files")
    else:
        roots = [d for d in top_dirs if f"{d}/{MANIFEST}" in pkg.entries]
        if len(roots) != 1:
            r.fail("single-plugin-root",
                   f"expected exactly one top-level directory containing "
                   f"{MANIFEST}; found {roots or 'none'} "
                   f"(top-level dirs: {top_dirs})")
            return None
        pkg.root = roots[0]
        r.ok("single-plugin-root")
        strays = [d for d in top_dirs if d != pkg.root]
        if top_files or strays:
            r.fail("no-sibling-files",
                   f"entries beside the {pkg.root}/ plugin root: "
                   f"{sorted(top_files + strays)}")
        else:
            r.ok("no-sibling-files")

    raw = pkg.get(MANIFEST)
    if raw is None:
        r.fail("manifest-parses", f"{pkg.path(MANIFEST)} is not in the package")
        return None
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        r.fail("manifest-parses", f"{pkg.path(MANIFEST)}: {e}")
        return None
    if not isinstance(doc, dict):
        r.fail("manifest-parses",
               f"{pkg.path(MANIFEST)}: top level is {type(doc).__name__}, not an object")
        return None
    r.ok("manifest-parses")
    return doc


def _check_identity(doc: dict, r: Report) -> None:
    name = doc.get("name")
    if not isinstance(name, str) or not name:
        r.fail("name-charset-length", "`name` is missing or not a string")
    elif len(name) > 64:
        r.fail("name-charset-length", f"`name` is {len(name)} chars, max 64")
    elif not NAME_RE.match(name):
        r.fail("name-charset-length",
               f"`name` {name!r} must start with an ASCII letter or digit and "
               f"use only ASCII letters, digits, `_` or `-`")
    else:
        r.ok("name-charset-length")

    version = doc.get("version")
    if not isinstance(version, str) or not version:
        r.fail("version-semver", "`version` is missing or not a string")
    elif len(version) > 64:
        r.fail("version-semver", f"`version` is {len(version)} chars, max 64")
    elif not SEMVER_RE.match(version):
        r.fail("version-semver", f"`version` {version!r} is not semver")
    else:
        r.ok("version-semver")


def _text_rule(iface: dict, field: str, limit: int, rule_id: str, r: Report) -> None:
    value = iface.get(field)
    if not isinstance(value, str) or not value.strip():
        r.fail(rule_id, f"`interface.{field}` is missing or empty")
    elif len(value) > limit:
        r.fail(rule_id, f"`interface.{field}` is {len(value):,} chars, max {limit:,}")
    else:
        r.ok(rule_id)


def _check_listing(doc: dict, r: Report) -> None:
    iface = doc.get("interface")
    if not isinstance(iface, dict):
        iface = {}
    _text_rule(iface, "displayName", 30, "display-name-length", r)
    _text_rule(iface, "shortDescription", 30, "short-description-length", r)
    _text_rule(iface, "longDescription", 4000, "long-description-length", r)
    _text_rule(iface, "developerName", 80, "developer-name-length", r)

    category = iface.get("category")
    if category in CATEGORIES:
        r.ok("category-allowed")
    else:
        r.fail("category-allowed",
               f"`interface.category` {category!r} is not one of "
               f"{sorted(CATEGORIES)}")

    caps = iface.get("capabilities")
    if not isinstance(caps, list) or not caps:
        r.fail("capabilities-shape", "`interface.capabilities` is missing or empty")
    elif len(caps) > 20:
        r.fail("capabilities-shape", f"{len(caps)} capabilities, max 20")
    else:
        bad = []
        for c in caps:
            if not isinstance(c, str) or not c.strip():
                bad.append(f"{c!r}: empty or not a string")
            elif "\n" in c or "\r" in c:
                bad.append(f"{c!r}: must be one line")
            elif len(c) > 120:
                bad.append(f"{c[:40]!r}...: {len(c)} chars, max 120")
        if bad:
            r.fail("capabilities-shape", "; ".join(bad))
        else:
            r.ok("capabilities-shape")

    prompts = iface.get("defaultPrompt")
    if prompts is None:
        # Starter prompts are optional; the cap is on how many, not on having any.
        r.ok("default-prompt-shape")
    elif not isinstance(prompts, list):
        r.fail("default-prompt-shape", "`interface.defaultPrompt` is not a list")
    elif len(prompts) > 3:
        r.fail("default-prompt-shape", f"{len(prompts)} starter prompts, max 3")
    else:
        bad, seen = [], {}
        for p in prompts:
            if not isinstance(p, str) or not p.strip():
                bad.append(f"{p!r}: empty or not a string")
                continue
            if "\n" in p or "\r" in p:
                bad.append(f"{p!r}: must be one line")
            if len(p) > 128:
                bad.append(f"{p[:40]!r}...: {len(p)} chars, max 128")
            if MENTION_RE.search(p):
                bad.append(f"{p!r}: contains an @mention")
            # "unique after Unicode and whitespace normalization" -- two prompts
            # differing only by NBSP, double space or compatibility forms are one
            # prompt as far as the portal is concerned.
            key = " ".join(unicodedata.normalize("NFKC", p).split()).casefold()
            if key in seen:
                bad.append(f"{p!r}: duplicate of {seen[key]!r} after normalization")
            seen[key] = p
        if bad:
            r.fail("default-prompt-shape", "; ".join(bad))
        else:
            r.ok("default-prompt-shape")


def _numeric(token: str) -> float | None:
    """A positive finite number with no unit and no percentage, or None."""
    try:
        value = float(token)
    except ValueError:
        return None
    if value != value or value in (float("inf"), float("-inf")) or value <= 0:
        return None
    return value


def _check_svg(pkg: Package, rel: str, r: Report) -> list[str]:
    raw = pkg.get(rel)
    problems: list[str] = []
    try:
        root = ET.fromstring(raw.decode("utf-8"))
    except (UnicodeDecodeError, ET.ParseError) as e:
        return [f"{rel}: not parseable XML ({e})"]
    tag = root.tag.rsplit("}", 1)[-1]
    if tag != "svg":
        return [f"{rel}: root element is <{tag}>, not <svg>"]

    box = root.get("viewBox")
    if box:
        parts = box.replace(",", " ").split()
        if len(parts) != 4:
            problems.append(f"{rel}: viewBox {box!r} does not have four values")
        else:
            w, h = _numeric(parts[2]), _numeric(parts[3])
            if w is None or h is None:
                problems.append(
                    f"{rel}: viewBox {box!r} width/height are not positive finite "
                    f"numbers without units")
            elif w != h:
                problems.append(f"{rel}: viewBox is {w:g}x{h:g}, not square")
            elif w < 48:
                problems.append(f"{rel}: viewBox is {w:g}x{h:g}, below the 48x48 minimum")
    else:
        w, h = _numeric(root.get("width") or ""), _numeric(root.get("height") or "")
        if w is None or h is None:
            problems.append(
                f"{rel}: no numeric viewBox and no numeric unitless width/height")
        elif w != h:
            problems.append(f"{rel}: {w:g}x{h:g} is not square")
        elif w < 48:
            problems.append(f"{rel}: {w:g}x{h:g} is below the 48x48 minimum")
    return problems


def _check_branding(pkg: Package, doc: dict, r: Report) -> None:
    iface = doc.get("interface") if isinstance(doc.get("interface"), dict) else {}
    problems, svg_problems, svgs_seen = [], [], False

    for field in ("logo", "composerIcon"):
        value = iface.get(field)
        if not isinstance(value, str) or not value:
            problems.append(f"`interface.{field}` is missing")
            continue
        if not value.startswith("./"):
            problems.append(f"`interface.{field}` {value!r} does not start with './'")
            continue
        rel = value[2:]
        if rel.startswith("/") or ".." in rel.split("/") or ":" in rel:
            problems.append(f"`interface.{field}` {value!r} is not a plain relative path")
            continue
        if not rel.lower().endswith(IMAGE_SUFFIXES):
            problems.append(f"`interface.{field}` {value!r} is not one of "
                            f"{', '.join(IMAGE_SUFFIXES)}")
            continue
        if pkg.get(rel) is None:
            problems.append(f"`interface.{field}` points at {value!r}, which is "
                            f"not in the package")
            continue
        if rel.lower().endswith(".svg"):
            svgs_seen = True
            svg_problems += _check_svg(pkg, rel, r)

    if problems:
        r.fail("branding-assets", "; ".join(problems))
    else:
        r.ok("branding-assets")

    if svg_problems:
        r.fail("svg-geometry", "; ".join(dict.fromkeys(svg_problems)))
    elif svgs_seen:
        r.ok("svg-geometry")
    # No SVG asset in the package: nothing to check, and no verdict to record.
    # Raster dimension checks would need an image decoder, so they are out of
    # scope here rather than silently skipped -- see the module docstring.


def _check_skills(pkg: Package, doc: dict, r: Report) -> None:
    members = pkg.under_root()

    banned_files = [m for m in members
                    if posixpath.basename(m) in (".mcp.json", ".app.json")]
    banned_fields = [f for f in ("mcpServers", "apps") if f in doc]
    iface = doc.get("interface") if isinstance(doc.get("interface"), dict) else {}
    if "screenshots" in iface:
        banned_fields.append("interface.screenshots")
    if banned_files or banned_fields:
        r.fail("skills-only-exclusions",
               f"a skills-only package must not carry "
               f"{sorted(banned_files + banned_fields)}")
    else:
        r.ok("skills-only-exclusions")

    skills = sorted({m.split("/")[1] for m in members
                     if m.startswith("skills/") and m.count("/") >= 2
                     and m.split("/", 2)[2].split("/")[0] == "SKILL.md"
                     and m.count("/") == 2})
    if not skills:
        dirs = sorted({m.split("/")[1] for m in members
                       if m.startswith("skills/") and m.count("/") >= 2})
        r.fail("skill-md-present",
               f"no skills/<skill>/SKILL.md in the package "
               f"(skills/ subdirectories present: {dirs or 'none'})")
        r.ok("qualified-skill-name-length")  # nothing to qualify
        return
    r.ok("skill-md-present")

    name = doc.get("name") if isinstance(doc.get("name"), str) else ""
    over = [f"{name}:{s} is {len(name) + 1 + len(s)} chars"
            for s in skills if len(name) + 1 + len(s) > 64]
    if over:
        r.fail("qualified-skill-name-length", "; ".join(over))
    else:
        r.ok("qualified-skill-name-length")


def _check_policy(pkg: Package, doc: dict, r: Report) -> None:
    iface = doc.get("interface") if isinstance(doc.get("interface"), dict) else {}
    author = doc.get("author") if isinstance(doc.get("author"), dict) else {}
    a_name, d_name = author.get("name"), iface.get("developerName")
    if a_name and d_name and a_name == d_name:
        r.ok("author-matches-developer-name")
    else:
        r.fail("author-matches-developer-name",
               f"author.name {a_name!r} != interface.developerName {d_name!r}")

    raw = pkg.get(CLAUDE_MANIFEST)
    if raw is None:
        # The OpenAI asset ships without it, by design -- one manifest per host.
        r.ok("cross-manifest-agreement")
        return
    try:
        other = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        r.fail("cross-manifest-agreement", f"{CLAUDE_MANIFEST}: {e}")
        return
    diffs = [f"{f}: codex {doc.get(f)!r} != claude {other.get(f)!r}"
             for f in ("name", "version", "license", "skills")
             if doc.get(f) != other.get(f)]
    if diffs:
        r.fail("cross-manifest-agreement", "; ".join(diffs))
    else:
        r.ok("cross-manifest-agreement")


def validate(target: Path) -> Report:
    """Run every rule against `target` (a zip or an extracted directory)."""
    pkg = load_package(target)
    r = Report()
    doc = _check_packaging(pkg, r)
    if doc is None:
        return r
    _check_identity(doc, r)
    _check_listing(doc, r)
    _check_branding(pkg, doc, r)
    _check_skills(pkg, doc, r)
    _check_policy(pkg, doc, r)
    return r


# ------------------------------------------------------------------------- cli

def print_rules() -> None:
    for tag in ("OPENAI", "POLICY"):
        ids = [k for k, v in RULES.items() if v["tag"] == tag]
        print(f"\n{tag} -- {len(ids)} rules")
        for rid in ids:
            v = RULES[rid]
            print(f"  {rid}  [{v['cls']}]")
            print(f"    {v['rule']}")
            print(f"    source: {v['source']} (read {v['verified']})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Validate a skills-only plugin package for the OpenAI directory.")
    ap.add_argument("target", nargs="?", type=Path,
                    help="a built .zip, or a directory holding the extracted archive")
    ap.add_argument("--rules", action="store_true",
                    help="print the rule table with sources and exit")
    args = ap.parse_args(argv)

    if args.rules:
        print_rules()
        return 0
    if args.target is None:
        ap.error("a target is required unless --rules is given")
    if not args.target.exists():
        raise SystemExit(f"no such path: {args.target}")

    r = validate(args.target)
    openai_fails, policy_fails = r.by_tag("OPENAI"), r.by_tag("POLICY")

    for label, fails in (("OPENAI", openai_fails), ("POLICY", policy_fails)):
        for rid, detail in fails:
            print(f"{label} FAIL  {rid}")
            print(f"  {detail}")
            print(f"  rule: {RULES[rid]['rule']}")
            print(f"  source: {RULES[rid]['source']} (read {RULES[rid]['verified']})")
            print()

    n_openai = sum(1 for v in RULES.values() if v["tag"] == "OPENAI")
    n_policy = len(RULES) - n_openai
    if openai_fails or policy_fails:
        print(f"FAIL: {len(openai_fails)} OPENAI, {len(policy_fails)} POLICY "
              f"(of {n_openai} OPENAI + {n_policy} POLICY rules, "
              f"{len(r.checked)} evaluated).")
        if policy_fails and not openai_fails:
            print("Every failure above is OURS -- the portal would accept this "
                  "package. It is still not the package we meant to publish.")
        return 1
    print(f"OK: {args.target.name} passes {n_openai} OPENAI + {n_policy} POLICY "
          f"rules ({len(r.checked)} evaluated). Skills-only scope; "
          f"source {ERRORS_DOC}, read {VERIFIED}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
