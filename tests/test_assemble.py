"""Guards on the generator's two safety mechanisms.

Both exist because the failure they prevent is SILENT: `str.replace` no-ops on a
drifted anchor, and a file reference that cannot resolve produces a model that
invents the missing content rather than an error anyone sees.
"""
from __future__ import annotations

import json

import pytest


# --------------------------------------------------------------- _sub() refuses

def test_sub_raises_when_anchor_is_missing(assemble):
    with pytest.raises(SystemExit) as e:
        assemble._sub("some text without the anchor",
                      [("an anchor that drifted", "replacement")], "test ctx")
    msg = str(e.value)
    assert "test ctx" in msg, "the failure must name the context that broke"
    assert "an anchor that drifted" in msg


def test_sub_raises_even_when_earlier_pairs_matched(assemble):
    """A partially-applied substitution is the dangerous case: the artifact would
    look edited while still carrying one unresolvable reference."""
    with pytest.raises(SystemExit):
        assemble._sub("alpha only", [("alpha", "A"), ("beta", "B")], "test ctx")


def test_sub_substitutes_when_anchors_present(assemble):
    out = assemble._sub("alpha and beta", [("alpha", "A"), ("beta", "B")], "test ctx")
    assert out == "A and B"


# ------------------------------------------------------- check_references()

def test_single_file_surface_may_not_reference_a_md_file(assemble):
    fatal: list[str] = []
    assemble.check_references(
        {"adapters/web/chatgpt-gpt-instructions.md": "Follow `roles/critic.md` at Stage 2."},
        fatal)
    assert len(fatal) == 1
    assert "roles/critic.md" in fatal[0]
    assert "single file" in fatal[0]


def test_agent_profile_may_not_reference_a_md_file(assemble):
    fatal: list[str] = []
    assemble.check_references(
        {"adapters/copilot/agents/innovate-or-die-innovator.agent.md":
            "Draw lenses from `../references/lenses.md`."}, fatal)
    assert len(fatal) == 1
    assert "../references/lenses.md" in fatal[0]


def test_repo_tree_reference_that_resolves_is_accepted(assemble):
    fatal: list[str] = []
    assemble.check_references(
        {"skills/innovate-or-die/SKILL.md": "Follow `roles/critic.md`.",
         "skills/innovate-or-die/roles/critic.md": "the critic brief"}, fatal)
    assert fatal == []


def test_repo_tree_reference_that_dangles_is_fatal(assemble):
    fatal: list[str] = []
    assemble.check_references(
        {"skills/innovate-or-die/SKILL.md": "Follow `roles/nonexistent.md`."}, fatal)
    assert len(fatal) == 1
    assert "roles/nonexistent.md" in fatal[0]


def test_prose_mention_of_a_dot_md_is_not_a_reference(assemble):
    """The check is deliberately narrow -- it matches the backticked form core/
    actually uses, so ordinary prose does not trip it."""
    fatal: list[str] = []
    assemble.check_references(
        {"adapters/web/chatgpt-gpt-instructions.md": "Paste the .md file into the box."},
        fatal)
    assert fatal == []


# ------------------------------------------------------------- size guardrails

def test_fallback_hard_ceiling_fails_the_build(assemble, monkeypatch):
    """Over the instruction caps is the fallback's accepted condition; over the
    ceiling is a size nobody decided on."""
    monkeypatch.setattr(assemble, "FALLBACK_CEILING", 1000)
    problems: list[str] = []
    fatal: list[str] = []
    assemble.web_variants(assemble.load_core(), problems, fatal)
    assert any("hard ceiling" in f and "fallback" in f for f in fatal), fatal


def test_slack_warning_fires_only_inside_the_slack_margin(assemble, monkeypatch):
    c = assemble.load_core()

    def run(budget):
        problems, fatal = [], []
        monkeypatch.setattr(assemble, "WEB_TARGETS",
                            {"t": ("Test target", budget, "TEST: fixture")})
        assemble.web_variants(c, problems, fatal)
        return problems, fatal

    # Measure the real instructions length, then set budgets around it.
    problems, _ = run(10 ** 9)
    size = len(next(iter(assemble.web_variants(c, [], []).values())))

    problems, fatal = run(size + assemble.INSTRUCTIONS_SLACK + 50)
    assert fatal == []
    assert not any("SLACK" in p for p in problems), "comfortable headroom must stay quiet"

    problems, fatal = run(size + 10)
    assert fatal == [], "10 chars under the cap still fits -- a warning, not a failure"
    assert any("SLACK" in p for p in problems), problems

    problems, fatal = run(size - 1)
    assert any("exceeds" in f for f in fatal), "over the cap is fatal, not a warning"


# --------------------------------------------- per-target preamble host naming

def test_preamble_wrap_width_matches_the_authored_paragraph(assemble):
    """Re-wrapping must reproduce the source when the words are unchanged.

    PREAMBLE_WRAP is a magic number, and the wrong one would reflow lines the
    host name never touched -- making every host-named target differ from the
    generic preamble by a whole paragraph instead of by one phrase, and hiding
    a real wording change inside the noise.
    """
    import textwrap
    anchor = assemble.PREAMBLE_HOST_ANCHOR
    assert textwrap.fill(" ".join(anchor.split()), width=assemble.PREAMBLE_WRAP) == anchor


def test_host_named_preamble_differs_only_in_the_host_name(assemble):
    _anchor, filled = assemble._preamble_host_pair("Perplexity Projects")
    assert "Perplexity Projects provides no context isolation" in " ".join(filled.split())
    assert "This host" not in filled


def test_every_host_named_target_is_a_real_web_target(assemble):
    """A typo'd key here would silently emit the generic preamble under a target
    that documents itself as naming its host."""
    assert set(assemble.WEB_PREAMBLE_HOST) <= set(assemble.WEB_TARGETS)


# ------------------------------------------------- the real build, end to end

def test_real_build_has_no_fatal_findings(assemble):
    _files, _problems, fatal = assemble.generate()
    assert fatal == []


def test_every_generated_web_instructions_file_fits_its_cap(assemble):
    files, _problems, _fatal = assemble.generate()
    for target, (_label, budget, _status) in assemble.WEB_TARGETS.items():
        assert len(files[f"adapters/web/{target}-instructions.md"]) <= budget


def test_no_generated_file_ships_an_unsubstituted_placeholder(assemble):
    files, _problems, _fatal = assemble.generate()
    for rel, content in files.items():
        assert "{{" not in content, rel


# ------------------------------------------------ evals/results index guard

def test_results_index_guard_names_an_undescribed_file(assemble, monkeypatch, tmp_path):
    """A results file with no row in the README table cannot be described, so the
    index would silently thin out instead of failing."""
    (tmp_path / "evals" / "results").mkdir(parents=True)
    (tmp_path / "evals/results/2026-01-01-orphan.md").write_text("# Orphan result\n")
    (tmp_path / "README.md").write_text("no results table here\n")
    monkeypatch.setattr(assemble, "ROOT", tmp_path)
    fatal: list[str] = []
    out = assemble.evals_results_index(fatal)
    assert out == {}
    assert len(fatal) == 1
    assert "2026-01-01-orphan.md" in fatal[0]
    assert "README results table" in fatal[0]


def test_results_index_guard_names_a_link_to_a_missing_file(assemble, monkeypatch, tmp_path):
    (tmp_path / "evals" / "results").mkdir(parents=True)
    (tmp_path / "README.md").write_text(
        "| [Gone](evals/results/2026-01-01-gone.md) | a result that was deleted |\n")
    monkeypatch.setattr(assemble, "ROOT", tmp_path)
    fatal: list[str] = []
    assemble.evals_results_index(fatal)
    assert any("2026-01-01-gone.md" in f and "no such file" in f for f in fatal), fatal


def test_results_index_lists_every_committed_result(assemble, root):
    files, _problems, fatal = assemble.generate()
    index = files[assemble.EVALS_INDEX]
    on_disk = {p.name for p in (root / "evals/results").glob("*.md")} - {"README.md"}
    for name in on_disk:
        assert f"]({name})" in index, f"{name} is missing from the generated index"
    assert fatal == []


# ------------------------------------------------------ LICENSE <-> skill-meta

def test_license_string_matches_the_license_file(root):
    """The license lives in two places. One-line insurance against them drifting."""
    meta = json.loads((root / "core/skill-meta.json").read_text())
    first_line = (root / "LICENSE").read_text().strip().splitlines()[0].strip()
    assert first_line == f"{meta['license']} License", (
        f"LICENSE opens with {first_line!r} but skill-meta.json says {meta['license']!r}")


def test_license_copyright_matches_the_declared_author(root):
    meta = json.loads((root / "core/skill-meta.json").read_text())
    license_text = (root / "LICENSE").read_text()
    author = meta.get("author", {})
    assert author.get("name") and author["name"] in license_text
    assert author.get("url") and author["url"] in license_text


def test_every_generated_manifest_carries_the_same_license(assemble):
    c = assemble.load_core()
    declared = c["meta"]["license"]
    files, _problems, _fatal = assemble.generate()
    for rel in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
        assert json.loads(files[rel])["license"] == declared, rel
    marketplace = json.loads(files[".claude-plugin/marketplace.json"])
    assert marketplace["plugins"][0]["license"] == declared
    for base in ("skills", ".agents/skills", ".github/skills"):
        skill_md = files[f"{base}/innovate-or-die/SKILL.md"]
        assert f"\nlicense: {declared}\n" in skill_md, base
