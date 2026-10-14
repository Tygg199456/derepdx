"""Verdict types shared by every check.

Each check returns a :class:`CheckResult`. ``ok`` is the verdict, ``findings`` carries
the evidence for a failure, ``metrics`` carries the numbers a human would want to see
even on success. The shape is identical across checks so that CI, the CLI and the
regression tests can all treat them uniformly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Finding:
    """One reason a check failed, with the evidence that produced it."""

    code: str
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "evidence": self.evidence}


@dataclass
class CheckResult:
    """The uniform output of every check."""

    check: str
    ok: bool
    findings: list[Finding] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    # Only the polarity check uses this: it is a three-valued classification, not a
    # boolean, so the class is reported separately from the pass/fail verdict.
    classification: str | None = None

    @property
    def codes(self) -> list[str]:
        return [f.code for f in self.findings]

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "check": self.check,
            "ok": self.ok,
            "findings": [f.to_dict() for f in self.findings],
            "metrics": self.metrics,
        }
        if self.classification is not None:
            d["classification"] = self.classification
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    @property
    def status(self) -> str:
        return "PASS" if self.ok else "FAIL"
