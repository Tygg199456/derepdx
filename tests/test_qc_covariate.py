from derepdx import io
from derepdx.checks import qc_covariate
from derepdx.fixtures import fixture


def _df(name):
    return io.read_table(fixture("qc", name), ["accession", "metric", "distance"])


def test_positive_metric_tracks_distance():
    res = qc_covariate.run(_df("pos_metric_tracks_distance.tsv"))
    assert res.ok is False
    assert res.codes == ["QC_TRACKS_DISTANCE"]
    assert res.metrics["pearson_r"] < -0.9


def test_negative_metric_is_independent():
    res = qc_covariate.run(_df("neg_metric_independent.tsv"))
    assert res.ok is True
    assert abs(res.metrics["pearson_r"]) < 0.5


def test_filter_report_names_the_deep_branches():
    res = qc_covariate.run(_df("pos_metric_tracks_distance.tsv"), filter_below=95.0)
    assert res.metrics["removed"] > 0
    assert res.metrics["fraction_removed_that_are_deep"] > 0.5
    assert "FILTER_REMOVES_DEEP_BRANCHES" in res.codes
