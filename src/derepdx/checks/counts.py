"""Table 3 row 9 -- assert output count equals input count.

Silent partial completion is the cheapest failure to miss: a pipeline stage that
produced 28 of 206 outputs and exited 0 looks exactly like success. This check compares
a declared expectation against the observed counts and fails on any mismatch.
"""

from __future__ import annotations

from ..result import CheckResult, Finding

NAME = "assert-count"
TABLE3_ROW = 9


def run(manifest: dict) -> CheckResult:
    """``manifest`` = {"expected": {stage: n}, "observed": {stage: n}}."""
    expected = manifest.get("expected", {})
    observed = manifest.get("observed", {})
    findings = []
    for stage, want in expected.items():
        got = observed.get(stage)
        if got is None:
            findings.append(Finding("COUNT_MISSING", f"stage {stage!r} has no observed count",
                                    {"stage": stage, "expected": want, "observed": None}))
        elif int(got) != int(want):
            findings.append(Finding("COUNT_MISMATCH",
                                    f"stage {stage!r}: observed {got} of {want}",
                                    {"stage": stage, "expected": int(want), "observed": int(got)}))
    return CheckResult(NAME, not findings, findings,
                       {"stages": len(expected), "mismatched": len(findings)})
