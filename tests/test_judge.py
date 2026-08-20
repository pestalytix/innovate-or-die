"""Guards on the blind judge's majority rule -- the second bug fixed in v2.0.2.

The defect: `Counter.most_common(1)` returns the top vote whether or not it is a
majority. A/B/tie is a three-way split, so a 1-1-1 result awarded a win on a
single ballot.
"""
from __future__ import annotations

import pytest

MAPPING = {"A": "with_skill", "B": "without_skill"}


def ballots(*winners):
    return [{"winner": w, "A": {}, "B": {}, "reason": f"ballot {i}"}
            for i, w in enumerate(winners)]


def test_three_way_split_yields_no_winner(judge):
    """The regression case: one A, one B, one tie must not elect A."""
    winner, has_majority, tally, _n = judge.decide(ballots("A", "B", "tie"), MAPPING)
    assert winner == "tie"
    assert has_majority is False
    assert dict(tally) == {"A": 1, "B": 1, "tie": 1}


def test_three_way_split_is_a_tie_whichever_ballot_came_first(judge):
    for order in (("A", "B", "tie"), ("B", "tie", "A"), ("tie", "A", "B")):
        winner, has_majority, _t, _n = judge.decide(ballots(*order), MAPPING)
        assert (winner, has_majority) == ("tie", False), order


def test_two_of_three_is_a_majority(judge):
    winner, has_majority, _t, n_top = judge.decide(ballots("A", "A", "B"), MAPPING)
    assert winner == "with_skill"
    assert has_majority is True
    assert n_top == 2


def test_unanimous_verdict_maps_to_the_arm(judge):
    winner, has_majority, _t, n_top = judge.decide(ballots("B", "B", "B"), MAPPING)
    assert (winner, has_majority, n_top) == ("without_skill", True, 3)


def test_even_split_is_a_tie(judge):
    """Two-two is exactly half, and half is not more than half."""
    winner, has_majority, _t, _n = judge.decide(ballots("A", "A", "B", "B"), MAPPING)
    assert (winner, has_majority) == ("tie", False)


def test_majority_of_ties_stays_a_tie(judge):
    winner, has_majority, _t, _n = judge.decide(ballots("tie", "tie", "A"), MAPPING)
    assert winner == "tie"
    assert has_majority is True, "the majority is real -- it just elected no arm"


def test_single_ballot_carries_itself(judge):
    """With --votes 1 there is nothing to be a majority against; documented so a
    future change to the default is a visible decision, not a silent one."""
    winner, has_majority, _t, _n = judge.decide(ballots("A"), MAPPING)
    assert (winner, has_majority) == ("with_skill", True)


def test_arm_mapping_follows_presentation_order(judge):
    """Position is flipped on alternating cases, so A is not always the treatment
    arm. Unblinding must follow the mapping, not the label."""
    flipped = {"A": "without_skill", "B": "with_skill"}
    winner, _m, _t, _n = judge.decide(ballots("A", "A", "B"), flipped)
    assert winner == "without_skill"


def test_unparseable_winner_field_does_not_elect_an_arm(judge):
    winner, _m, _t, _n = judge.decide([{"winner": None}, {"winner": None},
                                       {"winner": "A"}], MAPPING)
    assert winner == "tie"


# ------------------------------------------- per-ballot presentation order

def test_ballot_order_is_stable_across_processes(judge):
    """The seed must not come from the builtin `hash()`: string hashing is salted
    per interpreter, so a `hash()`-derived order would differ on every run and the
    recorded `presented_first` would not reproduce."""
    import subprocess
    import sys
    from pathlib import Path

    runner = Path(judge.__file__)
    prog = (f"import importlib.util as u;"
            f"s=u.spec_from_file_location('j',r'{runner}');"
            f"m=u.module_from_spec(s);s.loader.exec_module(m);"
            f"print([m.ballot_order('claude','workhorse',3,'eval-x',v)[0] for v in range(8)])")
    runs = {subprocess.run([sys.executable, "-c", prog], capture_output=True,
                           text=True, check=True,
                           env={"PYTHONHASHSEED": seed}).stdout.strip()
            for seed in ("0", "1", "random")}
    assert len(runs) == 1, f"order changed with PYTHONHASHSEED: {runs}"


def test_ballot_order_varies_within_a_case(judge):
    """Index alternation gave one fixed order per case. The draw is per BALLOT, so
    the vote_index has to move it."""
    orders = {judge.ballot_order("claude", "workhorse", 3, "eval-route-density", v)[0]
              for v in range(8)}
    assert orders == {"with_skill", "without_skill"}


def test_ballot_order_is_a_permutation_of_both_arms(judge):
    for v in range(20):
        first, second = judge.ballot_order("codex", "workhorse", 3, f"case-{v}", v)
        assert {first, second} == set(judge.ARMS)
        assert first != second


def test_arm_identity_lets_decide_tally_already_unblinded_ballots(judge):
    """Per-ballot order means each ballot carries its own A/B mapping, so main()
    unblinds first and tallies over arms. `decide` must handle that form."""
    ballots = [{"winner": "with_skill"}, {"winner": "with_skill"},
               {"winner": "without_skill"}]
    winner, has_majority, tally, n_top = judge.decide(ballots, judge.ARM_IDENTITY)
    assert (winner, has_majority, n_top) == ("with_skill", True, 2)
    assert dict(tally) == {"with_skill": 2, "without_skill": 1}
