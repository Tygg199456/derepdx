"""Table 3 row 7 -- name the matrix when comparing against a noise floor.

A distance threshold must be calibrated against the noise floor computed on the *same*
matrix. Comparing a threshold to a floor measured on a different matrix (a Tier B
distance against a Tier A floor, in the source study) is meaningless and silent. Every
matrix carries a ``matrix_id``; this lint fails any comparison whose floor is measured
on a different matrix.
"""

from __future__ import annotations

from ..result import CheckResult, Finding

NAME = "lint-matrix-id"
TABLE3_ROW = 7


def run(obj: dict) -> CheckResult:
    """``obj`` = {"matrices": [{"id": str}], "comparisons": [{"name", "matrix_id",
    "noise_floor_matrix_id"}]}."""
    matrices = {m["id"] for m in obj.get("matrices", [])}
    findings = []
    comparisons = obj.get("comparisons", [])
    for c in comparisons:
        mid = c.get("matrix_id")
        fid = c.get("noise_floor_matrix_id")
        if mid != fid:
            findings.append(Finding(
                "CROSS_MATRIX_COMPARISON",
                f"comparison {c.get('name', '?')!r} uses matrix {mid!r} but a noise floor "
                f"from {fid!r}",
                {"name": c.get("name"), "matrix_id": mid, "noise_floor_matrix_id": fid},
            ))
        for label, value in (("matrix_id", mid), ("noise_floor_matrix_id", fid)):
            if value not in matrices:
                findings.append(Finding(
                    "UNKNOWN_MATRIX_ID",
                    f"comparison {c.get('name', '?')!r} references {label} {value!r} "
                    "which is not declared in matrices",
                    {"name": c.get("name"), "field": label, "id": value},
                ))
    return CheckResult(NAME, not findings, findings,
                       {"comparisons": len(comparisons), "matrices": len(matrices)})
