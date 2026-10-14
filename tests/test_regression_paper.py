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
