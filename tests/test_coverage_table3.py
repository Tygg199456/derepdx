"""Meta-test: mechanically prove that every Table 3 row is implemented and tested.

This is the file to point a reviewer at. It fails if a row is removed from the registry,
or if either a positive or a negative fixture disappears -- so the mapping in
``docs/table3_mapping.md`` cannot silently rot.
"""

from derepdx import fixtures
from derepdx.checks import REGISTRY


def _by_row():
    rows: dict[int, set[str]] = {}
    for row, kind, _fn in fixtures.cases():
        rows.setdefault(row, set()).add(kind)
    return rows


def test_all_nine_rows_are_registered():
    assert set(REGISTRY) == set(range(1, 10))


def test_every_row_has_a_command_and_both_sides():
    rows = _by_row()
    for row in range(1, 10):
        assert row in REGISTRY, f"Table 3 row {row} has no command"
        assert {"pos", "neg"} <= rows.get(row, set()), f"row {row} is missing a fixture"


def test_row_five_has_its_third_state():
    from derepdx.checks import polarity
    classes = set()
    for row, kind, fn in fixtures.cases():
        if row == 5:
            classes.add(fn().classification)
    for fn in fixtures.ambiguous_cases():
        classes.add(fn().classification)
    assert classes == {"derived_LOSS", "lineage_GAIN", "AMBIGUOUS"}


def test_negative_fixtures_all_pass():
    for row, kind, fn in fixtures.cases():
        if kind == "neg":
            res = fn()
            assert res.ok, f"row {row} negative fixture failed: {res.codes}"


def test_positive_fixtures_all_fail():
    for row, kind, fn in fixtures.cases():
        if kind == "pos":
            res = fn()
            assert not res.ok, f"row {row} positive fixture passed but must fail"


def test_every_command_is_exposed_on_the_cli():
    from derepdx.cli import build_parser
    parser = build_parser()
    sub = next(a for a in parser._actions if a.dest == "cmd")
    exposed = set(sub.choices)
    for row, mod in REGISTRY.items():
        assert mod.NAME in exposed, f"row {row} command {mod.NAME} not on the CLI"
    assert "demo" in exposed
