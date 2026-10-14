# Table 3 rows to commands

Table 3 of the companion manuscript is a list of nine diagnostics. Each row is one
command here. This file is the contract between the paper's claim — "we provide runnable
diagnostics" — and the code.

| Row | Command | Input | Verdict |
|---|---|---|---|
| 1 | `derepdx check-length <metadata.tsv>` | `accession, strain, total_bp` | `LENGTH_MISMATCH` when two genomes share a strain name and differ by more than `--max-delta-bp` (default 50000) |
| 2 | `derepdx lint-denominators <claims.json>` | one claim with two or more proportions, each declaring `denominator_set` | `DENOMINATOR_MISMATCH` when the sets differ |
| 3 | `derepdx check-concordance <matrix.tsv> <profiles.tsv> --t 20` | square distance matrix + per-accession profile | `CONCORDANCE_VIOLATION` for every cluster that merges discordant profiles inside the threshold |
| 4 | `derepdx check-profile <profiles.tsv>` | `accession, replicon, state` | `TWO_STATE_PROFILE` when no state is unresolved |
| 5 | `derepdx polarity <region.tsv>` | `outgroup, callable_fraction, present` | `derived_LOSS` / `lineage_GAIN` / `AMBIGUOUS` |
| 6 | `derepdx check-background <regions.tsv>` | `region, value, background_p95, claimed_special` | `REGION_INSIDE_BACKGROUND` when a claimed-special region does not beat the p95 |
| 7 | `derepdx lint-matrix-id <matrices.json>` | matrices and comparisons | `CROSS_MATRIX_COMPARISON` when a comparison borrows a noise floor from another matrix |
| 8 | `derepdx check-qc-covariate <qc.tsv>` | `accession, metric, distance` | `QC_TRACKS_DISTANCE` when `abs(pearson_r) >= --max-abs-r`; `--filter-below` adds `FILTER_REMOVES_DEEP_BRANCHES` |
| 9 | `derepdx assert-count <manifest.json>` | `{"expected": {stage: n}, "observed": {stage: n}}` | `COUNT_MISMATCH` on any stage |

## The two human decisions

- **Row 5.** When `polarity` returns `AMBIGUOUS`, no callable outgroup exists and a person
  has to decide. The command exits 1 and says so.
- **Row 8.** When `check-qc-covariate` reports `QC_TRACKS_DISTANCE`, whether to change the
  workflow is a person's call. The command reports the correlation and, with
  `--filter-below`, how many deep branches the filter would remove.

## Worked examples

```bash
# row 1: the reference strain and its attenuated derivative differ by 107,003 bp
derepdx check-length src/derepdx/data/fixtures/length/pos_same_strain_107kb.tsv

# row 3: a merge at t=20 would join a pgm+ parent with its pgm- derivative
derepdx check-concordance \
  src/derepdx/data/fixtures/concordance/dist_8x8.tsv \
  src/derepdx/data/fixtures/concordance/pos_discordant_at_t20.tsv --t 20

# row 5: an outgroup that carries the region makes the focal absence a derived loss
derepdx polarity src/derepdx/data/fixtures/polarity/neg_derived_loss.tsv
```
