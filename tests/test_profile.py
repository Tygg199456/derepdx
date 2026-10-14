from derepdx import io
from derepdx.checks import profile
from derepdx.fixtures import fixture


def _df(name):
    return io.read_table(fixture("profile", name), ["accession", "replicon", "state"])


def test_positive_two_state_profile_is_rejected():
    res = profile.run(_df("pos_two_state.tsv"))
    assert res.ok is False
    assert res.codes == ["TWO_STATE_PROFILE"]


def test_negative_three_state_profile_passes():
    res = profile.run(_df("neg_three_state.tsv"))
    assert res.ok is True
    assert res.metrics["has_unresolved"] is True
