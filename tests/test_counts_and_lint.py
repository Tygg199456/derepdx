from derepdx import io
from derepdx.checks import counts
from derepdx.fixtures import fixture
from derepdx.lint import denominators, matrix_id


def test_counts_positive():
    res = counts.run(io.read_json(fixture("counts", "pos_28_of_206.json")))
    assert res.ok is False
    assert res.codes == ["COUNT_MISMATCH"]
    assert res.findings[0].evidence == {"stage": "closed_genomes", "expected": 206,
                                        "observed": 28}


def test_counts_negative():
    res = counts.run(io.read_json(fixture("counts", "neg_206_of_206.json")))
    assert res.ok is True


def test_denominators_positive():
    res = denominators.run(io.read_json(fixture("lint", "pos_denominators.json")))
    assert res.ok is False
    assert res.codes == ["DENOMINATOR_MISMATCH"]


def test_denominators_negative():
    res = denominators.run(io.read_json(fixture("lint", "neg_denominators.json")))
    assert res.ok is True


def test_matrix_id_positive():
    res = matrix_id.run(io.read_json(fixture("lint", "pos_matrix_id.json")))
    assert res.ok is False
    assert "CROSS_MATRIX_COMPARISON" in res.codes


def test_matrix_id_negative():
    res = matrix_id.run(io.read_json(fixture("lint", "neg_matrix_id.json")))
    assert res.ok is True
