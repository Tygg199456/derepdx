"""Table 3 row 8 -- reference-based quality metrics are covariates, never filters.

A completeness-like metric measured against one reference tracks distance from that
reference. Used as a filter it removes the deep branches first: in the source study
42.6 % of closed genomes were dropped and the lost genomes were not a random subset.
This check measures the association between the metric and the distance and reports how
many genomes a filter at a given threshold would remove.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..result import CheckResult, Finding

NAME = "check-qc-covariate"
TABLE3_ROW = 8
DEFAULT_MAX_ABS_R = 0.5


def run(qc: pd.DataFrame, metric_col: str = "metric", distance_col: str = "distance",
        max_abs_r: float = DEFAULT_MAX_ABS_R, filter_below: float | None = None,
        deep_quantile: float = 0.75) -> CheckResult:
    """``qc`` columns: metric, distance (one row per genome)."""
    df = qc.copy()
    metric = pd.to_numeric(df[metric_col], errors="raise").to_numpy(dtype=float)
    distance = pd.to_numeric(df[distance_col], errors="raise").to_numpy(dtype=float)
    if len(df) < 3:
        raise ValueError("need at least 3 genomes to measure an association")
    pearson = float(np.corrcoef(metric, distance)[0, 1])
    rank_m = pd.Series(metric).rank().to_numpy()
    rank_d = pd.Series(distance).rank().to_numpy()
    spearman = float(np.corrcoef(rank_m, rank_d)[0, 1])

    metrics: dict = {"n": len(df), "pearson_r": round(pearson, 4),
                     "spearman_r": round(spearman, 4), "max_abs_r": float(max_abs_r)}
    findings = []
    if abs(pearson) >= max_abs_r:
        findings.append(Finding(
            "QC_TRACKS_DISTANCE",
            f"quality metric correlates with distance to the reference (r = {pearson:.3f}); "
            "using it as a filter removes deep branches first",
            {"pearson_r": round(pearson, 4), "spearman_r": round(spearman, 4),
             "max_abs_r": float(max_abs_r)},
        ))
    if filter_below is not None:
        cutoff = float(np.quantile(metric, 1 - deep_quantile))
        removed = metric < filter_below
        deep = distance >= np.quantile(distance, deep_quantile)
        n_removed = int(removed.sum())
        n_removed_deep = int((removed & deep).sum())
        frac_deep = (n_removed_deep / n_removed) if n_removed else 0.0
        metrics.update({"filter_below": float(filter_below), "removed": n_removed,
                        "removed_deep_branches": n_removed_deep,
                        "fraction_removed_that_are_deep": round(frac_deep, 4),
                        "background_cutoff": float(cutoff)})
        if n_removed and frac_deep > 0.5:
            findings.append(Finding(
                "FILTER_REMOVES_DEEP_BRANCHES",
                f"a filter at {filter_below} removes {n_removed} genomes, "
                f"{frac_deep:.0%} of them from the deepest quartile",
                {"filter_below": float(filter_below), "removed": n_removed,
                 "removed_deep_branches": n_removed_deep},
            ))
    return CheckResult(NAME, not findings, findings, metrics)
