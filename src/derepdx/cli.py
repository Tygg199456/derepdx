"""The single ``derepdx`` command.

One console script with subcommands, not nine scripts. Exit codes: 0 pass, 1 findings,
2 usage or input error -- so the checks can be wired straight into CI.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__, fixtures, io
from .checks import (
    REGISTRY,
    background,
    concordance,
    counts,
    length,
    polarity,
    profile,
    qc_covariate,
)
from .lint import denominators, matrix_id
from .result import CheckResult


def _emit(res: CheckResult, as_json: bool) -> int:
    if as_json:
        print(res.to_json())
    else:
        print(f"[{res.status}] {res.check}")
        for f in res.findings:
            print(f"  - {f.code}: {f.message}")
        if res.classification:
            print(f"  classification: {res.classification}")
        if res.metrics:
            print("  metrics: " + json.dumps(res.metrics))
    return 0 if res.ok else 1


def _add(parser, name, help_text):
    return parser.add_parser(name, help=help_text)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="derepdx", description=__doc__)
    p.add_argument("--version", action="version", version=f"derepdx {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = _add(sub, "check-length", "row 1: same strain name, different total length")
    sp.add_argument("metadata")
    sp.add_argument("--max-delta-bp", type=int, default=length.DEFAULT_MAX_DELTA_BP)
    sp.add_argument("--json", action="store_true")

    sp = _add(sub, "check-concordance", "row 3: profile concordance inside a merge threshold")
    sp.add_argument("matrix")
    sp.add_argument("profiles")
    sp.add_argument("--t", type=float, default=20.0)
    sp.add_argument("--constraint", default="conservative",
                    choices=["off", "full", "threestate", "conservative"])
    sp.add_argument("--json", action="store_true")

    sp = _add(sub, "check-profile", "row 4: profile must distinguish absent from not submitted")
    sp.add_argument("profiles")
    sp.add_argument("--json", action="store_true")

    sp = _add(sub, "polarity", "row 5: derived_LOSS / lineage_GAIN / AMBIGUOUS")
    sp.add_argument("region")
    sp.add_argument("--min-callable", type=float, default=polarity.DEFAULT_MIN_CALLABLE)
    sp.add_argument("--json", action="store_true")

    sp = _add(sub, "check-background", "row 6: a special region must beat the background")
    sp.add_argument("regions")
    sp.add_argument("--json", action="store_true")

    sp = _add(sub, "check-qc-covariate", "row 8: quality metric must not track distance")
    sp.add_argument("qc")
    sp.add_argument("--max-abs-r", type=float, default=qc_covariate.DEFAULT_MAX_ABS_R)
    sp.add_argument("--filter-below", type=float, default=None)
    sp.add_argument("--json", action="store_true")

    sp = _add(sub, "assert-count", "row 9: output count must equal input count")
    sp.add_argument("manifest")
    sp.add_argument("--json", action="store_true")

    sp = _add(sub, "lint-denominators", "row 2: proportions in a claim must share a denominator")
    sp.add_argument("claims")
    sp.add_argument("--json", action="store_true")

    sp = _add(sub, "lint-matrix-id", "row 7: a noise floor must come from the same matrix")
    sp.add_argument("matrices")
    sp.add_argument("--json", action="store_true")

    sp = _add(sub, "demo", "run every Table 3 command on the bundled fixtures")
    sp.add_argument("--json", action="store_true")
    return p


def dispatch(args) -> int:
    c = args.cmd
    if c == "check-length":
        return _emit(length.run(io.read_table(args.metadata, ["accession", "strain", "total_bp"]),
                                args.max_delta_bp), args.json)
    if c == "check-concordance":
        profiles = io.read_table(args.profiles, ["accession", "chromosome_blocks"])
        return _emit(concordance.run(io.read_matrix(args.matrix), profiles,
                                     t=args.t, mode=args.constraint), args.json)
    if c == "check-profile":
        return _emit(profile.run(io.read_table(args.profiles, ["accession", "replicon", "state"])),
                     args.json)
    if c == "polarity":
        return _emit(polarity.run(io.read_table(args.region,
                                                ["outgroup", "callable_fraction", "present"]),
                                  args.min_callable), args.json)
    if c == "check-background":
        return _emit(background.run(io.read_table(
            args.regions, ["region", "value", "background_p95", "claimed_special"])), args.json)
    if c == "check-qc-covariate":
        return _emit(qc_covariate.run(io.read_table(args.qc, ["accession", "metric", "distance"]),
                                      max_abs_r=args.max_abs_r,
                                      filter_below=args.filter_below), args.json)
    if c == "assert-count":
        return _emit(counts.run(io.read_json(args.manifest)), args.json)
    if c == "lint-denominators":
        return _emit(denominators.run(io.read_json(args.claims)), args.json)
    if c == "lint-matrix-id":
        return _emit(matrix_id.run(io.read_json(args.matrices)), args.json)
    if c == "demo":
        return _demo(args.json)
    raise SystemExit(2)


def _demo(as_json: bool) -> int:
    results = []
    for row, kind, fn in fixtures.cases():
        res = fn()
        results.append({"row": row, "check": res.check, "kind": kind, "ok": res.ok,
                        "classification": res.classification})
    for fn in fixtures.ambiguous_cases():
        res = fn()
        results.append({"row": 5, "check": res.check, "kind": "amb", "ok": res.ok,
                        "classification": res.classification})
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        print(f"{'row':>3}  {'check':<20} {'positive':<9} {'negative':<9}")
        by_row: dict[int, dict[str, str]] = {}
        for r in results:
            cell = r["classification"] or ("PASS" if r["ok"] else "FAIL")
            by_row.setdefault(r["row"], {})[r["kind"]] = cell
        for row in sorted(by_row):
            d = by_row[row]
            print(f"{row:>3}  {REGISTRY[row].NAME:<20}"
                  f" {d.get('pos', '-'):<9} {d.get('neg', '-'):<9}")
        print("\npositive fixtures must FAIL, negative fixtures must PASS, "
              "row 5 also prints the AMBIGUOUS class for its amb_ fixture.")
    bad = [r for r in results if (r["kind"] == "neg" and not r["ok"])
           or (r["kind"] == "pos" and r["ok"])]
    return 1 if bad else 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return dispatch(args)
    except (io.SchemaError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
