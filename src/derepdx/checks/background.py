"""Table 3 row 6 -- measure the background before calling a region special.

Outgroup disagreement is common; a region that sits inside the genome-wide background
is not special. In the source study 12 of 18 blocks lay inside the background. A region
may only be labelled special when its statistic exceeds the background quantile.
"""

from __future__ import annotations

import pandas as pd

from ..result import CheckResult, Finding

NAME = "check-background"
TABLE3_ROW = 6


def _truthy(value) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def run(regions: pd.DataFrame, value_col: str = "value",
        background_col: str = "background_p95", flag_col: str = "claimed_special") -> CheckResult:
    """One row per region: ``value`` vs ``background_p95``, plus ``claimed_special``."""
    df = regions.copy()
    for col in (value_col, background_col):
        df[col] = pd.to_numeric(df[col], errors="raise")
    findings = []
    for _, row in df.iterrows():
        if not _truthy(row[flag_col]):
            continue
        if float(row[value_col]) <= float(row[background_col]):
            findings.append(Finding(
                "REGION_INSIDE_BACKGROUND",
                f"region {row.get('region', '?')!r} is claimed special but its value "
                f"{row[value_col]} is inside the background (p95 = {row[background_col]})",
                {"region": str(row.get("region", "")), "value": float(row[value_col]),
                 "background_p95": float(row[background_col])},
            ))
    n_claimed = int(df[flag_col].map(_truthy).sum())
    return CheckResult(NAME, not findings, findings,
                       {"regions": len(df), "claimed_special": n_claimed,
                        "inside_background": len(findings)})
