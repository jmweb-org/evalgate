# evalgate

[![CI](https://github.com/jmweb-org/evalgate/actions/workflows/ci.yml/badge.svg)](https://github.com/jmweb-org/evalgate/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/evalgate.svg)](https://pypi.org/project/evalgate/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Decide whether an eval delta is a real regression or just sampling noise, and
fail CI only when it is real.

A model eval that drops from 90.0% to 89.4% on a 1,000-example set looks like a
regression, but on that sample size it is noise. Gating CI on the raw number
makes the build flap; ignoring it lets real regressions through. `evalgate`
runs the appropriate significance test and fails only when the candidate is
significantly worse.

```console
$ evalgate proportions \
    --baseline-score 0.900 --baseline-n 1000 \
    --candidate-score 0.894 --candidate-n 1000
verdict     worse, but within noise
difference  -0.0060
p-value     0.6232
alpha       0.05
# exit code 0 -> build passes
```

## Install

```console
$ pip install evalgate
```

Pure standard library plus typer and rich. No heavy dependencies.

## Usage

### From two aggregate accuracies

```console
$ evalgate proportions \
    --baseline-score 0.90 --baseline-n 2000 \
    --candidate-score 0.87 --candidate-n 2000 \
    --alpha 0.05
```

Uses a two-proportion z-test on the accuracies and their sample sizes.

### From paired per-example results

When both models were evaluated on the same examples, a paired test is more
powerful. Give a CSV with per-example correctness (or predictions plus a truth
column):

```console
$ evalgate paired results.csv --baseline base_correct --candidate cand_correct
$ evalgate paired results.csv --baseline pred_a --candidate pred_b --truth label
```

Uses McNemar's test: an exact binomial test on the discordant pairs, or the
continuity-corrected chi-squared approximation for large samples.

### In CI

```yaml
- run: evalgate proportions --baseline-score 0.90 --baseline-n 2000
        --candidate-score "$SCORE" --candidate-n 2000
```

## Verdicts and exit codes

| Verdict | Meaning | Exit |
| --- | --- | --- |
| `improvement` | Candidate is better | 0 |
| `unchanged` | No measurable difference | 0 |
| `noise` | Worse, but not significant at `alpha` | 0 |
| `regression` | Significantly worse | 1 |

A bad invocation (scores out of range, missing column, unreadable file) exits 2.
## JSON output

When using the `--json` flag, `evalgate` returns a JSON object with the following fields:

| Field                    | Type      | Description                                                                                             |
| ------------------------ | --------- | ------------------------------------------------------------------------------------------------------- |
| `verdict`                | `string`  | One of `improvement`, `unchanged`, `noise`, or `regression`.                                            |
| `p_value`                | `float`   | The p-value from the statistical test.                                                                  |
| `difference`             | `float`   | Signed difference between candidate and baseline. A negative value means the candidate performed worse. |
| `alpha`                  | `float`   | Significance threshold used for the test.                                                               |
| `is_regression`          | `boolean` | `true` if the result is a statistically significant regression; otherwise `false`.                      |
| `test`                   | `string`  | Statistical test used (`two_proportion_z` or `mcnemar`).                                                |
| `baseline_only_correct`  | `integer` | *(Paired mode only)* Number of examples only the baseline answered correctly.                           |
| `candidate_only_correct` | `integer` | *(Paired mode only)* Number of examples only the candidate answered correctly.                          |


## What it does and does not do

It answers one question: is this difference larger than sampling variation?
It does not correct for multiple comparisons across many evals, and a
`noise` verdict means "not proven", not "proven equal". For small evals,
collect more examples rather than trusting a borderline p-value.

## License

MIT. See [LICENSE](LICENSE).
