"""Table readers with schema validation.

Everything is a TSV or a small JSON file. Readers validate the columns they need and
raise :class:`SchemaError` with a message that names the missing column and the file,
because a silently mis-parsed column is exactly the class of failure this package
exists to catch.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


class SchemaError(ValueError):
    """A table does not have the columns a check requires."""


def read_table(path: str | Path, required: list[str] | None = None) -> pd.DataFrame:
    """Read a whitespace-delimited table and validate its columns."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"input file not found: {p}")
    df = pd.read_csv(p, sep="\t", dtype=str, keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    if required:
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise SchemaError(
                f"{p.name}: missing column(s) {missing}; found {list(df.columns)}"
            )
    return df


def read_json(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"input file not found: {p}")
    return json.loads(p.read_text())


def read_matrix(path: str | Path) -> pd.DataFrame:
    """Read a square distance matrix: first column is the label, the rest numeric.

    Cell values may be the sentinel ``NA``/``nan`` for "not comparable"; those are
    preserved as NaN rather than silently turned into a number.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"input file not found: {p}")
    df = pd.read_csv(p, sep="\t", index_col=0)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df
