# Changelog

All notable changes to `derepdx` are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - unreleased

### Added
- The nine Table 3 diagnostics as CLI subcommands: `check-length`, `lint-denominators`,
  `check-concordance`, `check-profile`, `polarity`, `check-background`,
  `lint-matrix-id`, `check-qc-covariate`, `assert-count`.
- `derepdx demo`, which runs every command on the bundled positive/negative fixtures and
  exits non-zero if any fixture behaves unexpectedly.
- Complete-linkage dereplication with the deletion-profile constraint
  (`off` / `full` / `threestate` / `conservative`), ported from the companion study.
- A bundled fixture set (tables only, no genomes) generated deterministically by
  `scripts/make_fixtures.py`.
- A coverage meta-test asserting that every Table 3 row has a command and both a
  positive and a negative fixture.
- A paper-regression test suite (`-m paper`) that can reproduce the companion
  manuscript's frozen numbers when `PAPER1_RESULTS` is set.
