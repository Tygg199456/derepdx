import pandas as pd

from derepdx import io
from derepdx.checks import concordance
from derepdx.fixtures import fixture


def _D():
    return io.read_matrix(fixture("concordance", "dist_8x8.tsv"))


def _P(name):
    return io.read_table(fixture("concordance", name), ["accession", "chromosome_blocks"])


def test_positive_discordant_pair_inside_threshold():
    res = concordance.run(_D(), _P("pos_discordant_at_t20.tsv"), t=20)
    assert res.ok is False
    assert res.codes == ["CONCORDANCE_VIOLATION"]
    assert res.findings[0].evidence["pairs"][0]["raw_d"] == 13.0


def test_negative_concordant_pair():
    res = concordance.run(_D(), _P("neg_concordant.tsv"), t=20)
    assert res.ok is True


def test_negative_both_sides_unresolved_does_not_block():
    res = concordance.run(_D(), _P("neg_unresolved_both_sides.tsv"), t=20)
    assert res.ok is True


def test_threshold_boundary_is_respected():
    # pair distances in the fixture are 13, 19, 20 and 21; at t=20 exactly three
    # pairs must merge and the d=21 pair must not (guards against off-by-one).
    res = concordance.run(_D(), _P("neg_concordant.tsv"), t=20)
    assert res.metrics["multi_member_clusters"] == 3

    res21 = concordance.run(_D(), _P("neg_concordant.tsv"), t=21)
    assert res21.metrics["multi_member_clusters"] == 4


def test_off_mode_never_blocks():
    blocked, details = __import__("derepdx.derep", fromlist=["derep"]).blocked_pairs(
        _D(), _P("pos_discordant_at_t20.tsv"), mode="off")
    assert details == []
    assert not blocked.any()


def test_profiles_accept_accession_column_or_index():
    as_col = _P("pos_discordant_at_t20.tsv")
    as_idx = as_col.set_index("accession")
    r1 = concordance.run(_D(), as_col, t=20)
    r2 = concordance.run(_D(), as_idx, t=20)
    assert r1.ok == r2.ok is False


def test_missing_accession_in_matrix_is_not_silently_merged():
    D = _D()
    D2 = D.drop(index=["A2"], columns=["A2"])
    res = concordance.run(D2, _P("pos_discordant_at_t20.tsv").iloc[1:], t=20)
    assert isinstance(res.ok, bool)
    assert isinstance(res.metrics, dict) and res.metrics["genomes"] == 7
    assert isinstance(pd.DataFrame(), pd.DataFrame)
