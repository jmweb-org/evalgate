from __future__ import annotations

import pytest

from evalgate.decide import Verdict, decide
from evalgate.io import (
    as_correct,
    correctness_against_truth,
    discordant_counts,
    read_columns,
)
from evalgate.stats import StatResult, mcnemar_test, two_proportion_test


def test_decide_improvement():
    result = StatResult(statistic=2.0, p_value=0.04, difference=0.02)
    assert decide(result).verdict is Verdict.IMPROVEMENT


def test_decide_unchanged():
    result = StatResult(statistic=0.0, p_value=1.0, difference=0.0)
    assert decide(result).verdict is Verdict.UNCHANGED


def test_decide_regression_when_worse_and_significant():
    result = two_proportion_test(900, 1000, 800, 1000)
    decision = decide(result, alpha=0.05)
    assert decision.verdict is Verdict.REGRESSION
    assert decision.is_regression


def test_decide_noise_when_worse_but_not_significant():
    result = two_proportion_test(900, 1000, 895, 1000)
    decision = decide(result, alpha=0.05)
    assert decision.verdict is Verdict.NOISE
    assert not decision.is_regression


def test_decide_alpha_changes_outcome():
    result = two_proportion_test(900, 1000, 878, 1000)
    # borderline: tighter alpha calls it noise, looser calls it regression
    strict = decide(result, alpha=0.001)
    loose = decide(result, alpha=0.20)
    assert strict.verdict is Verdict.NOISE
    assert loose.verdict is Verdict.REGRESSION


def test_as_correct_parses_truthy_values():
    assert as_correct(["1", "0", "true", "no", "correct"]) == [True, False, True, False, True]


def test_correctness_against_truth():
    assert correctness_against_truth(["a", "b", "c"], ["a", "x", "c"]) == [True, False, True]


def test_correctness_length_mismatch():
    with pytest.raises(ValueError):
        correctness_against_truth(["a"], ["a", "b"])


def test_discordant_counts():
    base = [True, True, False, True]
    cand = [True, False, True, False]
    b, c = discordant_counts(base, cand)
    assert b == 2  # baseline right, candidate wrong (idx 1, 3)
    assert c == 1  # candidate right, baseline wrong (idx 2)


def test_read_columns(tmp_path):
    path = tmp_path / "r.csv"
    path.write_text("base,cand\n1,0\n1,1\n0,1\n")
    cols = read_columns(path, ["base", "cand"])
    assert cols["base"] == ["1", "1", "0"]
    assert cols["cand"] == ["0", "1", "1"]


def test_read_columns_missing(tmp_path):
    path = tmp_path / "r.csv"
    path.write_text("a\n1\n")
    with pytest.raises(ValueError):
        read_columns(path, ["a", "missing"])


def test_mcnemar_decision_end_to_end():
    result = mcnemar_test(20, 2)
    assert decide(result).verdict is Verdict.REGRESSION
