"""evalgate: decide whether an eval delta is a real regression or sampling noise."""

from evalgate.decide import Decision, Verdict, decide
from evalgate.stats import (
    StatResult,
    mcnemar_test,
    two_proportion_test,
    wilson_interval,
)

__version__ = "0.2.0"

__all__ = [
    "Decision",
    "StatResult",
    "Verdict",
    "__version__",
    "decide",
    "mcnemar_test",
    "two_proportion_test",
    "wilson_interval",
]
