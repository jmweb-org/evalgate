"""Render a gate decision for the terminal and as JSON."""

from __future__ import annotations

from rich.console import Group
from rich.table import Table
from rich.text import Text

from evalgate.decide import Decision, Verdict

_STYLE = {
    Verdict.REGRESSION: "bold red",
    Verdict.NOISE: "yellow",
    Verdict.UNCHANGED: "dim",
    Verdict.IMPROVEMENT: "green",
}
_MESSAGE = {
    Verdict.REGRESSION: "significant regression",
    Verdict.NOISE: "worse, but within noise",
    Verdict.UNCHANGED: "no measurable change",
    Verdict.IMPROVEMENT: "improvement",
}


def decision_to_json(decision: Decision, extra: dict | None = None) -> dict:
    payload = {
        "verdict": decision.verdict.value,
        "p_value": round(decision.p_value, 6),
        "difference": round(decision.difference, 6),
        "alpha": decision.alpha,
        "is_regression": decision.is_regression,
    }
    if extra:
        payload.update(extra)
    return payload


def render_decision(decision: Decision) -> Group:
    table = Table(box=None, pad_edge=False, show_header=False)
    table.add_column("key", style="cyan")
    table.add_column("value")
    table.add_row(
        "verdict",
        Text(_MESSAGE[decision.verdict], style=_STYLE[decision.verdict]),
    )
    table.add_row("difference", f"{decision.difference:+.4f}")
    table.add_row("p-value", f"{decision.p_value:.4f}")
    table.add_row("alpha", f"{decision.alpha:g}")
    return Group(table)
