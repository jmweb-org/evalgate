"""Command-line interface for evalgate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console

from evalgate import __version__
from evalgate.decide import decide
from evalgate.io import (
    as_correct,
    correctness_against_truth,
    discordant_counts,
    read_columns,
)
from evalgate.render import decision_to_json, render_decision
from evalgate.stats import mcnemar_test, two_proportion_test

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Decide whether an eval delta is a real regression or sampling noise.",
)
_out = Console()
_err = Console(stderr=True)

EXIT_OK = 0
EXIT_REGRESSION = 1
EXIT_BAD_INPUT = 2


def _version_callback(value: bool) -> None:
    if value:
        _out.print(f"evalgate {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    _version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """evalgate command-line interface."""


def _emit(decision, extra, as_json):
    if as_json:
        _out.print_json(json.dumps(decision_to_json(decision, extra)))
    else:
        _out.print(render_decision(decision))
    if decision.is_regression:
        raise typer.Exit(EXIT_REGRESSION)


@app.command("proportions")
def proportions(
    baseline_score: float = typer.Option(..., "--baseline-score", help="Baseline accuracy (0-1)."),
    baseline_n: int = typer.Option(..., "--baseline-n", help="Baseline sample size."),
    candidate_score: float = typer.Option(
        ..., "--candidate-score", help="Candidate accuracy (0-1)."
    ),
    candidate_n: int = typer.Option(..., "--candidate-n", help="Candidate sample size."),
    alpha: float = typer.Option(0.05, "--alpha", help="Significance level."),
    as_json: bool = typer.Option(False, "--json", help="Emit the decision as JSON."),
) -> None:
    """Gate on two aggregate accuracies and their sample sizes."""

    if not (0 <= baseline_score <= 1 and 0 <= candidate_score <= 1):
        _err.print("evalgate: scores must be between 0 and 1")
        raise typer.Exit(EXIT_BAD_INPUT)
    try:
        result = two_proportion_test(
            round(baseline_score * baseline_n),
            baseline_n,
            round(candidate_score * candidate_n),
            candidate_n,
        )
    except ValueError as exc:
        _err.print(f"evalgate: {exc}")
        raise typer.Exit(EXIT_BAD_INPUT) from exc
    decision = decide(result, alpha=alpha)
    _emit(decision, {"test": "two_proportion_z"}, as_json)


@app.command("paired")
def paired(
    data: Path = typer.Argument(..., help="CSV of per-example outcomes."),
    baseline: str = typer.Option(..., "--baseline", help="Baseline column."),
    candidate: str = typer.Option(..., "--candidate", help="Candidate column."),
    truth: str = typer.Option(
        None, "--truth", help="If set, baseline/candidate are predictions vs this truth."
    ),
    alpha: float = typer.Option(0.05, "--alpha", help="Significance level."),
    as_json: bool = typer.Option(False, "--json", help="Emit the decision as JSON."),
) -> None:
    """Gate on paired per-example correctness with McNemar's test."""

    names = [baseline, candidate] + ([truth] if truth else [])
    try:
        cols = read_columns(data, names)
    except (OSError, ValueError) as exc:
        _err.print(f"evalgate: {exc}")
        raise typer.Exit(EXIT_BAD_INPUT) from exc

    if truth:
        base_correct = correctness_against_truth(cols[baseline], cols[truth])
        cand_correct = correctness_against_truth(cols[candidate], cols[truth])
    else:
        base_correct = as_correct(cols[baseline])
        cand_correct = as_correct(cols[candidate])

    b, c = discordant_counts(base_correct, cand_correct)
    result = mcnemar_test(b, c)
    decision = decide(result, alpha=alpha)
    _emit(
        decision,
        {"test": "mcnemar", "baseline_only_correct": b, "candidate_only_correct": c},
        as_json,
    )


def entrypoint() -> None:
    try:
        app()
    except KeyboardInterrupt:  # pragma: no cover - interactive only
        print("evalgate: interrupted", file=sys.stderr)
        raise SystemExit(130) from None
