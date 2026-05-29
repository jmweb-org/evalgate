"""Read per-example results from a CSV and reduce them to discordant counts.

Only the standard-library CSV reader is used: evalgate is a statistics tool,
not a dataframe tool, and the paired input is a simple table of per-example
outcomes.
"""

from __future__ import annotations

import csv
from collections.abc import Sequence
from pathlib import Path

TRUTHY = {"1", "true", "yes", "correct", "t", "y"}


def read_columns(path: str | Path, names: Sequence[str]) -> dict[str, list[str]]:
    path = Path(path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        missing = [n for n in names if n not in header]
        if missing:
            raise ValueError(f"column(s) not found: {', '.join(missing)}")
        columns: dict[str, list[str]] = {name: [] for name in names}
        for row in reader:
            for name in names:
                columns[name].append(row[name])
    return columns


def as_correct(values: Sequence[str]) -> list[bool]:
    return [str(v).strip().lower() in TRUTHY for v in values]


def correctness_against_truth(predictions: Sequence[str], truth: Sequence[str]) -> list[bool]:
    if len(predictions) != len(truth):
        raise ValueError("prediction and truth columns differ in length")
    return [str(p) == str(t) for p, t in zip(predictions, truth, strict=False)]


def discordant_counts(
    baseline_correct: Sequence[bool], candidate_correct: Sequence[bool]
) -> tuple[int, int]:
    """Return (b, c): baseline-only-correct and candidate-only-correct."""

    if len(baseline_correct) != len(candidate_correct):
        raise ValueError("baseline and candidate columns differ in length")
    b = sum(1 for x, y in zip(baseline_correct, candidate_correct, strict=False) if x and not y)
    c = sum(1 for x, y in zip(baseline_correct, candidate_correct, strict=False) if y and not x)
    return b, c
