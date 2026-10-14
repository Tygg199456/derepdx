"""Table 3 row 4 -- the profile must distinguish absent from not submitted.

A two-state present/absent profile cannot tell a plasmid that is genuinely gone from a
plasmid that a draft assembly never assembled. In the source study 42 of 70 inferred
absences were unresolved, not losses; scoring them as losses reverses the direction of
the association. This check fails when a profile table carries no unresolved state.
"""

from __future__ import annotations

import pandas as pd

from ..derep import CARRIED, LOST, UNRESOLVED, norm_state
from ..result import CheckResult, Finding

NAME = "check-profile"
TABLE3_ROW = 4
KNOWN = {CARRIED, LOST, UNRESOLVED}


def run(profile: pd.DataFrame) -> CheckResult:
    """``profile`` columns: accession, replicon, state."""
    states = {norm_state(s) for s in profile["state"].unique()}
    unknown = sorted(states - KNOWN)
    has_unresolved = UNRESOLVED in states
    findings = []
    if not has_unresolved:
        findings.append(Finding(
            "TWO_STATE_PROFILE",
            "profile has no unresolved state, so absence cannot be distinguished from "
            "non-submission",
            {"states": sorted(states), "unresolved_values": 0},
        ))
    if unknown:
        findings.append(Finding(
            "UNKNOWN_STATE",
            f"unrecognised state value(s): {unknown}",
            {"states": sorted(states), "unknown": unknown},
        ))
    return CheckResult(NAME, not findings, findings,
                       {"states": sorted(states), "n_rows": len(profile),
                        "has_unresolved": has_unresolved})
