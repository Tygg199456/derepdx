from derepdx import io
from derepdx.checks import background
from derepdx.fixtures import fixture

COLS = ["region", "value", "background_p95", "claimed_special"]


def _df(name):
    return io.read_table(fixture("background", name), COLS)


def test_positive_region_inside_background():
    res = background.run(_df("pos_inside_background.tsv"))
    assert res.ok is False
    assert res.codes == ["REGION_INSIDE_BACKGROUND"]


def test_negative_region_outside_background():
    res = background.run(_df("neg_outside_background.tsv"))
    assert res.ok is True
