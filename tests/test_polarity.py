from derepdx import io
from derepdx.checks import polarity
from derepdx.fixtures import fixture, ambiguous_cases


def _df(name):
    return io.read_table(fixture("polarity", name),
                         ["outgroup", "callable_fraction", "present"])


def test_classify_lineage_gain():
    assert polarity.classify([(0.95, False), (0.93, False)]) == "lineage_GAIN"


def test_classify_derived_loss_with_one_witness():
    assert polarity.classify([(0.95, True), (0.63, False)]) == "derived_LOSS"


def test_classify_ambiguous_when_no_witness():
    assert polarity.classify([(0.593, False), (0.555, False)]) == "AMBIGUOUS"


def test_run_reports_enum_not_boolean():
    res = polarity.run(_df("pos_lineage_gain.tsv"))
    assert res.classification == "lineage_GAIN"
    assert res.ok is False
    assert res.codes == ["POLARITY_REVERSED"]


def test_run_derived_loss_is_clean():
    res = polarity.run(_df("neg_derived_loss.tsv"))
    assert res.classification == "derived_LOSS"
    assert res.ok is True


def test_run_ambiguous_needs_a_human():
    res = next(fn() for fn in ambiguous_cases())
    assert res.classification == "AMBIGUOUS"
    assert res.ok is False
    assert res.codes == ["POLARITY_UNDETERMINED"]
