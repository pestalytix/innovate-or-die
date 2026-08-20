"""Guards on the two claims the results header makes about its own runs.

Both were hardcoded prose sitting above data that could contradict it:

1. "Every run in this iteration used **v2.0.1**" -- a literal, so a tier run
   under any other version emitted a file asserting the wrong version, and a
   tier that mixed versions asserted it had not.
2. "Paired design: every case ran twice" -- unconditional, printed directly
   above tables computed over matched pairs only and above the exclusion list
   that named the cases which had *not* run twice.

Both are now derived from the workspace, and the version claim is a refusal
rather than a correction: a mixed-version tier produces no file at all.
"""
from __future__ import annotations

import json

import pytest

CASES = ["case-alpha", "case-beta"]


def timing(version="2.1.0", **over):
    t = {"total_tokens": 100_000, "duration_ms": 60_000, "skill_version": version,
         "requested_model": "test-model-1", "resolved_model": "test-model-1",
         "repo_commit": "0" * 40, "repo_dirty": False, "activated": True,
         "skill_version_method": "read:SKILL.md-frontmatter",
         "cli_name": "claude", "cli_version": "0.0.0"}
    t.update(over)
    return t


def benchmark(pairs_used=CASES, excluded_pairs=(), with_pairing=True):
    doc = {
        "run_summary": {
            "with_skill": {"pass_rate": {"mean": 0.8}, "time_seconds": {"mean": 60.0},
                           "tokens": {"mean": 100_000}, "n": len(pairs_used)},
            "without_skill": {"pass_rate": {"mean": 0.5}, "time_seconds": {"mean": 30.0},
                              "tokens": {"mean": 50_000}, "n": len(pairs_used)},
            "delta": {"pass_rate": 0.3, "time_seconds": 30.0, "tokens": 50_000}},
        "deltas": {
            "deployed": {"mean": 0.3, "n": len(pairs_used),
                         "per_case": {s: 0.3 for s in pairs_used},
                         "meaning": "every case"},
            "per_activation": {"mean": 0.3, "n": len(pairs_used),
                               "per_case": {s: 0.3 for s in pairs_used},
                               "meaning": "cases where the skill fired"},
            "excluded_from_per_activation": [], "gap_is": "reliability"},
        "resolved_models": ["test-model-1"], "provider": "testprov", "iteration": 2}
    if with_pairing:
        doc["pairing"] = {"rule": "matched valid pairs only", "note": "a note",
                          "pairs_used": list(pairs_used),
                          "excluded_pairs": list(excluded_pairs)}
    return doc


@pytest.fixture
def build(tmp_path, report, monkeypatch):
    """Return a runner that lays down an iteration-2 workspace and reports.

    Iteration 2 deliberately: the iteration-1 banner is a historical record of a
    genuine two-version span and is not derived.
    """
    def run(*, versions, bench=None, iteration=2):
        it = tmp_path / f"evals-workspace/iteration-{iteration}"
        base = it / "testprov/workhorse"
        (tmp_path / "evals/results").mkdir(parents=True, exist_ok=True)
        (tmp_path / "evals/evals.json").write_text(json.dumps(
            {"evals": [{"slug": s, "domain": "d", "phrasing": "casual", "prompt": "p"}
                       for s in CASES]}))
        for slug, ver in zip(CASES, versions):
            for arm in ("with_skill", "without_skill"):
                d = base / slug / arm
                d.mkdir(parents=True, exist_ok=True)
                (d / "timing.json").write_text(json.dumps(timing(ver)))
        base.mkdir(parents=True, exist_ok=True)
        (base / "benchmark.json").write_text(
            json.dumps(bench if bench is not None else benchmark()))
        # cost_line() needs one of the two cost sources to emit "## Cost",
        # which required_sections() demands for iteration != 1.
        (it / "cost-grading-testprov-workhorse.json").write_text(json.dumps(
            {"calls": 30, "cost_usd": 2.5, "cached_share_of_tokens": 0.959}))
        monkeypatch.setattr(report, "ROOT", tmp_path)
        monkeypatch.setattr("sys.argv",
                            ["report.py", "--provider", "testprov", "--tier",
                             "workhorse", "--iteration", str(iteration),
                             "--date", "2026-08-20"])
        rc = report.main()
        written = sorted((tmp_path / "evals/results").glob("*.md"))
        return rc, (written[0].read_text(encoding="utf-8") if written else None), written
    return run


# ------------------------------------------------- the version banner is derived

def test_single_version_is_read_from_the_runs_not_hardcoded(build):
    rc, text, _ = build(versions=["2.1.0", "2.1.0"])
    assert rc == 0
    assert "Every run in this iteration used **v2.1.0**" in text
    assert "v2.0.1" not in text, "the literal the banner used to carry"


def test_mixed_versions_refuse_to_emit_a_file(build, capsys):
    rc, text, written = build(versions=["2.0.1", "2.1.0"])
    assert rc == 1
    assert written == [], "no file may be written when the claim cannot be made"
    assert text is None
    err = capsys.readouterr().err
    assert "2.0.1" in err and "2.1.0" in err, "the refusal must print the set it found"


def test_no_runs_at_all_is_also_a_refusal(build):
    """Zero versions is not 'one version'. An empty set must not silently emit."""
    rc, _text, written = build(versions=[])
    assert rc == 1 and written == []


def test_a_run_missing_its_version_shows_up_as_unknown(build, capsys):
    rc, _text, written = build(versions=[None, "2.1.0"])
    assert rc == 1 and written == []
    assert "UNKNOWN" in capsys.readouterr().err


def test_the_derived_banner_is_in_the_completeness_manifest(report):
    class A:
        iteration, provider, tier = 2, "testprov", "workhorse"
    assert "**Single protocol version.**" in report.required_sections(A())

    class B:
        iteration, provider, tier = 1, "claude", "flagship"
    assert "**Version span.**" in report.required_sections(B())


# -------------------------------------------------- the paired-design line

def test_complete_pairing_keeps_the_original_sentence(report):
    line = report.paired_design_line(benchmark(), len(CASES))
    assert line.startswith("Paired design: every case ran twice")


def test_incomplete_pairing_states_how_many_survived(report):
    bench = benchmark(pairs_used=["case-alpha"],
                      excluded_pairs=[{"slug": "case-beta", "with_skill": [],
                                       "without_skill": ["no timing.json"]}])
    line = report.paired_design_line(bench, len(CASES))
    assert line == ("Paired design: 1 of 2 cases have a matched valid pair "
                    "(see exclusions under Two deltas).")


def test_a_case_dropped_with_no_arms_at_all_still_counts_against_n(report):
    """aggregate.py only records an excluded_pair when a partial pair exists, so
    N comes from evals.json, not from used + excluded."""
    line = report.paired_design_line(benchmark(pairs_used=["case-alpha"]), len(CASES))
    assert "1 of 2 cases" in line


def test_absent_pairing_metadata_claims_nothing(report):
    line = report.paired_design_line(benchmark(with_pairing=False), len(CASES))
    assert line == "Paired design; pairing metadata absent in this benchmark.json."


def test_the_derived_line_reaches_the_written_file(build):
    bench = benchmark(pairs_used=["case-alpha"],
                      excluded_pairs=[{"slug": "case-beta", "with_skill": [],
                                       "without_skill": ["no timing.json"]}])
    rc, text, _ = build(versions=["2.1.0", "2.1.0"], bench=bench)
    assert rc == 0
    assert "Paired design: 1 of 2 cases have a matched valid pair" in text
    assert "every case ran twice" not in text
