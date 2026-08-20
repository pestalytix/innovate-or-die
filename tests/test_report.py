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


def test_all_runs_unknown_is_a_refusal_not_a_single_version(build, capsys):
    """`{"UNKNOWN"}` is one ELEMENT and zero versions. Emitting "every run used
    vUNKNOWN" would be a provenance claim made out of missing provenance."""
    rc, text, written = build(versions=[None, None])
    assert rc == 1, "a tier with no resolvable version must not emit"
    assert written == [] and text is None
    err = capsys.readouterr().err
    assert "REFUSING TO EMIT" in err
    assert "UNKNOWN" in err
    assert "could not resolve a single real skill version" in err


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


# ------------------------------------------ the uncontrolled-context annotation

class Args:
    """Minimal stand-in for the parsed argv namespace `banners()` reads."""
    def __init__(self, iteration, provider, tier="workhorse"):
        self.iteration, self.provider, self.tier = iteration, provider, tier


ANCHOR = "**Uncontrolled context (found 2026-08-20).**"


@pytest.mark.parametrize("iteration,provider,expected", [
    (1, "claude", True),      # the affected lane
    (1, "codex", False),      # codex exposes no host metadata to leak
    (2, "claude", False),     # the finding is scoped to iteration 1
    (3, "claude", False),
])
def test_banner_is_gated_to_the_affected_lane(report, iteration, provider, expected):
    L = []
    report.banners(Args(iteration, provider), L, "2.1.0")
    assert any(ANCHOR in line for line in L) is expected


@pytest.mark.parametrize("iteration,provider,expected", [
    (1, "claude", True), (1, "codex", False), (2, "claude", False),
])
def test_the_annotation_is_in_the_completeness_manifest(report, iteration,
                                                        provider, expected):
    """A banner not in the manifest can silently stop being emitted."""
    assert (ANCHOR in report.required_sections(Args(iteration, provider))) is expected


def test_the_banner_names_both_affected_arms(report):
    L = []
    report.banners(Args(1, "claude"), L, "2.0.1")
    banner = next(line for line in L if ANCHOR in line)
    assert "with_skill" in banner and "without_skill" in banner
    assert "BigQuery" in banner, "the control's leak must be named, not just the treatment's"
    assert "eval-route-density" in banner
    assert "transcripts/README.md#" in banner, "must link the evidence"


# ------------------------- method prose derives from fields, not iteration number

JDOC = {"verdicts": [{"slug": "s", "winner_arm": "with_skill", "reason": "r"}],
        "judge_model_requested": "m", "judge_model_resolved": ["m"],
        "limitation": "l"}


def jdoc(**over):
    d = dict(JDOC); d.update(over); return d


def test_recorded_presentation_method_is_described(report):
    L = []
    report.judge_section(jdoc(presentation_method="per-ballot-seeded-sha256"), L)
    txt = "\n".join(L)
    assert "drawn independently per ballot" in txt
    assert "predates" not in txt


def test_absent_presentation_method_says_so_and_names_the_commit(report):
    """The field is the provenance. Without it the file must say the run predates
    it, not silently inherit whatever the harness does today."""
    L = []
    report.judge_section(jdoc(), L)
    txt = "\n".join(L)
    assert "index alternation" in txt
    assert "predates the `presentation_method` field" in txt
    assert "d4c7269" in txt
    assert "drawn independently per ballot" not in txt


def test_an_unrecognised_method_is_reported_verbatim_not_guessed(report):
    """Mapping an unknown value to the nearest known one would reintroduce the
    original bug in a subtler form."""
    L = []
    report.judge_section(jdoc(presentation_method="latin-square-v2"), L)
    txt = "\n".join(L)
    assert "`latin-square-v2`" in txt
    assert "no description for" in txt
    assert "index alternation" not in txt


def test_harness_commit_is_reported_when_recorded(report):
    L = []
    report.judge_section(jdoc(presentation_method="per-ballot-seeded-sha256",
                              harness_commit="d4c7269d4b4b9356a85863cc"), L)
    assert "d4c7269d4b4b" in "\n".join(L)


def test_iteration_number_does_not_change_the_method_prose(report):
    """The whole point: iteration is a label, not provenance. Same jdoc must
    produce the same sentence regardless of which iteration is being reported."""
    outs = []
    for _ in range(2):
        L = []
        report.judge_section(jdoc(presentation_method="per-ballot-seeded-sha256"), L)
        outs.append("\n".join(L))
    assert outs[0] == outs[1]
    import inspect
    assert "iteration" not in inspect.signature(report.judge_section).parameters


# ---- arm order, same rule, read from timing.json ----

def _tier(tmp_path, *methods):
    base = tmp_path / "ws"
    for i, m in enumerate(methods):
        d = base / f"case-{i}/with_skill"
        d.mkdir(parents=True)
        rec = {"total_tokens": 1, "duration_ms": 1}
        if m is not None:
            rec["arm_order_method"] = m
        (d / "timing.json").write_text(json.dumps(rec))
    return base


def test_recorded_arm_order_method_is_described(report, tmp_path):
    line = report.arm_order_line(_tier(tmp_path, "per-case-seeded-sha256",
                                       "per-case-seeded-sha256"))
    assert "drawn per case from a seeded RNG" in line
    assert "arm_order_index" in line


def test_absent_arm_order_method_says_with_skill_ran_first(report, tmp_path):
    line = report.arm_order_line(_tier(tmp_path, None, None))
    assert "`with_skill` ran first in every pair" in line
    assert "predates the `arm_order_method` field" in line
    assert "d4c7269" in line


def test_a_tier_with_no_runs_at_all_falls_back_to_the_absent_wording(report, tmp_path):
    (tmp_path / "empty").mkdir()
    assert "predates" in report.arm_order_line(tmp_path / "empty")


def test_mixed_arm_order_methods_are_reported_as_mixed(report, tmp_path):
    """Two methods in one tier is not describable by either. Say so."""
    line = report.arm_order_line(_tier(tmp_path, "per-case-seeded-sha256",
                                       "round-robin-v9"))
    assert "mixed methods" in line
    assert "per-case-seeded-sha256" in line and "round-robin-v9" in line


def test_run_order_banner_is_in_the_completeness_manifest(report):
    assert "**Run order.**" in report.required_sections(Args(1, "claude"))
    assert "**Run order.**" in report.required_sections(Args(2, "codex"))


# ------------------------------------ the flagship probe names its control run

def _flagship(tmp_path, control: dict | None):
    """Lay down the minimum opus_section() reads: the probe arm, and optionally
    the control arm that exists on disk but is excluded from the probe."""
    base = tmp_path / "evals-workspace/iteration-1/claude/flagship/eval-route-density"
    (base / "with_skill").mkdir(parents=True)
    (base / "with_skill/timing.json").write_text(json.dumps(
        {"resolved_model": "claude-opus-5", "skill_version": "2.0.1",
         "effort": "default", "total_tokens": 1_137_884, "duration_ms": 1_472_000,
         "num_turns": 15, "cost_usd": 4.84, "activation_method": "observed:Skill-tool-call",
         "tools": {"Agent": 3, "WebSearch": 4}}))
    if control is not None:
        (base / "without_skill").mkdir(parents=True)
        (base / "without_skill/timing.json").write_text(json.dumps(control))
    return base


def test_probe_states_that_a_control_exists_on_disk(report, tmp_path, monkeypatch):
    """'with_skill only' alone read as 'no control was run' — a different claim,
    and one the uncontrolled-context banner directly contradicts."""
    _flagship(tmp_path, {"resolved_model": "claude-opus-5", "skill_version": "2.0.0",
                         "total_tokens": 28_357, "duration_ms": 47_581,
                         "activated": False})
    monkeypatch.setattr(report, "ROOT", tmp_path)
    L = []
    report.opus_section(L)
    para = next(x for x in L if "envelope probe (MODEL_POLICY" in x)
    assert "does exist on disk" in para
    assert "28,357 tok" in para, "the control's figures must be derived, not asserted"
    assert "v2.0.0" in para and "claude-opus-5" in para
    assert "non-activated, as a control should be" in para
    assert "excluded from the probe by design" in para
    assert "uncontrolled-context banner" in para, "must tie to the banner that names it"


def test_probe_says_nothing_about_a_control_that_is_not_there(report, tmp_path,
                                                             monkeypatch):
    """The clause is derived from disk; with no control run there is nothing to
    claim and the section must not invent one."""
    _flagship(tmp_path, None)
    monkeypatch.setattr(report, "ROOT", tmp_path)
    L = []
    report.opus_section(L)
    para = next(x for x in L if "envelope probe (MODEL_POLICY" in x)
    assert "does exist on disk" not in para
    assert para.rstrip().endswith("the medium-effort mitigation arm was not run.")


def test_an_unexpectedly_activated_control_is_not_described_as_non_activated(
        report, tmp_path, monkeypatch):
    """A control that fired is a finding, not something to paper over with the
    word the happy path uses."""
    _flagship(tmp_path, {"resolved_model": "claude-opus-5", "skill_version": "2.0.0",
                         "total_tokens": 28_357, "activated": True})
    monkeypatch.setattr(report, "ROOT", tmp_path)
    L = []
    report.opus_section(L)
    para = next(x for x in L if "envelope probe (MODEL_POLICY" in x)
    assert "non-activated, as a control should be" not in para
    assert "activated=True" in para


def test_the_banner_does_not_claim_codex_is_clean(report):
    """Codex exposes no event stream, so the scan could only read delivered
    answers. "No Codex run shows this" invites the inference that Codex is
    clean; what is true is that absence there cannot be observed."""
    L = []
    report.banners(Args(1, "claude"), L, "2.0.1")
    banner = next(line for line in L if ANCHOR in line)
    assert "unobservable rather than established" in banner
    assert "No other run in any tier, and no Codex run, shows this" not in banner, (
        "the wording that read as an established Codex absence")
