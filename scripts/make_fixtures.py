#!/usr/bin/env python3
"""Generate the test fixtures for derepdx.

Fixtures are tables, never genomes, so they are small enough to commit. Everything here
is deterministic (fixed seed) and the generated files are committed alongside this
script: the fixtures are reproducible, not magic.

Run from the repository root:  python scripts/make_fixtures.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "derepdx" / "data" / "fixtures"
SEED = 20261014


def w(rel: str, text: str) -> None:
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def build() -> None:
    # --- row 1: length ----------------------------------------------------------
    w("length/pos_same_strain_107kb.tsv",
      "accession\tstrain\ttotal_bp\n"
      "GCA_000000001.1\tCO92\t4829855\n"
      "GCA_000000002.1\tCO92\t4722852\n")
    w("length/neg_same_strain_within_tol.tsv",
      "accession\tstrain\ttotal_bp\n"
      "GCA_000000001.1\tCO92\t4829855\n"
      "GCA_000000003.1\tCO92\t4829901\n")

    # --- row 4: profile ---------------------------------------------------------
    w("profile/pos_two_state.tsv",
      "accession\treplicon\tstate\n"
      "A\tpCD1\t1\nA\tpPCP1\t0\n"
      "B\tpCD1\t1\nB\tpPCP1\t1\n")
    w("profile/neg_three_state.tsv",
      "accession\treplicon\tstate\n"
      "A\tpCD1\tCARRIED\nA\tpPCP1\tLOST\n"
      "B\tpCD1\tCARRIED\nB\tpPCP1\tUNRESOLVED\n")

    # --- row 3: concordance -----------------------------------------------------
    accs = [f"A{i}" for i in range(1, 9)]
    M = np.full((8, 8), 100.0)
    np.fill_diagonal(M, 0.0)
    for a, b, d in [("A1", "A2", 13), ("A3", "A4", 19), ("A5", "A6", 20), ("A7", "A8", 21)]:
        i, j = accs.index(a), accs.index(b)
        M[i, j] = M[j, i] = float(d)
    lines = ["accession\t" + "\t".join(accs)]
    for i, a in enumerate(accs):
        lines.append(a + "\t" + "\t".join(str(int(x)) for x in M[i]))
    w("concordance/dist_8x8.tsv", "\n".join(lines) + "\n")

    hdr = "accession\tchromosome_blocks\tpCD1_state\tpPCP1_state\tpMT1_state\n"

    def profile_rows(blocks: dict, states: dict) -> str:
        rows = [hdr]
        for a in accs:
            b = blocks.get(a, "NC_003143:500-600")
            c = states.get(a, ("CARRIED", "CARRIED", "CARRIED"))
            rows.append(f"{a}\t{b}\t{c[0]}\t{c[1]}\t{c[2]}\n")
        return "".join(rows)

    base_blocks = {a: "NC_003143:500-600" for a in accs}
    # A1 carries the pgm block, A2 does not -> discordant at d=13.
    w("concordance/pos_discordant_at_t20.tsv",
      profile_rows({**base_blocks, "A1": "NC_003143:2135000-2240000", "A2": ""}, {}))
    w("concordance/neg_concordant.tsv",
      profile_rows({**base_blocks,
                    "A1": "NC_003143:2135000-2240000",
                    "A2": "NC_003143:2135000-2240000"}, {}))
    # Both sides unresolved on the differing plasmid: not evidence of difference.
    w("concordance/neg_unresolved_both_sides.tsv",
      profile_rows({**base_blocks,
                    "A1": "NC_003143:2135000-2240000",
                    "A2": "NC_003143:2135000-2240000"},
                   {"A1": ("UNRESOLVED", "CARRIED", "CARRIED"),
                    "A2": ("UNRESOLVED", "CARRIED", "CARRIED")}))

    # --- row 5: polarity --------------------------------------------------------
    w("polarity/pos_lineage_gain.tsv",
      "outgroup\tcallable_fraction\tpresent\nIP32953\t0.95\t0\nIP31758\t0.93\t0\n")
    w("polarity/neg_derived_loss.tsv",
      "outgroup\tcallable_fraction\tpresent\nIP32953\t0.95\t1\nIP31758\t0.63\t0\n")
    w("polarity/amb_undetermined.tsv",
      "outgroup\tcallable_fraction\tpresent\nIP32953\t0.593\t0\nIP31758\t0.555\t0\n")

    # --- row 6: background ------------------------------------------------------
    w("background/pos_inside_background.tsv",
      "region\tvalue\tbackground_p95\tclaimed_special\n"
      "blk_07\t0.04\t0.0902\t1\n")
    w("background/neg_outside_background.tsv",
      "region\tvalue\tbackground_p95\tclaimed_special\n"
      "blk_12\t0.42\t0.0902\t1\n")

    # --- row 8: qc covariate ----------------------------------------------------
    rng = np.random.default_rng(SEED)
    n = 30
    dist = np.linspace(0, 100, n)
    tracking = 99.0 - 0.05 * dist + rng.normal(0, 0.4, n)      # r ~ -0.99
    independent = 97.5 + rng.normal(0, 0.8, n)                 # r ~ 0
    rows = ["accession\tmetric\tdistance\n"]
    for i, (m, d) in enumerate(zip(tracking, dist, strict=True), 1):
        rows.append(f"G{i:03d}\t{m:.3f}\t{d:.1f}\n")
    w("qc/pos_metric_tracks_distance.tsv", "".join(rows))
    rows = ["accession\tmetric\tdistance\n"]
    for i, (m, d) in enumerate(zip(independent, dist, strict=True), 1):
        rows.append(f"G{i:03d}\t{m:.3f}\t{d:.1f}\n")
    w("qc/neg_metric_independent.tsv", "".join(rows))

    # --- row 9: counts ----------------------------------------------------------
    w("counts/pos_28_of_206.json", json.dumps(
        {"expected": {"closed_genomes": 206}, "observed": {"closed_genomes": 28}}, indent=2))
    w("counts/neg_206_of_206.json", json.dumps(
        {"expected": {"closed_genomes": 206}, "observed": {"closed_genomes": 206}}, indent=2))

    # --- rows 2 and 7: report linters ------------------------------------------
    w("lint/pos_denominators.json", json.dumps({"claim_id": "pgm_arm", "proportions": [
        {"name": "arm1_pct", "numerator_set": ["a", "b"], "denominator_set": ["a", "b", "c"]},
        {"name": "arm2_pct", "numerator_set": ["d"], "denominator_set": ["a", "b", "c", "d"]},
    ]}, indent=2))
    w("lint/neg_denominators.json", json.dumps({"claim_id": "pgm_arm", "proportions": [
        {"name": "arm1_pct", "numerator_set": ["a", "b"], "denominator_set": ["a", "b", "c"]},
        {"name": "arm2_pct", "numerator_set": ["c"], "denominator_set": ["a", "b", "c"]},
    ]}, indent=2))
    w("lint/pos_matrix_id.json", json.dumps({
        "matrices": [{"id": "tierA"}, {"id": "tierB"}],
        "comparisons": [{"name": "tierB_vs_tierA_floor",
                         "matrix_id": "tierB", "noise_floor_matrix_id": "tierA"}],
    }, indent=2))
    w("lint/neg_matrix_id.json", json.dumps({
        "matrices": [{"id": "tierA"}, {"id": "tierB"}],
        "comparisons": [{"name": "tierA_vs_tierA_floor",
                         "matrix_id": "tierA", "noise_floor_matrix_id": "tierA"}],
    }, indent=2))

    print(f"wrote fixtures under {OUT}")


if __name__ == "__main__":
    build()
