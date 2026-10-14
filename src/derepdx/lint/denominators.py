"""Table 3 row 2 -- confirm both denominators name the same set.

Before writing "A % versus B %", confirm the two percentages share a denominator set.
Mixing denominators produced apparent effects of up to 10 percentage points in the
source study. Each proportion declares its ``denominator_set``; if two proportions in
the same claim do not share it, the comparison is not licit.
"""

from __future__ import annotations

from ..result import CheckResult, Finding

NAME = "lint-denominators"
TABLE3_ROW = 2


def _claims(obj) -> list[dict]:
    if isinstance(obj, dict) and "claims" in obj:
        return obj["claims"]
    if isinstance(obj, dict):
        return [obj]
    return list(obj)


def run(claims) -> CheckResult:
    """Each claim: {"claim_id": str, "proportions": [{"name", "denominator_set"}]}."""
    findings = []
    n_claims = 0
    for claim in _claims(claims):
        proportions = claim.get("proportions", [])
        if len(proportions) < 2:
            continue
        n_claims += 1
        sets = {p["name"]: frozenset(p.get("denominator_set", [])) for p in proportions}
        distinct = {frozenset(s) for s in sets.values()}
        if len(distinct) > 1:
            findings.append(Finding(
                "DENOMINATOR_MISMATCH",
                f"claim {claim.get('claim_id', '?')!r} compares proportions with "
                f"{len(distinct)} different denominator sets",
                {"claim_id": claim.get("claim_id"),
                 "denominator_sets": {k: sorted(v) for k, v in sets.items()}},
            ))
    return CheckResult(NAME, not findings, findings,
                       {"claims_checked": n_claims, "mismatched": len(findings)})
