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
