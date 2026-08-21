"""Guards on the OpenAI directory validator.

The validator's whole job is to fail *here* rather than at a submission portal,
where the feedback is a generic rejection and the turnaround is days. So each
rule class is handed the mistake it exists to catch, built by mutating a copy of
the package we actually intend to publish -- not a hand-written stub, which
could drift into passing rules the real package would fail.

One negative per rule *class*, not per rule: nineteen near-identical tests would
be maintained by nobody and would still only prove the same wiring nineteen
times. What is asserted per rule is that every one of them is reachable -- see
test_the_positive_control_evaluates_every_rule, which fails the moment a rule is
added to the table and never wired into a check.

The positive control is load-bearing for the same reason it is in
test_package.py: negative tests all pass against a validator that rejects
everything, including the real asset.
"""
from __future__ import annotations

import json
import shutil

import pytest

PLUGIN_ROOT = "innovate-or-die"
PKG_DIR = "skills/innovate-or-die"


@pytest.fixture
def pkg(root, tmp_path):
    """A valid plugin package on disk, copied from the working tree.

    The validator reads a zip or a directory identically, and a directory is what
    a mutation test needs. build/package.py's own tests cover the zip path.
    """
    dest = tmp_path / "pkg" / PLUGIN_ROOT
    for rel in (".codex-plugin", PKG_DIR, "assets"):
        shutil.copytree(root / rel, dest / rel)
    shutil.copy(root / "LICENSE", dest / "LICENSE")
    return tmp_path / "pkg"


def manifest(pkg) -> dict:
    return json.loads((pkg / PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text())


def rewrite(pkg, doc: dict) -> None:
    (pkg / PLUGIN_ROOT / ".codex-plugin" / "plugin.json").write_text(
        json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def failed(report) -> set[str]:
    return {rid for rid, _ in report.failures}


# --------------------------------------------------------- the positive control

def test_the_package_we_intend_to_publish_passes(validate_openai, pkg):
    report = validate_openai.validate(pkg)
    assert report.failures == [], f"real package fails: {report.failures}"


def test_the_positive_control_evaluates_every_rule(validate_openai, pkg):
    """A rule in the table that no check ever reaches is a rule that silently
    approves everything. This is the only test that notices."""
    report = validate_openai.validate(pkg)
    assert report.checked == set(validate_openai.RULES), (
        f"never evaluated: {sorted(set(validate_openai.RULES) - report.checked)}")


# ------------------------------------------------- one negative per rule class

def test_packaging_a_sibling_file_beside_the_plugin_root(validate_openai, pkg):
    """The commonest rejected shape: a zip with the plugin directory AND a stray
    README or .DS_Store next to it. The portal wants exactly one plugin root."""
    (pkg / "README.md").write_text("stray\n", encoding="utf-8")
    assert "no-sibling-files" in failed(validate_openai.validate(pkg))


def test_identity_a_bad_name_and_a_two_part_version(validate_openai, pkg):
    doc = manifest(pkg)
    doc["name"] = "Innovate or Die!"   # spaces and punctuation, not the charset
    doc["version"] = "2.1"             # not semver
    rewrite(pkg, doc)
    assert failed(validate_openai.validate(pkg)) >= {"name-charset-length",
                                                     "version-semver"}


def test_listing_copy_over_the_final_submission_limits(validate_openai, pkg):
    """shortDescription is the trap: 240 chars passes package validation and is
    rejected at final submission, so a package can upload clean and never list."""
    doc = manifest(pkg)
    doc["interface"]["shortDescription"] = "x" * 240
    doc["interface"]["category"] = "Innovation"     # not a published category
    doc["interface"]["defaultPrompt"] = ["Ask @innovate-or-die for help."]
    rewrite(pkg, doc)
    assert failed(validate_openai.validate(pkg)) >= {"short-description-length",
                                                     "category-allowed",
                                                     "default-prompt-shape"}


def test_branding_a_non_square_logo_and_a_path_without_the_prefix(validate_openai, pkg):
    doc = manifest(pkg)
    doc["interface"]["composerIcon"] = "assets/logo.svg"   # missing the ./
    rewrite(pkg, doc)
    svg = pkg / PLUGIN_ROOT / "assets" / "logo.svg"
    svg.write_text(svg.read_text().replace('viewBox="0 0 512 512"',
                                           'viewBox="0 0 512 256"'), encoding="utf-8")
    assert failed(validate_openai.validate(pkg)) >= {"branding-assets", "svg-geometry"}


def test_skills_an_mcp_manifest_and_a_missing_skill_md(validate_openai, pkg):
    """A skills-only submission that carries MCP or app wiring is not a
    skills-only submission, and is validated against a much larger rule set."""
    (pkg / PLUGIN_ROOT / ".mcp.json").write_text("{}\n", encoding="utf-8")
    (pkg / PLUGIN_ROOT / PKG_DIR / "SKILL.md").unlink()
    assert failed(validate_openai.validate(pkg)) >= {"skills-only-exclusions",
                                                     "skill-md-present"}


def test_policy_publisher_identity_left_to_the_portal_to_reconcile(validate_openai, pkg):
    """The portal would accept this -- it offers to use the verified identity for
    both after confirmation. We refuse it, so what gets published is what core/
    says and not what someone clicked."""
    doc = manifest(pkg)
    doc["author"]["name"] = "Ken Pendergast"        # != interface.developerName
    rewrite(pkg, doc)
    assert failed(validate_openai.validate(pkg)) == {"author-matches-developer-name"}


# ------------------------------------------------------- the table, and the CLI

def test_every_rule_carries_a_tag_a_class_a_source_and_a_date(validate_openai):
    """A limit with no source is folklore, and folklore is what this project
    refuses to ship. A rule whose tag is wrong is worse: a POLICY rule mistaken
    for an OPENAI one becomes a fact about the portal that nobody can check."""
    for rid, v in validate_openai.RULES.items():
        assert v["tag"] in ("OPENAI", "POLICY"), rid
        assert v["cls"] and v["rule"], rid
        assert v["verified"] == validate_openai.VERIFIED, rid
        if v["tag"] == "OPENAI":
            assert v["source"] == validate_openai.ERRORS_DOC, rid


def test_a_policy_only_failure_still_exits_one_and_says_whose_rule_it_is(
        validate_openai, pkg, capsys):
    """Both tags exit 1 -- neither package is one to submit -- but the report has
    to say which. Otherwise a house rule gets waived as pedantry, or gets quoted
    back as something OpenAI requires."""
    doc = manifest(pkg)
    doc["author"]["name"] = "Ken Pendergast"
    rewrite(pkg, doc)

    assert validate_openai.main([str(pkg)]) == 1
    out = capsys.readouterr().out
    assert "POLICY FAIL  author-matches-developer-name" in out
    assert "OPENAI FAIL" not in out
    assert "Every failure above is OURS" in out


def test_a_clean_package_exits_zero(validate_openai, pkg, capsys):
    assert validate_openai.main([str(pkg)]) == 0
    assert "OK:" in capsys.readouterr().out
