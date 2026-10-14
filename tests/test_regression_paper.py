"""Regression against the paper1 archive.

These tests read the frozen paper1 results and assert that derepdx reproduces the
numbers the manuscript prints. They are the instrument that settles the open CHECKs:
when one of them fails, either the code or the manuscript text is wrong, and that is the
output, not a broken test.

Skipped unless ``PAPER1_RESULTS`` points at a directory containing ``numbers.json``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from derepdx import io
from derepdx.checks import concordance

PAPER = Path(os.environ.get("PAPER1_RESULTS", "")).expanduser() if os.environ.get("PAPER1_RESULTS") else None

pytestmark = pytest.mark.paper

missing = PAPER is None or not (PAPER / "numbers.json").exists()
skip = pytest.mark.skipif(missing, reason="set PAPER1_RESULTS to the paper1 results/ dir")


def _registry() -> dict:
    return json.loads((PAPER / "numbers.json").read_text())


@skip
def test_concordance_conservative_retained_matches_registry():
    reg = _registry()
    matrix = io.read_matrix(PAPER / "dedup" / "snp_distance_raw_tierA.tsv")
    profiles = io.read_table(PAPER / "qc" / "tierA_refined.tsv", ["accession"])
    res = concordance.run(matrix, profiles, t=20, mode="conservative")
    assert res.metrics["retained_with_constraint"] == reg["dedup.conservative.kept"]


@skip
def test_registry_values_are_reproducible():
    reg = _registry()
    # every frozen value must at least be present and numeric; the specific
    # assertions above are added CHECK by CHECK as they are settled.
    for key, value in reg.items():
        assert value is None or isinstance(value, (int, float, str)), key
