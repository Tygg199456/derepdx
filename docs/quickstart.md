# Quickstart

Everything here runs on fixtures bundled with `derepdx`. No download, no reference
genome, no cluster. Two minutes.

## 1. Install

```bash
pip install -e ".[dev]"
```

## 2. Run the whole matrix

```bash
derepdx demo
```

This executes all nine Table 3 commands on their positive and negative fixtures and
prints the verdict table. It exits non-zero if any positive fixture fails to be caught or
any negative fixture is wrongly flagged.

## 3. Run one diagnostic

```bash
derepdx check-length src/derepdx/data/fixtures/length/pos_same_strain_107kb.tsv
```

```
[FAIL] check-length
  - LENGTH_MISMATCH: strain 'CO92': 107003 bp between GCA_000000001.1 and GCA_000000002.1
  metrics: {"strains": 1, "genomes": 2, "max_delta_bp": 50000}
```

Exit code 1.

## 4. Run one diagnostic in CI

```bash
derepdx check-concordance matrix.tsv profiles.tsv --t 20 --json | jq .ok
```

`--json` prints the full :class:`CheckResult`; the exit code is still `0/1/2`, so a shell
`&&` chain works either way.

## 5. Point it at your own data

Inputs are TSVs with the columns listed in [`formats.md`](formats.md). The commands are
meant to sit between your pipeline stages:

```
metadata ──► check-length ──► align ──► distance matrix ──┐
                                                          ├─► check-concordance ──► dereplicate
deletion profiles ────────────────────────────────────────┘
```
