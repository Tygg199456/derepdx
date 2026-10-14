"""Table 3 row 5 -- determine polarity before scoring an absence as a loss.

An absence relative to the reference has no direction until one is established. Using
an outgroup that carries the region as a witness makes the focal absence a derived loss
(``derived_LOSS``); an outgroup that is callable and lacks the region means the region
was gained on the reference lineage (``lineage_GAIN``), which is the error the source
study found in 2 of 13 recurrent regions. With no callable witness the answer is
``AMBIGUOUS``. This is a three-valued classification, not a boolean: the pipeline
reports, the human decides.
"""

from __future__ import annotations

import pandas as pd

from ..result import CheckResult, Finding

NAME = "polarity"
TABLE3_ROW = 5
DEFAULT_MIN_CALLABLE = 0.8

_TRUE = {"1", "true", "yes", "carried", "present"}


def _as_bool(value) -> bool:
    return str(value).strip().lower() in _TRUE


def classify(outgroups, min_callable: float = DEFAULT_MIN_CALLABLE) -> str:
    """``outgroups`` is an iterable of ``(callable_fraction, carries_region)``."""
    witnesses = [(float(c), bool(p)) for c, p in outgroups if float(c) >= min_callable]
    if not witnesses:
        return "AMBIGUOUS"
    if any(present for _, present in witnesses):
        return "derived_LOSS"
    return "lineage_GAIN"


def run(region: pd.DataFrame, min_callable: float = DEFAULT_MIN_CALLABLE) -> CheckResult:
    """``region`` columns: outgroup, callable_fraction, present."""
    outgroups = [(_try_float(r["callable_fraction"]), _as_bool(r["present"]))
                 for _, r in region.iterrows()]
    cls = classify(outgroups, min_callable)
    findings = []
    if cls == "lineage_GAIN":
        findings.append(Finding(
            "POLARITY_REVERSED",
            "no callable outgroup carries the region: this is a reference-lineage gain, "
            "not a parallel loss",
            {"classification": cls,
             "witnesses": [{"callable_fraction": c, "present": p} for c, p in outgroups
                           if c >= min_callable]},
        ))
    elif cls == "AMBIGUOUS":
        findings.append(Finding(
            "POLARITY_UNDETERMINED",
            "no outgroup is callable enough to set polarity; a human must decide",
            {"classification": cls, "min_callable": min_callable,
             "outgroups": [{"callable_fraction": c, "present": p} for c, p in outgroups]},
        ))
    return CheckResult(NAME, cls == "derived_LOSS", findings,
                       {"min_callable": float(min_callable),
                        "n_outgroups": len(outgroups)}, classification=cls)


def _try_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
