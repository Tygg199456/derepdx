"""The nine diagnostics, keyed by their Table 3 row number.

``REGISTRY`` is the single place that says "Table 3 row N is command X". The meta-test in
``tests/test_coverage_table3.py`` asserts that every row has an entry and both a
positive and a negative fixture, so the mapping cannot rot silently.
"""

from __future__ import annotations

from ..lint import denominators, matrix_id
from . import background, concordance, counts, length, polarity, profile, qc_covariate

REGISTRY = {
    1: length,
    2: denominators,
    3: concordance,
    4: profile,
    5: polarity,
    6: background,
    7: matrix_id,
    8: qc_covariate,
    9: counts,
}

# Rows 1-6, 8, 9 are data checks; 2 and 7 lint the reporting convention.
DATA_ROWS = [r for r in REGISTRY if r not in (2, 7)]

__all__ = ["REGISTRY", "DATA_ROWS", "background", "concordance", "counts", "length",
           "polarity", "profile", "qc_covariate", "denominators", "matrix_id"]
