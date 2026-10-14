"""Dereplication by raw SNP distance, with the deletion-profile constraint.

Ported from the companion study's ``snp_dedup.py`` with every path and large-file
dependency stripped: the functions here take a distance matrix and a profile table and
return clusters. Two behaviours are preserved because they are the point of the study:

* **complete linkage**, not single linkage. Independent assemblies of one strain differ
  by a few SNPs, so the threshold is not zero; at a non-zero threshold single linkage
  chains (A~B~C can span 3x the threshold) and silently merges distinct organisms.
* **the deletion-profile constraint**. SNP distance is computed over jointly called
  sites, so a large deletion contributes exactly zero; a derivative and its parent look
  identical. Genomes with discordant profiles are therefore forced apart.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

SENTINEL = 10**6

# Canonical three-state vocabulary. A profile that only ever says present/absent cannot
# distinguish a real deletion from a sequence that was never submitted.
CARRIED, LOST, UNRESOLVED = "CARRIED", "LOST", "UNRESOLVED"
_STATE_ALIASES = {
    "carried": CARRIED, "present": CARRIED, "1": CARRIED, "true": CARRIED, "yes": CARRIED,
    "lost": LOST, "absent": LOST, "0": LOST, "false": LOST, "no": LOST,
    "unresolved": UNRESOLVED, "na": UNRESOLVED, "n/a": UNRESOLVED, ".": UNRESOLVED,
    "?": UNRESOLVED, "unknown": UNRESOLVED, "-1": UNRESOLVED,
}
PLASMID_STATES = ("pCD1_state", "pPCP1_state", "pMT1_state")


def norm_state(value: str) -> str:
    """Map a vocabulary entry onto CARRIED / LOST / UNRESOLVED, or return it unchanged."""
    return _STATE_ALIASES.get(str(value).strip().lower(), str(value).strip())


def _blocks(value: str) -> frozenset[str]:
    return frozenset(b for b in str(value).split(";") if b)


def profiles_discordant(pa: pd.Series, pb: pd.Series, mode: str = "conservative") -> bool:
    """Do two deletion profiles disagree strongly enough to forbid a merge?

    ``mode`` is one of ``off`` / ``full`` / ``threestate`` / ``conservative`` and mirrors
    the source study:

    * ``off``          -- never block.
    * ``full``         -- block on any signature difference.
    * ``threestate``   -- chromosome differences always block; a plasmid difference
                          blocks only when both genomes have that plasmid resolved.
    * ``conservative`` -- chromosome differences block, and so does any plasmid
                          difference unless both sides are unresolved (an unresolved
                          plasmid is not evidence of sameness).
    """
    if mode == "off":
        return False
    if mode == "full":
        return (_blocks(pa.get("chromosome_blocks", "")) != _blocks(pb.get("chromosome_blocks", ""))
                or any(pa.get(k) != pb.get(k) for k in PLASMID_STATES))
    chrom_diff = _blocks(pa.get("chromosome_blocks", "")) != _blocks(pb.get("chromosome_blocks", ""))
    if mode == "threestate":
        if chrom_diff:
            return True
        for k in PLASMID_STATES:
            a, b = norm_state(pa.get(k, UNRESOLVED)), norm_state(pb.get(k, UNRESOLVED))
            if a != UNRESOLVED and b != UNRESOLVED and a != b:
                return True
        return False
    if mode == "conservative":
        if chrom_diff:
            return True
        for k in PLASMID_STATES:
            a, b = norm_state(pa.get(k, UNRESOLVED)), norm_state(pb.get(k, UNRESOLVED))
            if a != b and a != UNRESOLVED and b != UNRESOLVED:
                return True
            if a != b and UNRESOLVED in (a, b):
                # One side is a called absence and the other is not submitted: not
                # evidence of sameness, so it blocks under the conservative rule.
                return True
        return False
    raise ValueError(f"unknown constraint mode: {mode!r}")


def blocked_pairs(D: pd.DataFrame, profiles: pd.DataFrame, mode: str = "conservative"):
    """Return (blocked_mask, details) for pairs whose profiles disagree."""
    if "accession" in profiles.columns:
        profiles = profiles.set_index("accession")
    labels = list(D.index)
    n = len(labels)
    blocked = np.zeros((n, n), dtype=bool)
    details = []
    for i in range(n):
        if labels[i] not in profiles.index:
            continue
        for j in range(i + 1, n):
            if labels[j] not in profiles.index:
                continue
            if profiles_discordant(profiles.loc[labels[i]], profiles.loc[labels[j]], mode):
                blocked[i, j] = blocked[j, i] = True
                details.append((labels[i], labels[j], float(D.iloc[i, j])))
    return blocked, details


def cluster(D: pd.DataFrame, t: float, blocked: np.ndarray | None = None,
            method: str = "complete") -> pd.Series:
    """Complete-linkage clustering at threshold ``t``; blocked pairs are pushed apart."""
    labels = list(D.index)
    M = D.to_numpy(dtype=float, copy=True)
    M = np.minimum(M, SENTINEL)
    np.fill_diagonal(M, 0.0)
    M = (M + M.T) / 2.0
    if blocked is not None:
        M = np.where(blocked, SENTINEL, M)
    Z = linkage(squareform(M, checks=False), method=method)
    lab = fcluster(Z, t=t, criterion="distance")
    return pd.Series(lab, index=labels, name="cluster")
