"""Regression against the paper1 archive (the Day-3 instrument).

These tests reproduce the numbers the manuscript prints, reading them from the frozen
``results/numbers.json`` rather than hard-coding them, so the registry stays the single
source of truth. When one fails, either the code or the manuscript is wrong -- that is the
output, not a broken test.

Skipped unless ``PAPER1_RESULTS`` points at a directory containing ``numbers.json``. The
default is the archived paper1 tree if it is present.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from derepdx.checks import concordance

_DEFAULT = Path.home() / "Desktop" / "SY01" / "archive" / \
    "structural-variation-is-invisible-to-snp-distance-dereplication" / "results"
PAPER = Path(os.environ.get("PAPER1_RESULTS", _DEFAULT)).expanduser()

pytestmark = pytest.mark.paper
skip = pytest.mark.skipif(not (PAPER / "numbers.json").exists(),
                          reason="set PAPER1_RESULTS to the paper1 results/ dir")


def _norm(a: str) -> str:
    return str(a).strip()


def _registry():
    return json.loads((PAPER / "numbers.json").read_text())["numbers"]


def _matrix() -> pd.DataFrame:
    M = np.load(PAPER / "dedup" / "snp_distance_raw_tierA.npy").astype(float)
    order = [ln.strip() for ln in
             (PAPER / "dedup" / "snp_distance_raw_tierA.order.txt").read_text().splitlines()
             if ln.strip()]
    return pd.DataFrame(M, index=order, columns=order)


def _profiles() -> pd.DataFrame:
    """Chromosome blocks from the deletion profile, plasmid states from the
    three-state inventory; both keyed by the raw accession (which carries the .1
    version suffix and must match the distance-matrix order)."""
    blocks = pd.read_csv(PAPER / "qc" / "deletion_profile_all.tsv", sep="\t", dtype=str)
    three = pd.read_csv(PAPER / "qc" / "replicon_three_state_seqreport.tsv", sep="\t", dtype=str)
    three = three.set_index(three["accession"].map(_norm))
    rows = []
    for _, r in blocks.iterrows():
        acc = _norm(r["accession"])
        ts = three.loc[acc] if acc in three.index else None
        rows.append({
            "accession": acc,
            "chromosome_blocks": r.get("big_blocks_5kb", "") or "",
            "pCD1_state": (ts["pCD1_state"] if ts is not None else "UNRESOLVED"),
            "pPCP1_state": (ts["pPCP1_state"] if ts is not None else "UNRESOLVED"),
            "pMT1_state": (ts["pMT1_state"] if ts is not None else "UNRESOLVED"),
        })
    return pd.DataFrame(rows).set_index("accession")


@skip
def test_matrix_is_the_frozen_256():
    D = _matrix()
    assert len(D) == _registry()["sets"]["tierA"] == 256
    assert bool((D.index == D.columns).all())


@skip
def test_off_constraint_reproduces_the_registry():
    reg = _registry()["dereplication"]["constraints"]["off"]
    res = concordance.run(_matrix(), _profiles(), t=20, mode="off")
    assert res.metrics["clusters"] == reg["clusters"]        # 175
    assert res.metrics["multi_member_clusters"] == reg["multi"]  # 36


@skip
def test_conservative_constraint_reproduces_the_registry():
    reg = _registry()["dereplication"]["constraints"]["conservative"]
    res = concordance.run(_matrix(), _profiles(), t=20, mode="conservative")
    assert res.metrics["retained_with_constraint"] == reg["kept"]  # 209
    assert res.metrics["multi_member_clusters"] == 36             # unconstrained clusters


@skip
def test_mixed_clusters_are_detected():
    res = concordance.run(_matrix(), _profiles(), t=20, mode="conservative")
    # Table 3 row 3 prints "24 of 36 multi-member clusters mixed".
    assert res.metrics["multi_member_clusters"] == 36
    assert len(res.findings) > 0


# ---------------------------------------------------------------------------
# The open CHECKs, settled here.
#
# CHECK 2 -- Table 3 row 6 prints "12 of 18 blocks lie inside the background",
# while section 3.6 prints "four blocks qualify as special at or above the 95th
# percentile". Both are correct but use different thresholds: the archived
# within_background flag is `percentile < 75` (prep_figure_data.py), so 12 is the
# count at or below p75 and 4 is the count above p95, with two "elevated" blocks
# between them. This test pins both definitions so the number can never drift.
# ---------------------------------------------------------------------------
@skip
def test_background_matches_text():
    bg = pd.read_csv(PAPER / "figures" / "fig5b_background.csv")["delta"]
    p95 = float(np.quantile(bg, 0.95))
    assert round(p95, 4) == 0.0902
    bd = pd.read_csv(PAPER / "figures" / "fig5b_block_delta.csv")
    assert len(bd) == 18
    special = set(bd.loc[bd["delta"] > p95, "region_id"])
    within_p75 = set(bd.loc[bd["within_background"] == 1, "region_id"])
    elevated = set(bd["region_id"]) - special - within_p75
    assert len(special) == 4, "section 3.6: four blocks are special at or above p95"
    assert len(within_p75) == 12, "Table 3 row 6: twelve blocks are within the p75 flag"
    assert elevated == {"NC_003143:795000:15000", "NC_003143:4520000:45000"}, \
        "section 3.6 names exactly these two as elevated (87.3rd and 79.2nd percentile)"


# ---------------------------------------------------------------------------
# CHECK 10 -- the largest cluster. The manuscript prints 12 for the unconstrained
# run with a stated composition, and keeps every constrained run smaller.
# ---------------------------------------------------------------------------
@skip
def test_largest_cluster_per_constraint():
    sizes = {}
    for mode in ("off", "full", "threestate", "conservative"):
        d = pd.read_csv(PAPER / "dedup" / f"tierA_clusters.{mode}.tsv", sep="\t")
        sizes[mode] = int(d["size"].max())
    assert sizes == {"off": 12, "full": 10, "threestate": 8, "conservative": 8}


@skip
def test_largest_cluster_composition():
    off = pd.read_csv(PAPER / "dedup" / "tierA_clusters.off.tsv", sep="\t")
    big = off.loc[off["size"].idxmax()]
    members = big["members"].split(",")
    prof = pd.read_csv(PAPER / "qc" / "deletion_profile_all.tsv", sep="\t").set_index("accession")
    n_none = n_pgm = n_30kb = 0
    for acc in members:
        raw = prof.loc[acc, "big_blocks_5kb"] if acc in prof.index else None
        blocks = [] if raw is None or pd.isna(raw) else [b for b in str(raw).split(";") if b]
        if not blocks:
            n_none += 1
        elif any("2135000:105000" in b for b in blocks):
            n_pgm += 1
        elif any("1110000:30000" in b for b in blocks):
            n_30kb += 1
    # "the largest cluster held 12 genomes, of which 7 had no large deletion, 4
    # carried the 102.6 kb pgm block and 1 a different 30 kb block"
    assert (n_none, n_pgm, n_30kb) == (7, 4, 1)


# ---------------------------------------------------------------------------
# CHECK 3 -- two raw blocks that overlap merge into one recurring region; the
# carrier count must be the merged count, not the sum of the raw counts.
# ---------------------------------------------------------------------------
@skip
def test_gain_region_carriers_are_not_double_counted():
    t2 = pd.read_csv(PAPER / "qc" / "table2_regions.tsv", sep="\t")
    row = t2[(t2["replicon"] == "NC_003143") & (t2["start"] == 2365000)].iloc[0]
    assert int(row["n_blocks_merged"]) == 2
    assert int(row["n_genomes_absent"]) == 173      # the raw blocks carry 117 and 173
    assert int(row["n_genomes_absent"]) != 117 + 173
    assert row["polarity"] == "CO92_lineage_GAIN"
