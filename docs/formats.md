# Input formats

Every input is a whitespace-delimited (tab) table or a small JSON file. Column names are
exact; extra columns are ignored, missing required columns raise a `SchemaError` and exit
2. This is deliberate: a silently mis-parsed column is the class of failure these tools
exist to catch.

## `check-length` — metadata.tsv

| column | meaning |
|---|---|
| `accession` | genome identifier |
| `strain` | strain name; rows sharing it are compared |
| `total_bp` | total assembly length in base pairs |

## `check-profile` — profiles.tsv

| column | meaning |
|---|---|
| `accession` | genome identifier |
| `replicon` | replicon or region |
| `state` | one of `CARRIED`, `LOST`, `UNRESOLVED` (aliases: `present`/`absent`/`NA`/`?`/`1`/`0`) |

A table whose states are only ever present/absent cannot distinguish a deletion from a
sequence that was never submitted. `check-profile` fails it.

## `check-concordance` — matrix.tsv + profiles.tsv

`matrix.tsv` is a square distance matrix: the first column is the accession label, the
header row is the same labels, the cells are integers or `NA`.

`profiles.tsv` (indexed by `accession`):

| column | meaning |
|---|---|
| `accession` | genome identifier |
| `chromosome_blocks` | `;`-separated large-deletion block ids on the chromosome |
| `pCD1_state`, `pPCP1_state`, `pMT1_state` | `CARRIED` / `LOST` / `UNRESOLVED` |

Constraint modes (`--constraint`):

- `off` — never block a merge (the baseline that shows the size of the problem);
- `full` — block on any signature difference;
- `threestate` — chromosome differences always block; a plasmid difference blocks only
  when both genomes have that plasmid resolved;
- `conservative` (default) — chromosome differences block, and any plasmid difference
  blocks unless it is explained by non-submission on one side.

## `polarity` — region.tsv

| column | meaning |
|---|---|
| `outgroup` | outgroup identifier |
| `callable_fraction` | fraction of the region callable in this outgroup |
| `present` | whether the outgroup carries the region (`1`/`0`) |

An outgroup is a witness when `callable_fraction >= --min-callable` (default 0.8). Any
witness that carries the region makes the focal absence a `derived_LOSS`; witnesses that
are callable and lack it make it a `lineage_GAIN`; no witness gives `AMBIGUOUS`.

## `check-background` — regions.tsv

| column | meaning |
|---|---|
| `region` | region identifier |
| `value` | the statistic the region is called special on |
| `background_p95` | the genome-wide background 95th percentile of the same statistic |
| `claimed_special` | `1`/`0` |

## `check-qc-covariate` — qc.tsv

| column | meaning |
|---|---|
| `accession` | genome identifier |
| `metric` | the reference-based quality metric |
| `distance` | distance from the reference |

## `assert-count` — manifest.json

```json
{"expected": {"closed_genomes": 206}, "observed": {"closed_genomes": 28}}
```

## `lint-denominators` — claims.json

```json
{"claim_id": "pgm_arm", "proportions": [
  {"name": "arm1_pct", "numerator_set": ["a","b"], "denominator_set": ["a","b","c"]},
  {"name": "arm2_pct", "numerator_set": ["c"],    "denominator_set": ["a","b","c"]}
]}
```

## `lint-matrix-id` — matrices.json

```json
{"matrices": [{"id": "tierA"}, {"id": "tierB"}],
 "comparisons": [{"name": "x", "matrix_id": "tierB", "noise_floor_matrix_id": "tierA"}]}
```
