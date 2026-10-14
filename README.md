# derepdx

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23354193.svg)](https://doi.org/10.5281/zenodo.23354193)

Diagnostics for SNP-distance dereplication that is blind to structural variation.

Dereplication by SNP distance assumes that "close in SNPs" means "same organism".
That assumption fails silently in three ways, each of which changes the composition of a
dereplicated set without raising an error:

- a SNP distance over jointly called sites **cannot see a deletion** — the deleted
  positions are uncalled in the genome that lacks them, so they enter neither the shared
  count nor the difference count and a derivative merges with its parent;
- **reference-based quality metrics are divergence filters** in disguise — measured
  against one reference they track distance from it, so using them as a filter removes
  the deep branches first;
- an **absence relative to the reference has no polarity** until an outgroup establishes
  one — a reference-lineage gain is otherwise scored as a parallel loss.

`derepdx` turns the nine diagnostics of the companion manuscript's Table 3 into commands
you can run before you trust a dereplicated set. It takes **tables in, verdict out**. It
never reads BAM/VCF/FASTA, so it installs with `pip`, runs on a laptop, and ships its own
test fixtures.

**The tools report; the human decides.** Two diagnostics (`polarity` and
`check-qc-covariate`) end in a judgement call — the output names the case and stops.

## Install

```bash
pip install derepdx          # from PyPI, once released
pip install -e ".[dev]"      # from a checkout, for development
```

Requires Python 3.10+.

## 60-second example

Every command runs on fixtures bundled with the package — no data needed:

```bash
derepdx demo
```

```
row  check                positive  negative
  1  check-length         FAIL      PASS
  2  lint-denominators    FAIL      PASS
  3  check-concordance    FAIL      PASS
  4  check-profile        FAIL      PASS
  5  polarity             lineage_GAIN derived_LOSS
  6  check-background     FAIL      PASS
  7  lint-matrix-id       FAIL      PASS
  8  check-qc-covariate   FAIL      PASS
  9  assert-count         FAIL      PASS
```

`positive` fixtures are inputs that **must** be flagged, `negative` fixtures are inputs
that **must not**. A single run reproduces the whole test matrix.

## The nine diagnostics

| Row | Command | Detects |
|---|---|---|
| 1 | `derepdx check-length` | a different total assembly length under the same strain name |
| 2 | `derepdx lint-denominators` | two percentages in one claim with different denominator sets |
| 3 | `derepdx check-concordance` | a merge threshold that would join discordant deletion profiles |
| 4 | `derepdx check-profile` | a present/absent profile that cannot tell "gone" from "not submitted" |
| 5 | `derepdx polarity` | a reference-relative absence scored as a loss when it is a lineage gain |
| 6 | `derepdx check-background` | a region called special that lies inside the background |
| 7 | `derepdx lint-matrix-id` | a noise floor taken from a different matrix than the distance |
| 8 | `derepdx check-qc-covariate` | a quality metric that tracks distance from the reference |
| 9 | `derepdx assert-count` | a stage that produced some of its outputs and exited 0 |

Details, input schemas and worked examples: [`docs/table3_mapping.md`](docs/table3_mapping.md).

## Exit codes

`0` pass · `1` findings · `2` usage or input error — so the checks drop straight into CI.

## Citation

If you use `derepdx`, please cite the archived release (concept DOI
[10.5281/zenodo.23354193](https://doi.org/10.5281/zenodo.23354193); version v0.1.0 is
`10.5281/zenodo.23354194`) and the companion manuscript; see [`CITATION.cff`](CITATION.cff).

## License

MIT (see [`LICENSE`](LICENSE)).
