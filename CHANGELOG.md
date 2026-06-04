# Changelog

All notable changes to this project are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-06-05

### Added
- Docker image and a published container entry point.
- Continuous integration across Python 3.10, 3.11 and 3.12.
- Expanded documentation, including verdicts and limitations.

## [0.1.0] - 2026-06-02

### Added
- `proportions` command: two-proportion z-test on two aggregate accuracies and
  their sample sizes.
- `paired` command: McNemar's test on paired per-example correctness, exact for
  small samples and chi-squared for large ones.
- A four-way verdict (improvement, unchanged, noise, regression) that fails CI
  only on a significant regression, with a configurable `--alpha`.

[0.2.0]: https://github.com/jmweb-org/evalgate/releases/tag/v0.2.0
[0.1.0]: https://github.com/jmweb-org/evalgate/releases/tag/v0.1.0
