from __future__ import annotations

import json

from typer.testing import CliRunner

from evalgate import __version__
from evalgate import cli as cli_module

runner = CliRunner()


def test_version():
    result = runner.invoke(cli_module.app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_proportions_regression_fails(tmp_path):
    result = runner.invoke(
        cli_module.app,
        [
            "proportions",
            "--baseline-score",
            "0.90",
            "--baseline-n",
            "1000",
            "--candidate-score",
            "0.80",
            "--candidate-n",
            "1000",
            "--json",
        ],
    )
    assert result.exit_code == cli_module.EXIT_REGRESSION
    payload = json.loads(result.stdout)
    assert payload["verdict"] == "regression"


def test_proportions_noise_passes():
    result = runner.invoke(
        cli_module.app,
        [
            "proportions",
            "--baseline-score",
            "0.900",
            "--baseline-n",
            "1000",
            "--candidate-score",
            "0.895",
            "--candidate-n",
            "1000",
            "--json",
        ],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["verdict"] == "noise"


def test_proportions_improvement_passes():
    result = runner.invoke(
        cli_module.app,
        [
            "proportions",
            "--baseline-score",
            "0.90",
            "--baseline-n",
            "1000",
            "--candidate-score",
            "0.93",
            "--candidate-n",
            "1000",
        ],
    )
    assert result.exit_code == 0


def test_proportions_rejects_bad_score():
    result = runner.invoke(
        cli_module.app,
        [
            "proportions",
            "--baseline-score",
            "1.5",
            "--baseline-n",
            "1000",
            "--candidate-score",
            "0.9",
            "--candidate-n",
            "1000",
        ],
    )
    assert result.exit_code == cli_module.EXIT_BAD_INPUT


def test_paired_regression_fails(tmp_path):
    path = tmp_path / "p.csv"
    rows = ["base,cand"]
    rows += ["1,0"] * 20  # baseline right, candidate wrong
    rows += ["0,1"] * 2  # candidate right, baseline wrong
    rows += ["1,1"] * 50
    path.write_text("\n".join(rows) + "\n")
    result = runner.invoke(
        cli_module.app,
        ["paired", str(path), "--baseline", "base", "--candidate", "cand", "--json"],
    )
    assert result.exit_code == cli_module.EXIT_REGRESSION
    payload = json.loads(result.stdout)
    assert payload["baseline_only_correct"] == 20
    assert payload["candidate_only_correct"] == 2


def test_paired_with_truth(tmp_path):
    path = tmp_path / "p.csv"
    path.write_text("y,a,b\n1,1,1\n1,1,0\n0,0,0\n1,1,0\n")
    result = runner.invoke(
        cli_module.app,
        ["paired", str(path), "--baseline", "a", "--candidate", "b", "--truth", "y"],
    )
    # candidate is worse on the examples where it flipped to wrong; small n -> not significant
    assert result.exit_code in (0, cli_module.EXIT_REGRESSION)


def test_paired_missing_column(tmp_path):
    path = tmp_path / "p.csv"
    path.write_text("a\n1\n")
    result = runner.invoke(
        cli_module.app, ["paired", str(path), "--baseline", "a", "--candidate", "nope"]
    )
    assert result.exit_code == cli_module.EXIT_BAD_INPUT
