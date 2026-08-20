"""Guards on matched-pair aggregation -- the bug fixed in v2.0.2.

The defect: a case whose control arm was missing still contributed its
`with_skill` run to the mean, so a 5-case treatment mean was subtracted from a
4-case control mean and the difference was reported as a delta. The fixture
below reproduces that shape exactly.
"""
from __future__ import annotations

import json

import pytest


def timing(*, activated=True, tokens=100_000, ms=60_000, **over):
    t = {"activated": activated, "duration_ms": ms, "total_tokens": tokens,
         "resolved_model": "test-model-1", "requested_model": "test-model-1",
         "model_mismatch": False, "parse_confidence": "ok", "error": None}
    t.update(over)
    return t


def grading(pass_rate):
    return {"summary": {"pass_rate": pass_rate}}


@pytest.fixture
def workspace(tmp_path, aggregate, monkeypatch):
    """A four-case iteration covering every pairing outcome:

    matched-activated, matched-non-activated, unmatched (control missing), and
    invalid (model mismatch).
    """
    slugs = ["case-matched-activated", "case-matched-not-activated",
             "case-unmatched", "case-model-mismatch"]
    (tmp_path / "evals").mkdir()
    (tmp_path / "evals/evals.json").write_text(
        json.dumps({"evals": [{"slug": s} for s in slugs]}))
    base = tmp_path / "evals-workspace/iteration-1/testprov/workhorse"

    def write(slug, arm, t, g):
        d = base / slug / arm
        d.mkdir(parents=True)
        (d / "timing.json").write_text(json.dumps(t))
        (d / "grading.json").write_text(json.dumps(g))

    write("case-matched-activated", "with_skill", timing(tokens=500_000), grading(0.8))
    write("case-matched-activated", "without_skill", timing(tokens=50_000), grading(0.5))

    # A non-activation is a real deployed outcome, NOT a harness failure: the
    # pair stays in, and the deployed/per_activation gap is what reports it.
    write("case-matched-not-activated", "with_skill",
          timing(activated=False, tokens=40_000,
                 error="SKILL DID NOT ACTIVATE"), grading(0.4))
    write("case-matched-not-activated", "without_skill", timing(tokens=40_000), grading(0.4))

    # The v2.0.2 bug: treatment arm present, control arm absent entirely.
    write("case-unmatched", "with_skill", timing(tokens=900_000), grading(1.0))

    write("case-model-mismatch", "with_skill",
          timing(model_mismatch=True, requested_model="test-model-1",
                 resolved_model="test-model-2"), grading(0.9))
    write("case-model-mismatch", "without_skill", timing(), grading(0.1))

    monkeypatch.setattr(aggregate, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv",
                        ["aggregate.py", "--iteration", "1",
                         "--provider", "testprov", "--tier", "workhorse"])
    aggregate.main()
    return json.loads((base / "benchmark.json").read_text())


def test_only_matched_pairs_are_used(workspace):
    assert workspace["pairing"]["pairs_used"] == [
        "case-matched-activated", "case-matched-not-activated"]


def test_both_arms_are_averaged_over_the_same_cases(workspace):
    run = workspace["run_summary"]
    assert run["with_skill"]["n"] == run["without_skill"]["n"] == 2


def test_unmatched_arm_is_dropped_from_the_means(workspace):
    """0.8 and 0.4 -> 0.6. If the unmatched 1.0 leaked in it would be 0.733."""
    assert workspace["run_summary"]["with_skill"]["pass_rate"]["mean"] == 0.6
    assert workspace["run_summary"]["without_skill"]["pass_rate"]["mean"] == 0.45
    assert workspace["run_summary"]["delta"]["pass_rate"] == 0.15


def test_unmatched_arm_is_named_not_silently_dropped(workspace):
    excluded = {e["slug"]: e for e in workspace["pairing"]["excluded_pairs"]}
    assert "case-unmatched" in excluded, "a dropped pair must be reported"
    # A wholly absent arm reports the first thing missing and stops -- there is
    # no run to say anything further about.
    assert excluded["case-unmatched"]["without_skill"] == ["no timing.json"]
    assert excluded["case-unmatched"]["with_skill"] == [], (
        "the surviving arm is valid; the pair is dropped for its partner")


def test_invalid_run_is_dropped_and_its_reason_is_stated(workspace):
    excluded = {e["slug"]: e for e in workspace["pairing"]["excluded_pairs"]}
    assert "case-model-mismatch" in excluded
    reasons = " ".join(excluded["case-model-mismatch"]["with_skill"])
    assert "model_mismatch" in reasons
    assert "test-model-2" in reasons, "the reason must name what actually resolved"


def test_tokens_and_time_are_also_matched(workspace):
    """The token delta is the figure the v2.0.2 correction moved most."""
    run = workspace["run_summary"]
    assert run["with_skill"]["tokens"]["mean"] == 270_000    # (500k + 40k) / 2
    assert run["without_skill"]["tokens"]["mean"] == 45_000  # (50k + 40k) / 2


def test_deployed_delta_includes_the_non_activated_case(workspace):
    dep = workspace["deltas"]["deployed"]
    assert dep["n"] == 2
    assert dep["per_case"]["case-matched-not-activated"] == 0.0
    assert dep["mean"] == 0.15


def test_per_activation_delta_excludes_it_and_says_which(workspace):
    act = workspace["deltas"]["per_activation"]
    assert act["n"] == 1
    assert act["mean"] == 0.3
    assert workspace["deltas"]["excluded_from_per_activation"] == [
        "case-matched-not-activated"]


# ------------------------------------------------------------ validity rules

def test_non_activation_notice_is_not_a_harness_failure(aggregate):
    """Dropping non-activations here would delete the activation-reliability
    finding instead of reporting it."""
    t = timing(activated=False, error="SKILL DID NOT ACTIVATE (no Skill tool call)")
    assert aggregate.invalid_reasons(t, grading(0.4)) == []


def test_other_errors_are_harness_failures(aggregate):
    reasons = aggregate.invalid_reasons(timing(error="connection reset"), grading(0.4))
    assert len(reasons) == 1 and "connection reset" in reasons[0]


@pytest.mark.parametrize("field,value", [("resolved_model", "TIMEOUT"),
                                         ("resolved_model", "UNKNOWN"),
                                         ("parse_confidence", "failed"),
                                         ("parse_confidence", "error-envelope")])
def test_unusable_runs_are_invalid(aggregate, field, value):
    assert aggregate.invalid_reasons(timing(**{field: value}), grading(0.4))


def test_missing_timing_or_null_grade_is_invalid(aggregate):
    assert aggregate.invalid_reasons(None, grading(0.4)) == ["no timing.json"]
    assert aggregate.invalid_reasons(timing(), None) == ["no grading.json"]
    assert aggregate.invalid_reasons(timing(), grading(None)) == [
        "grading pass_rate is null (parse failure)"]
