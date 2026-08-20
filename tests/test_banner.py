"""Guards on the activation banner (ADR-004, core v2.1.0).

The banner exists so "did the protocol run?" is an exact string match rather
than an inference over a whole answer. Two things can silently destroy that: a
check pinned to one version number, and grading the banner in an arm that can
never emit it.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def grade():
    spec = importlib.util.spec_from_file_location(
        "grade_under_test", Path(__file__).resolve().parents[1] / "evals/runners/grade.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["grade_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def run_evals():
    spec = importlib.util.spec_from_file_location(
        "run_evals_under_test",
        Path(__file__).resolve().parents[1] / "evals/runners/run_evals.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_evals_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


BANNER = "⟦innovate-or-die v2.1.0⟧"


# ------------------------------------------------------------- the check

def test_banner_on_the_first_line_passes(grade):
    ok, ev = grade.CHECKS["banner_present"](f"{BANNER}\n\n## Strongest thesis\n...")
    assert ok and "2.1.0" in ev


def test_banner_wrapped_in_a_code_span_still_passes(grade):
    """A model that formats the line has still emitted it."""
    ok, _ = grade.CHECKS["banner_present"](f"`{BANNER}`\n\ntext")
    assert ok
    ok, _ = grade.CHECKS["banner_present"](f"**{BANNER}**\n\ntext")
    assert ok


def test_leading_blank_lines_do_not_defeat_it(grade):
    ok, _ = grade.CHECKS["banner_present"](f"\n\n   \n{BANNER}\ntext")
    assert ok


def test_the_check_is_version_agnostic(grade):
    """Pinning the check to a literal version would read the next bump as an
    activation failure."""
    for v in ("2.1.0", "2.1.1", "3.0.0", "10.20.30"):
        ok, _ = grade.CHECKS["banner_present"](f"⟦innovate-or-die v{v}⟧\ntext")
        assert ok, v


def test_misplaced_banner_fails_but_is_distinguished_from_absent(grade):
    ok, ev = grade.CHECKS["banner_present"]("Here you go.\n\n" + BANNER)
    assert not ok
    assert "NOT on the first line" in ev
    ok, ev = grade.CHECKS["banner_present"]("Here you go.\n\nNo marker anywhere.")
    assert not ok
    assert "no activation banner" in ev


def test_a_lookalike_does_not_pass(grade):
    for near in ("[innovate-or-die v2.1.0]", "⟦innovate-or-die⟧",
                 "⟦innovate-or-die v2.1⟧", "innovate-or-die v2.1.0"):
        ok, _ = grade.CHECKS["banner_present"](near + "\ntext")
        assert not ok, near


def test_runner_and_grader_agree(run_evals, grade):
    """Two implementations read the same line; they must not drift apart."""
    for text in (f"{BANNER}\ntext", "no banner", f"intro\n{BANNER}", f"`{BANNER}`\nx"):
        first_line, _version = run_evals.read_banner(text)
        assert first_line == grade.CHECKS["banner_present"](text)[0], text


def test_runner_reports_the_version_even_when_misplaced(run_evals):
    on_first, version = run_evals.read_banner("intro\n⟦innovate-or-die v2.0.9⟧")
    assert (on_first, version) == (False, "2.0.9")


# --------------------------------------- the arm restriction (the real hazard)

@pytest.fixture
def graded(tmp_path, grade, monkeypatch):
    """Grade a with_skill/without_skill pair offline, mechanical checks only."""
    (tmp_path / "evals").mkdir()
    (tmp_path / "evals/evals.json").write_text(json.dumps({
        "evals": [{"slug": "case-a", "assertions": [
            {"text": "delivers an answer", "check": "delivers_answer"}]}],
        "banner_block": {
            "applies_from_iteration": 3,
            "assertions": [{"text": "opens with the banner",
                            "check": "banner_present", "arm": "with_skill"}]}}))
    base = tmp_path / "evals-workspace/iteration-3/testprov/workhorse"
    for arm, text in (("with_skill", f"{BANNER}\n\nA recommendation with a thesis."),
                      ("without_skill", "A recommendation with a thesis.")):
        d = base / "case-a" / arm / "outputs"
        d.mkdir(parents=True)
        (d / "response.md").write_text(text)
    monkeypatch.setattr(grade, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["grade.py", "--iteration", "3", "--provider",
                                     "testprov", "--tier", "workhorse", "--mechanical-only"])
    grade.main()
    return {arm: json.loads((base / "case-a" / arm / "grading.json").read_text())
            for arm in ("with_skill", "without_skill")}


def test_banner_is_graded_only_in_the_treatment_arm(graded):
    assert [r["passed"] for r in graded["with_skill"]["arm_specific_results"]] == [True]
    assert graded["without_skill"]["arm_specific_results"] == [], (
        "the control arm has no protocol and can never emit the banner")


def test_banner_does_not_enter_pass_rate_in_either_arm(graded):
    """Grading a protocol signature the control cannot produce would manufacture
    a delta out of nothing. Both summaries must be over the same assertions."""
    w, o = graded["with_skill"]["summary"], graded["without_skill"]["summary"]
    assert w["total"] == o["total"] == 1
    assert w["pass_rate"] == o["pass_rate"]
    for res in (graded["with_skill"], graded["without_skill"]):
        assert all(r.get("check") != "banner_present" for r in res["assertion_results"])
        assert "opens with the banner" not in [r["text"] for r in res["assertion_results"]]


# ------------------------------------------------- the shipped artifacts

def test_every_delivering_surface_ships_the_banner(assemble, root):
    version = json.loads((root / "core/skill-meta.json").read_text())["version"]
    banner = f"⟦innovate-or-die v{version}⟧"
    files, _p, _f = assemble.generate()
    must = [f"{b}/innovate-or-die/SKILL.md" for b in
            ("skills", ".agents/skills", ".github/skills")]
    must += [f"adapters/web/{t}-{k}.md" for t in
             ("chatgpt-gpt", "gemini-gem", "m365-copilot") for k in ("instructions", "fallback")]
    must += ["adapters/copilot/agents/innovate-or-die.agent.md"]
    for rel in must:
        assert banner in files[rel], rel


def test_surfaces_that_assemble_nothing_do_not_ship_it(assemble):
    files, _p, _f = assemble.generate()
    never = [f"adapters/web/{t}-knowledge.md" for t in
             ("chatgpt-gpt", "gemini-gem", "m365-copilot")]
    never += [f"adapters/copilot/agents/innovate-or-die-{r}.agent.md"
              for r in ("innovator", "critic", "reviser", "evaluator")]
    for rel in never:
        assert "innovate-or-die v" not in files[rel], rel


def test_the_banner_version_cannot_drift_from_skill_meta(assemble, root):
    """The banner carries {{CORE_VERSION}} in core/, so this is really a test
    that the substitution ran -- a shipped placeholder would be worse than a
    wrong version."""
    version = json.loads((root / "core/skill-meta.json").read_text())["version"]
    files, _p, _f = assemble.generate()
    skill = files["skills/innovate-or-die/SKILL.md"]
    assert f"⟦innovate-or-die v{version}⟧" in skill
    assert "{{" not in skill
