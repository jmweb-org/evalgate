"""Turn a significance test into a gate decision.

The gate fails only when the candidate is *significantly worse* than the
baseline. A candidate that is worse but within noise passes, and so does an
equal or better candidate. This is what keeps a CI eval from flapping on
sampling variation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from evalgate.stats import StatResult


class Verdict(str, Enum):
    REGRESSION = "regression"  # significantly worse -> fail
    NOISE = "noise"  # worse but not significant -> pass
    UNCHANGED = "unchanged"  # no measurable difference -> pass
    IMPROVEMENT = "improvement"  # better -> pass


@dataclass(frozen=True, slots=True)
class Decision:
    verdict: Verdict
    p_value: float
    difference: float
    alpha: float

    @property
    def is_regression(self) -> bool:
        return self.verdict is Verdict.REGRESSION


def decide(result: StatResult, *, alpha: float = 0.05) -> Decision:
    """Classify a test result as regression, noise, unchanged or improvement.

    ``result.difference`` is signed so that a negative value means the candidate
    is worse than the baseline.
    """

    diff = result.difference
    if diff == 0:
        verdict = Verdict.UNCHANGED
    elif diff > 0:
        verdict = Verdict.IMPROVEMENT
    elif result.p_value < alpha:
        verdict = Verdict.REGRESSION
    else:
        verdict = Verdict.NOISE
    return Decision(
        verdict=verdict,
        p_value=result.p_value,
        difference=diff,
        alpha=alpha,
    )
