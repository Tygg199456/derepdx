"""Table 3 row 1 -- compare total assembly lengths before any alignment.

Two genomes deposited under the same strain name whose total lengths differ by more
than a threshold are not the same organism, independently of any SNP distance: the
reference strain CO92 (4,829,855 bp) and its attenuated derivative (4,722,852 bp)
differ by 107,003 bp, which is the 102.6 kb pgm deletion plus the 9,612 bp pPCP1
plasmid. No alignment is needed to see it.
"""

from __future__ import annotations

import pandas as pd

from ..result import CheckResult, Finding

NAME = "check-length"
TABLE3_ROW = 1
DEFAULT_MAX_DELTA_BP = 50_000


def run(metadata: pd.DataFrame, max_delta_bp: int = DEFAULT_MAX_DELTA_BP) -> CheckResult:
    """``metadata`` columns: accession, strain, total_bp."""
    df = metadata.copy()
    df["total_bp"] = pd.to_numeric(df["total_bp"], errors="raise")
    findings = []
    for strain, group in df.groupby("strain", sort=True):
        if len(group) < 2:
            continue
        lo = group.loc[group["total_bp"].idxmin()]
        hi = group.loc[group["total_bp"].idxmax()]
        delta = int(hi["total_bp"]) - int(lo["total_bp"])
        if delta > max_delta_bp:
            findings.append(Finding(
                "LENGTH_MISMATCH",
                f"strain {strain!r}: {delta} bp between {lo['accession']} and {hi['accession']}",
                {"strain": strain, "delta_bp": delta,
                 "short_accession": str(lo["accession"]), "short_bp": int(lo["total_bp"]),
                 "long_accession": str(hi["accession"]), "long_bp": int(hi["total_bp"]),
                 "max_delta_bp": int(max_delta_bp)},
            ))
    return CheckResult(NAME, not findings, findings,
                       {"strains": int(df["strain"].nunique()), "genomes": len(df),
                        "max_delta_bp": int(max_delta_bp)})
