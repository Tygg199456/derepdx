"""Table 3 row 3 -- check deletion-profile concordance before merging on a threshold.

The SNP distance is computed over jointly called sites, so a large deletion contributes
zero and a derivative merges with its parent. This check clusters at threshold ``t``
using distance alone and reports every cluster that would merge genomes whose deletion
profiles disagree. In the source study 24 of 36 multi-member clusters did.
"""

from __future__ import annotations

import pandas as pd

from .. import derep
from ..result import CheckResult, Finding

NAME = "check-concordance"
TABLE3_ROW = 3


def run(D: pd.DataFrame, profiles: pd.DataFrame, t: float = 20.0,
        mode: str = "conservative") -> CheckResult:
    """``D`` is a square distance matrix; ``profiles`` is indexed by accession."""
    if "accession" in profiles.columns:
        profiles = profiles.set_index("accession")
    labels = derep.cluster(D, t)
    blocked, details = derep.blocked_pairs(D, profiles, mode)
    violations = [(a, b, d) for (a, b, d) in details if d <= t]
    violated_members = {x for a, b, _ in violations for x in (a, b)}

    clusters: dict[int, list[str]] = {}
    for acc, lab in labels.items():
        clusters.setdefault(int(lab), []).append(acc)
    multi = {c: sorted(m) for c, m in clusters.items() if len(m) > 1}

    findings = []
    for cid, members in sorted(multi.items()):
        bad = [v for v in violations if v[0] in members and v[1] in members]
        if bad:
            findings.append(Finding(
                "CONCORDANCE_VIOLATION",
                f"cluster {cid} (size {len(members)}) merges {len(bad)} discordant pair(s)",
                {"cluster_id": cid, "members": members,
                 "pairs": [{"a": a, "b": b, "raw_d": d} for a, b, d in bad]},
            ))

    # Representatives retained once discordant genomes are forced apart.
    constrained = derep.cluster(D, t, blocked=blocked)
    retained = int(constrained.nunique())

    return CheckResult(NAME, not findings, findings, {
        "threshold": float(t),
        "constraint": mode,
        "clusters": len(clusters),
        "multi_member_clusters": len(multi),
        "discordant_pairs_within_t": len(violations),
        "discordant_genomes": len(violated_members),
        "retained_with_constraint": retained,
        "genomes": len(labels),
    })
