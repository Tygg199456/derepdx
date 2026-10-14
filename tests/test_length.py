from derepdx import io
from derepdx.checks import length
from derepdx.fixtures import fixture


def _df(name):
    return io.read_table(fixture("length", name), ["accession", "strain", "total_bp"])


def test_positive_same_strain_107kb():
    res = length.run(_df("pos_same_strain_107kb.tsv"))
    assert res.ok is False
    assert res.codes == ["LENGTH_MISMATCH"]
    assert res.findings[0].evidence["delta_bp"] == 107003


def test_negative_within_tolerance():
    res = length.run(_df("neg_same_strain_within_tol.tsv"))
    assert res.ok is True
    assert res.findings == []


def test_threshold_is_configurable():
    res = length.run(_df("pos_same_strain_107kb.tsv"), max_delta_bp=200_000)
    assert res.ok is True
